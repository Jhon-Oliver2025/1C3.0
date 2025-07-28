from flask import Blueprint, request, jsonify, current_app
from typing import Any, Dict, Optional
import bcrypt
import secrets
from urllib.parse import urlencode
from core.email_service import send_email
import jwt
import uuid
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """Endpoint para autenticação de usuário"""
    try:
        data = request.get_json()
        if data is None:
            current_app.logger.warning("Corpo da requisição inválido ou vazio para /api/auth/login.")
            return jsonify({"message": "Corpo da requisição inválido ou vazio. Esperado JSON."}), 400

        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            current_app.logger.warning("Tentativa de login sem nome de usuário ou senha.")
            return jsonify({"message": "Nome de usuário e senha são obrigatórios."}), 400

        # Type hint para resolver o erro do Pyright
        bot_instance: Any = getattr(current_app, 'bot_instance', None)
        if not bot_instance:
            return jsonify({'error': 'Sistema não inicializado'}), 500
            
        # Remover linha incorreta que usa 'token' não definido
        # token_data = bot_instance.db.get_password_reset_token(token)  # LINHA REMOVIDA
        user = bot_instance.db.get_user_by_username(username)

        if not user:
            current_app.logger.debug(f"Tentativa de login falhou para username: {username} (usuário não encontrado)")
            return jsonify({"message": "Credenciais inválidas."}), 401

        if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            # Login bem-sucedido
            auth_token = secrets.token_hex(32)
            
            # Armazenar o token de autenticação no banco de dados
            bot_instance.db.store_auth_token(user['id'], auth_token, expires_in_minutes=60)
            
            current_app.logger.info(f"Login bem-sucedido para username: {username}")
            return jsonify({
                "message": "Login bem-sucedido.",
                "user": {
                    "id": user['id'],
                    "username": user['username'],
                    "is_admin": user['is_admin']
                },
                "token": auth_token
            }), 200
        else:
            current_app.logger.debug(f"Tentativa de login falhou para username: {username} (senha incorreta)")
            return jsonify({"message": "Credenciais inválidas."}), 401

    except Exception as e:
        current_app.logger.error(f"Erro inesperado durante o login: {e}", exc_info=True)
        return jsonify({"error": "Erro interno do servidor durante o login"}), 500

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Endpoint para solicitar a redefinição de senha"""
    try:
        data = request.get_json()
        if data is None:
            current_app.logger.warning("Corpo da requisição inválido ou vazio para /api/auth/forgot-password.")
            return jsonify({"message": "Corpo da requisição inválido ou vazio. Esperado JSON."}), 400
        
        username = data.get('username')
        email = data.get('email')

        if not username and not email:
            current_app.logger.warning("Tentativa de forgot-password sem nome de usuário ou e-mail.")
            return jsonify({"message": "Por favor, forneça um nome de usuário ou e-mail."}), 400

        # Type hint para resolver o erro do Pyright
        bot_instance: Any = getattr(current_app, 'bot_instance', None)
        if not bot_instance:
            return jsonify({'error': 'Sistema não inicializado'}), 500
            
        user = None
        if username:
            user = bot_instance.db.get_user_by_username(username)
        elif email:
            current_app.logger.warning("Redefinição de senha solicitada por e-mail, mas o backend requer nome de usuário.")
            return jsonify({"message": "A redefinição de senha requer o nome de usuário."}), 400

        if not user:
            current_app.logger.warning(f"Tentativa de redefinição de senha para usuário/email não encontrado: {username or email}")
            return jsonify({"message": "Se o usuário existir, um e-mail com instruções de redefinição de senha foi enviado."}), 200

        user_id = user['id']
        user_email = user['username']

        current_app.logger.debug(f"Tentando enviar e-mail de redefinição para: {user_email}")

        if not user_email:
            current_app.logger.error("Não foi possível encontrar um e-mail associado a este usuário.")
            return jsonify({"message": "Não foi possível encontrar um e-mail associado a este usuário."}), 400

        token = bot_instance.db.create_password_reset_token(user_id)
        if not token:
            current_app.logger.error("Erro ao gerar token de redefinição de senha.")
            return jsonify({"message": "Erro ao gerar token de redefinição de senha."}), 500

        # Construir o link de redefinição
        frontend_reset_url = "http://localhost:5173/reset-password"
        query_string = urlencode({'token': token, 'userId': user_id})
        reset_link = f"{frontend_reset_url}?{query_string}"

        subject = "Redefinição de Senha para sua Conta"
        text_content = f"""
        Olá {username},

        Você solicitou uma redefinição de senha para sua conta.
        Por favor, clique no link abaixo para redefinir sua senha:

        {reset_link}

        Este link expirará em 1 hora.

        Atenciosamente,
        Sua Equipe
        """
        
        html_content = f"""
        <p>Olá {username},</p>
        <p>Você solicitou uma redefinição de senha para sua conta.</p>
        <p>Por favor, clique no link abaixo para redefinir sua senha:</p>
        <p><a href="{reset_link}">Redefinir Senha</a></p>
        <p>Este link expirará em 1 hora.</p>
        <p>Atenciosamente,<br>Sua Equipe</p>
        """

        email_sent = send_email(user_email, subject, text_content, html_content)

        if email_sent:
            current_app.logger.info(f"E-mail de redefinição enviado para {user_email}.")
            return jsonify({"message": "Se o usuário existir, um e-mail com instruções foi enviado."}), 200
        else:
            current_app.logger.error(f"Falha ao enviar e-mail de redefinição para {user_email}.")
            return jsonify({"message": "Erro ao enviar e-mail de redefinição de senha."}), 500
            
    except Exception as e:
        current_app.logger.error(f"Erro inesperado ao solicitar redefinição de senha: {e}", exc_info=True)
        return jsonify({"error": "Erro interno do servidor"}), 500

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Endpoint para redefinir senha"""
    try:
        data = request.get_json()
        if data is None:
            current_app.logger.warning("Corpo da requisição inválido ou vazio para /api/auth/reset-password.")
            return jsonify({"message": "Corpo da requisição inválido ou vazio. Esperado JSON."}), 400
        
        token = data.get('token')
        user_id_from_frontend = data.get('userId')
        new_password = data.get('newPassword')

        if not token or not new_password:
            current_app.logger.warning("Token ou nova senha ausentes para redefinição.")
            return jsonify({"message": "Token e nova senha são obrigatórios."}), 400

        # Type hint para resolver o erro do Pyright
        bot_instance: Any = getattr(current_app, 'bot_instance', None)
        if not bot_instance:
            return jsonify({'error': 'Sistema não inicializado'}), 500
            
        token_data = bot_instance.db.get_password_reset_token(token)

        if not token_data:
            current_app.logger.warning(f"Token inválido ou expirado para redefinição: {token}")
            return jsonify({"message": "Token inválido ou expirado."}), 400

        # Validação extra do user_id
        if user_id_from_frontend:
            try:
                user_id_from_frontend_int = int(user_id_from_frontend)
                token_user_id_int = int(token_data['user_id'])

                if token_user_id_int != user_id_from_frontend_int:
                    current_app.logger.warning(f"User ID mismatch: token={token_user_id_int}, frontend={user_id_from_frontend_int}")
                    return jsonify({"message": "Token inválido."}), 400
            except ValueError:
                current_app.logger.warning("User ID inválido fornecido.")
                return jsonify({"message": "User ID inválido."}), 400

        # Atualizar a senha
        success = bot_instance.db.update_user_password(token_data['user_id'], new_password)
        if success:
            # Invalidar o token após uso
            bot_instance.db.invalidate_password_reset_token(token)
            current_app.logger.info(f"Senha redefinida com sucesso para user_id: {token_data['user_id']}")
            return jsonify({"message": "Senha redefinida com sucesso."}), 200
        else:
            current_app.logger.error(f"Falha ao atualizar senha para user_id: {token_data['user_id']}")
            return jsonify({"message": "Erro ao atualizar senha."}), 500

    except Exception as e:
        current_app.logger.error(f"Erro inesperado ao redefinir senha: {e}", exc_info=True)
        return jsonify({"error": "Erro interno do servidor"}), 500