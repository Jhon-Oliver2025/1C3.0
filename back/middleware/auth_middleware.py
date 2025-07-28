from flask import request, jsonify, g, current_app
from functools import wraps
from typing import cast
import jwt

def jwt_required(f):
    """Decorador para autenticação JWT"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Adicionar logs para debug
        print("Headers recebidos:", request.headers)
        print("Authorization header:", request.headers.get('Authorization'))
        
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            print("Auth header encontrado:", auth_header)
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                print("Token extraído:", token[:10], "...")
        else:
            print("Header 'Authorization' não encontrado")
        
        if not token:
            return jsonify({'message': 'Token de autenticação ausente.'}), 401

        try:
            # Decodificar o token JWT usando o segredo compartilhado
            secret_key: str = cast(str, current_app.config['JWT_SECRET'])
            decoded_token = jwt.decode(token, secret_key, algorithms=["HS256"])
            current_app.logger.debug(f"Token decodificado com sucesso: {decoded_token}")

            # Armazenar os dados do usuário do token no objeto 'g' do Flask
            g.user_data = decoded_token
            
            return f(*args, **kwargs)

        except jwt.ExpiredSignatureError:
            current_app.logger.warning("Token expirado.")
            return jsonify({'message': 'Token expirado.'}), 403
        except jwt.InvalidTokenError as e:
            current_app.logger.error(f"Token inválido: {e}")
            return jsonify({'message': 'Token inválido.'}), 403
        except Exception as e:
            current_app.logger.error(f"Erro na verificação do token: {str(e)}", exc_info=True)
            return jsonify({'message': 'Erro interno na verificação do token.'}), 500

    return decorated_function