from flask import Blueprint, request, jsonify, current_app
import bcrypt
import uuid
from datetime import datetime, timedelta

# Criar blueprint para autenticação
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """Endpoint para login de usuários - Otimizado para performance"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
            
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        # Validação rápida no backend
        if not username or not password:
            return jsonify({'error': 'Username e senha são obrigatórios'}), 400
            
        bot_instance = getattr(current_app, 'bot_instance', None)
        if not bot_instance:
            return jsonify({'error': 'Sistema não inicializado'}), 500
            
        # Otimização: Buscar usuário de forma mais eficiente
        # Primeiro por username (mais comum), depois por email
        user = bot_instance.db.get_user_by_username(username)
        if not user and '@' in username:
            user = bot_instance.db.get_user_by_email(username)
            
        if not user:
            # Delay mínimo para prevenir ataques de timing
            import time
            time.sleep(0.1)
            return jsonify({'error': 'Credenciais inválidas'}), 401
            
        # Verificação rápida de status
        user_status = user.get('status', 'inactive')
        if user_status != 'active':
            status_messages = {
                'pending': 'Conta pendente de aprovação pelo administrador',
                'suspended': 'Conta suspensa. Entre em contato com o administrador',
                'inactive': 'Conta inativa'
            }
            return jsonify({'error': status_messages.get(user_status, 'Conta inativa')}), 401
                
        # Verificação otimizada de senha
        stored_password = user.get('password', '')
        password_valid = False
        
        if stored_password.startswith('$2b$'):
            # Hash bcrypt - verificação segura
            password_valid = bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8'))
        else:
            # Texto plano (compatibilidade) - deve ser migrado para hash
            password_valid = (password == stored_password)
            
        if not password_valid:
            # Delay mínimo para prevenir ataques de timing
            import time
            time.sleep(0.1)
            return jsonify({'error': 'Credenciais inválidas'}), 401
                
        # Gerar token otimizado
        token = str(uuid.uuid4())
        expires_at = datetime.now() + timedelta(hours=24)
        
        # Salvar token no banco de forma assíncrona se possível
        bot_instance.db.save_auth_token(token, user['id'], expires_at)
        
        # Resposta otimizada com dados essenciais
        user_data = {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'is_admin': bool(user.get('is_admin', False))
        }
        
        # Log apenas em caso de sucesso (reduzir spam de logs)
        current_app.logger.info(f"Login bem-sucedido para usuário: {user['username']}")
        
        return jsonify({
            'success': True,
            'message': 'Login realizado com sucesso',
            'token': token,
            'user': user_data
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro no login: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@auth_bp.route('/register', methods=['POST'])
def register():
    """Endpoint para registro de usuários (ficam pendentes)"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
            
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not all([username, email, password]):
            return jsonify({'error': 'Username, email e senha são obrigatórios'}), 400
            
        bot_instance = getattr(current_app, 'bot_instance', None)
        if not bot_instance:
            return jsonify({'error': 'Sistema não inicializado'}), 500
            
        # Verificar se usuário já existe
        existing_user = bot_instance.db.get_user_by_username(username)
        if existing_user:
            return jsonify({'error': 'Nome de usuário já existe'}), 409
            
        existing_email = bot_instance.db.get_user_by_email(email)
        if existing_email:
            return jsonify({'error': 'Email já está cadastrado'}), 409
            
        # Criar usuário (status pendente)
        user_created = bot_instance.db.create_user(username, email, password)
        if user_created:
            return jsonify({
                'success': True,
                'message': 'Conta criada com sucesso! Aguarde a aprovação do administrador para acessar o sistema.'
            }), 201
        else:
            return jsonify({'error': 'Erro ao criar usuário'}), 500
            
    except Exception as e:
        current_app.logger.error(f"Erro no registro: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Endpoint para logout de usuários"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Token não fornecido'}), 401
            
        token = auth_header.split(' ')[1]
        
        bot_instance = getattr(current_app, 'bot_instance', None)
        if not bot_instance:
            return jsonify({'error': 'Sistema não inicializado'}), 500
            
        # Remover token do banco
        bot_instance.db.remove_auth_token(token)
        
        return jsonify({
            'success': True,
            'message': 'Logout realizado com sucesso'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro no logout: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Endpoint para solicitar redefinição de senha"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
            
        email = data.get('email')
        if not email:
            return jsonify({'error': 'Email é obrigatório'}), 400
            
        bot_instance = getattr(current_app, 'bot_instance', None)
        if not bot_instance:
            return jsonify({'error': 'Sistema não inicializado'}), 500
            
        # Verificar se usuário existe
        user = bot_instance.db.get_user_by_email(email)
        if not user:
            # Por segurança, não revelar se o email existe ou não
            return jsonify({
                'success': True,
                'message': 'Se o email estiver cadastrado, você receberá instruções para redefinir sua senha.'
            }), 200
            
        # Gerar token de redefinição
        reset_token = str(uuid.uuid4())
        expires_at = datetime.now() + timedelta(hours=1)
        
        # Salvar token de redefinição
        bot_instance.db.create_password_reset_token(user['id'], reset_token, expires_at)
        
        # Aqui você pode implementar o envio de email
        # Por enquanto, apenas log
        current_app.logger.info(f"Token de redefinição gerado para {email}: {reset_token}")
        
        return jsonify({
            'success': True,
            'message': 'Se o email estiver cadastrado, você receberá instruções para redefinir sua senha.'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao solicitar redefinição de senha: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Endpoint para redefinir senha com token"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
            
        token = data.get('token')
        new_password = data.get('password')
        
        if not all([token, new_password]):
            return jsonify({'error': 'Token e nova senha são obrigatórios'}), 400
            
        bot_instance = getattr(current_app, 'bot_instance', None)
        if not bot_instance:
            return jsonify({'error': 'Sistema não inicializado'}), 500
            
        # Verificar token de redefinição
        reset_data = bot_instance.db.get_password_reset_token(token)
        if not reset_data:
            return jsonify({'error': 'Token inválido ou expirado'}), 400
            
        # Atualizar senha do usuário
        success = bot_instance.db.update_user_password(reset_data['user_id'], new_password)
        if success:
            # Remover token usado
            bot_instance.db.remove_password_reset_token(token)
            
            return jsonify({
                'success': True,
                'message': 'Senha redefinida com sucesso'
            }), 200
        else:
            return jsonify({'error': 'Erro ao atualizar senha'}), 500
            
    except Exception as e:
        current_app.logger.error(f"Erro ao redefinir senha: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

# Endpoint verify-token removido (duplicado) - mantendo apenas a versão completa abaixo

@auth_bp.route('/check-admin', methods=['GET'])
def check_admin():
    """Verifica se o usuário atual é administrador"""
    try:
        # Obter token do header Authorization
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'is_admin': False, 'error': 'Token não fornecido'}), 401
            
        token = auth_header.split(' ')[1]
        
        bot_instance = getattr(current_app, 'bot_instance', None)
        if not bot_instance:
            return jsonify({'is_admin': False, 'error': 'Sistema não inicializado'}), 500
            
        # Verificar token
        user_id = bot_instance.db.verify_auth_token(token)
        if not user_id:
            return jsonify({'is_admin': False, 'error': 'Token inválido'}), 401
            
        # Buscar usuário
        user = bot_instance.db.get_user_by_id(user_id)
        if not user:
            return jsonify({'is_admin': False, 'error': 'Usuário não encontrado'}), 404
            
        # Verificar se é admin (pode ser por email específico ou campo is_admin)
        is_admin = user.get('is_admin', False) or user.get('email') == 'jonatasprojetos2013@gmail.com'
        
        return jsonify({
            'is_admin': is_admin,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email']
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao verificar admin: {str(e)}")
        return jsonify({'is_admin': False, 'error': 'Erro interno do servidor'}), 500

@auth_bp.route('/verify-token', methods=['POST'])
def verify_token():
    """Endpoint para verificar se um token ainda é válido"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'valid': False, 'error': 'Dados não fornecidos'}), 400
            
        token = data.get('token')
        if not token:
            # Tentar pegar do header Authorization
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
            else:
                return jsonify({'valid': False, 'error': 'Token não fornecido'}), 400
        
        bot_instance = getattr(current_app, 'bot_instance', None)
        if not bot_instance:
            return jsonify({'valid': False, 'error': 'Sistema não inicializado'}), 500
            
        # Verificar se token existe
        token_data = bot_instance.db.get_auth_token(token)
        if not token_data:
            return jsonify({'valid': False, 'error': 'Token inválido'}), 200
            
        # Verificar se token expirou
        expires_at = datetime.fromisoformat(token_data['expires_at'])
        now = datetime.now()
        
        if now > expires_at:
            bot_instance.db.remove_auth_token(token)
            return jsonify({'valid': False, 'error': 'Token expirado'}), 200
            
        # Buscar dados do usuário
        user = bot_instance.db.get_user_by_id(token_data['user_id'])
        if not user:
            return jsonify({'valid': False, 'error': 'Usuário não encontrado'}), 200
            
        # Calcular tempo até expiração em segundos
        expires_in = int((expires_at - now).total_seconds())
        
        return jsonify({
            'valid': True,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'is_admin': user.get('is_admin', False)
            },
            'expires_in': expires_in
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao verificar token: {str(e)}")
        return jsonify({'valid': False, 'error': 'Erro interno do servidor'}), 500