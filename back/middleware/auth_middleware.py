from flask import request, jsonify, g, current_app
from functools import wraps
from typing import Any
from flask import request, jsonify, current_app, g

def jwt_required(f):
    """Decorador para autenticação usando tokens do banco de dados"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Permitir que requisições OPTIONS passem sem autenticação
        if request.method == 'OPTIONS':
            return f(*args, **kwargs)

        # Adicionar logs para debug (apenas em desenvolvimento)
        auth_header = request.headers.get('Authorization')
        
        token = None
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            
            # Verificar se o token não é 'null', vazio ou inválido
            if not token or token.lower() == 'null' or token.strip() == '':
                current_app.logger.debug(f"Token inválido recebido: {token}")
                return jsonify({'message': 'Token de autenticação inválido.'}), 401
        
        if not token:
            return jsonify({'message': 'Token de autenticação ausente.'}), 401

        try:
            # Usar o sistema de tokens do banco de dados
            bot_instance: Any = getattr(current_app, 'bot_instance', None)
            if not bot_instance:
                return jsonify({'message': 'Sistema não inicializado.'}), 500
            
            # Verificar token no banco de dados
            user_data = bot_instance.db.get_user_by_token(token)
            
            if not user_data:
                current_app.logger.warning("Token inválido ou expirado.")
                return jsonify({'message': 'Token inválido ou expirado.'}), 403
            
            current_app.logger.debug(f"Token validado com sucesso para usuário: {user_data.get('username')}")
            
            # Armazenar os dados do usuário no objeto 'g' do Flask
            g.user_data = user_data
            
            return f(*args, **kwargs)

        except Exception as e:
            current_app.logger.error(f"Erro na verificação do token: {str(e)}", exc_info=True)
            return jsonify({'message': 'Erro interno na verificação do token.'}), 500

    return decorated_function


def get_current_user():
    """Função para obter o usuário atual autenticado"""
    if hasattr(g, 'user_data') and g.user_data:
        return g.user_data
    return None