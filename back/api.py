from flask import Flask, request, jsonify, send_from_directory, session, g
from flask_cors import CORS
from datetime import datetime, timedelta
import os
import json
import bcrypt
from urllib.parse import urlencode
import traceback
import time
import secrets
from werkzeug.security import generate_password_hash, check_password_hash
import numpy as np
import pandas as pd
from typing import cast, Any
import jwt
import csv # Adicione esta importação
import requests # NEW: Import the requests library

# Importações dos serviços
from core.database import Database
from core.email_service import send_email

def create_app():
    app_server = Flask(__name__)
    CORS(app_server)
    return app_server

app_server = create_app()

# Define JWT_SECRET para o backend Python
PYTHON_JWT_SECRET: str | None = os.getenv('JWT_SECRET') # Explicitly declare as str | None

if not PYTHON_JWT_SECRET:
    raise ValueError("❌ JWT_SECRET não está definido! Defina esta variável de ambiente com a mesma chave do Node.js")

# Assert that PYTHON_JWT_SECRET is not None after the check
# Pyright will now infer PYTHON_JWT_SECRET as 'str' from this point onwards.
assert PYTHON_JWT_SECRET is not None

print(f"✅ JWT_SECRET configurado: {PYTHON_JWT_SECRET[:5]}...") # Mostra apenas os primeiros 5 caracteres por segurança

# NEW: Define EVO_AI_AGENT_BASE_URL and EVO_AI_API_KEY in the global scope
# URL do agente Zion da Evo AI
# MODIFIED: Read EVO_AI_AGENT_BASE_URL from environment variables
EVO_AI_AGENT_BASE_URL = os.getenv('EVO_AI_AGENT_BASE_URL') 

# Se a Evo AI for open source e você estiver rodando uma instância local
# ou se não houver necessidade de API Key para interações básicas,
# você pode deixar EVO_AI_API_KEY como None ou uma string vazia.
# Caso contrário, defina-a aqui ou como uma variável de ambiente.
EVO_AI_API_KEY = os.getenv('EVO_AI_API_KEY', None) # Exemplo: 'sua_chave_secreta_aqui'

# NEW: Add a check for EVO_AI_AGENT_BASE_URL
if not EVO_AI_AGENT_BASE_URL:
    raise ValueError("❌ EVO_AI_AGENT_BASE_URL não está definido! Defina esta variável de ambiente.")


# Decorador para autenticação JWT no backend Python
def jwt_required(f):
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
        
        # Get token from Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                app_server.logger.debug(f"Token received: {token[:10]}...")
        
        if not token:
            return jsonify({'message': 'Token de autenticação ausente.'}), 401

        try:
            # Decodificar o token JWT usando o segredo compartilhado
            # NEW: Explicitly cast PYTHON_JWT_SECRET to str for type checker
            secret_key: str = cast(str, PYTHON_JWT_SECRET)
            decoded_token = jwt.decode(token, secret_key, algorithms=["HS256"])
            app_server.logger.debug(f"Token decodificado com sucesso: {decoded_token}")

            # Armazenar os dados do usuário do token no objeto 'g' do Flask
            g.user_data = decoded_token
            
            return f(*args, **kwargs)

        except jwt.ExpiredSignatureError:
            app_server.logger.warning("Token expirado.")
            return jsonify({'message': 'Token expirado.'}), 403
        except jwt.InvalidTokenError as e:
            app_server.logger.error(f"Token inválido: {e}")
            return jsonify({'message': 'Token inválido.'}), 403
        except Exception as e:
            app_server.logger.error(f"Erro na verificação do token: {str(e)}", exc_info=True)
            return jsonify({'message': 'Erro interno na verificação do token.'}), 500

    return decorated_function

# Esta função será chamada de app.py para registrar as rotas
def register_api_routes(app_server, bot_instance):
    print("DEBUG: register_api_routes foi chamada!")
    
    # Definir o caminho do arquivo de sinais
    signals_file = os.path.join(os.path.dirname(__file__), 'sinais_lista.csv')

    @app_server.route('/')
    def index():
        """
        Rota raiz para verificar se a API está online.
        """
        return jsonify({"message": "API do backend Flask está online!"}), 200

    @app_server.route('/status', methods=['GET', 'HEAD']) # Alterado de '/health' para '/status'
    def health_check():
        """
        Endpoint para verificar o status do backend.
        Não requer autenticação.
        """
        app_server.logger.debug("Rota /status foi acessada!") # Atualizado o log
        return jsonify({"status": "ok"}), 200

    def get_signals_from_csv():
        signals_list = []
        try:
            with open(signals_file, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                row_count = 0
                
                for row in csv_reader:
                    row_count += 1
                    
                    # Initialize variables with default values
                    entry_price = 0.0
                    target_price = 0.0
                    change_percentage = 0.0  # Initialize here
                    change_percentage_str = "0.00%"
                    quality_score = 0.0
                    
                    try:
                        entry_price = float(row.get('entry_price', 0))
                        target_price = float(row.get('target_price', 0))
                        
                        if entry_price != 0:
                            change_percentage = ((target_price / entry_price) - 1) * 100
                            change_percentage_str = f"{change_percentage:.2f}%"
                    except (ValueError, ZeroDivisionError):
                        pass
                    
                    try:
                        quality_score = float(row.get('quality_score', 0))
                    except ValueError:
                        quality_score = 0.0
                    
                    is_premium = quality_score >= 80
                    signal_type = "LONG" if row.get('type') == 'COMPRA' else "SHORT"
                    
                    # Create signal object with all required fields
                    signal_obj = {
                        "symbol": row.get('symbol', ''),
                        "type": signal_type,
                        "entry_price": entry_price,
                        "entry_time": row.get('entry_time', ''),
                        "target_price": target_price,
                        "projection_percentage": round(change_percentage, 2),  # Now always defined
                        "status": row.get('status', ''),
                        "quality_score": quality_score,
                        "signal_class": "Sinais Premium" if is_premium else "Sinais Básicos"
                    }
                    
                    # Ensure no undefined values
                    for key, value in signal_obj.items():
                        if value is None:
                            signal_obj[key] = ''
                    
                    signals_list.append(signal_obj)
        
            # These operations should be at the same level as csv_reader
            signals_list.sort(key=lambda x: x['entry_time'], reverse=True) # Ordenar por entry_time
            app_server.logger.debug(f"Processed {row_count} signals successfully")
            app_server.logger.debug(f"First signal after sorting: {signals_list[0] if signals_list else 'No signals'}")
            
            return signals_list  # Fixed: Now properly indented after the with block

        except Exception as e:
            app_server.logger.error(f"Error reading CSV: {str(e)}", exc_info=True)
            return []

    @app_server.route('/signals', methods=['GET'])
    @jwt_required # Aplica o decorador JWT para proteger esta rota
    def get_signals():
        """
        Endpoint para obter a lista de sinais do arquivo CSV.
        Requer autenticação JWT.
        """
        app_server.logger.debug("Rota /signals foi acessada!")
        try:
            # Acessa os dados do usuário do objeto g, anexados pelo decorador jwt_required
            user_data = g.user_data
            
            # Verificar se o usuário é admin para ver sinais premium
            # O payload do JWT do Node.js contém 'id', 'email', 'isAdmin'
            is_admin = user_data.get('isAdmin', False)

            # Obter sinais do CSV
            all_signals = get_signals_from_csv()

            # --- Início da Edição ---
            # Filtrar sinais premium se o usuário não for admin
            # if not is_admin:
            #     # Retorna apenas sinais que não são premium
            #     signals_to_return = [s for s in all_signals if not s.get('isPremium', False)]
            # else:
            #     # Retorna todos os sinais se o usuário for admin
            #     signals_to_return = all_signals
            signals_to_return = all_signals # Temporariamente retorna todos os sinais para depuração
            # --- Fim da Edição ---

            app_server.logger.debug(f"DEBUG: Sinais antes de jsonify: {signals_to_return}")
            # Retornar os sinais como JSON
            return jsonify(signals_to_return), 200

        except Exception as e:
            app_server.logger.error(f"Erro ao obter sinais: {e}", exc_info=True)
            return jsonify({"error": "Erro interno do servidor ao obter sinais"}), 500

    @app_server.route('/api/login', methods=['POST'])
    def login():
        """
        Endpoint para autenticação de usuário.
        Verifica as credenciais e retorna informações do usuário se o login for bem-sucedido.
        """
        try:
            data = request.get_json()
            if data is None:
                app_server.logger.warning("Corpo da requisição inválido ou vazio para /api/login.")
                return jsonify({"message": "Corpo da requisição inválido ou vazio. Esperado JSON."}), 400

            username = data.get('username')
            password = data.get('password')

            if not username or not password:
                app_server.logger.warning("Tentativa de login sem nome de usuário ou senha.")
                return jsonify({"message": "Nome de usuário e senha são obrigatórios."}), 400

            user = bot_instance.db.get_user_by_username(username)

            if not user:
                app_server.logger.debug(f"Tentativa de login falhou para username: {username} (usuário não encontrado)")
                return jsonify({"message": "Credenciais inválidas."}), 401 # Unauthorized

            # user['password'] contém a senha hasheada do CSV
            # password.encode('utf-8') é a senha fornecida pelo usuário, convertida para bytes
            # bcrypt.checkpw espera bytes para ambos os argumentos
            if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
                # Login bem-sucedido
                auth_token = secrets.token_hex(32) # Gera um token hexadecimal de 64 caracteres
                
                # Armazenar o token de autenticação no banco de dados com uma expiração (ex: 60 minutos)
                bot_instance.db.store_auth_token(user['id'], auth_token, expires_in_minutes=60)
                
                app_server.logger.info(f"Login bem-sucedido para username: {username}")
                return jsonify({
                    "message": "Login bem-sucedido.",
                    "user": {
                        "id": user['id'],
                        "username": user['username'],
                        "is_admin": user['is_admin']
                    },
                    "token": auth_token # Incluir o token na resposta
                }), 200
            else:
                app_server.logger.debug(f"Tentativa de login falhou para username: {username} (senha incorreta)")
                return jsonify({"message": "Credenciais inválidas."}), 401 # Unauthorized

        except Exception as e:
            app_server.logger.error(f"Erro inesperado durante o login: {e}", exc_info=True)
            return jsonify({"error": "Erro interno do servidor durante o login"}), 500

    @app_server.route('/api/forgot-password', methods=['POST'])
    def forgot_password():
        """
        Endpoint para solicitar a redefinição de senha.
        Envia um e-mail com um link de redefinição contendo um token.
        """
        try:
            data = request.get_json()
            if data is None:
                app_server.logger.warning("Corpo da requisição inválido ou vazio para /api/forgot-password.")
                return jsonify({"message": "Corpo da requisição inválido ou vazio. Esperado JSON."}), 400
            
            username = data.get('username')
            email = data.get('email')

            if not username and not email:
                app_server.logger.warning("Tentativa de forgot-password sem nome de usuário ou e-mail.")
                return jsonify({"message": "Por favor, forneça um nome de usuário ou e-mail."}), 400

            user = None
            if username:
                user = bot_instance.db.get_user_by_username(username)
            elif email:
                app_server.logger.warning("Redefinição de senha solicitada por e-mail, mas o backend requer nome de usuário.")
                return jsonify({"message": "A redefinição de senha requer o nome de usuário."}), 400

            if not user:
                # Para segurança, não informamos se o usuário não existe.
                # Apenas dizemos que o e-mail foi enviado (ou que o processo foi iniciado).
                app_server.logger.warning(f"Tentativa de redefinição de senha para usuário/email não encontrado: {username or email}")
                return jsonify({"message": "Se o usuário existir, um e-mail com instruções de redefinição de senha foi enviado."}), 200

            # Afirma para o Pyright que 'user' não é None neste ponto
            assert user is not None

            user_id = user['id']
            user_email = user['username'] # Assumindo que o username é o email para envio, ou adicione um campo 'email' no users.csv

            app_server.logger.debug(f"Tentando enviar e-mail de redefinição para: {user_email}")

            if not user_email:
                app_server.logger.error("Não foi possível encontrar um e-mail associado a este usuário para enviar o link de redefinição.")
                return jsonify({"message": "Não foi possível encontrar um e-mail associado a este usuário para enviar o link de redefinição."}), 400

            token = bot_instance.db.create_password_reset_token(user_id)
            if not token:
                app_server.logger.error("Erro ao gerar token de redefinição de senha.")
                return jsonify({"message": "Erro ao gerar token de redefinição de senha."}), 500

            # Construa o link de redefinição.
            # A URL base deve ser a URL do seu frontend onde o formulário de redefinição de senha está localizado.
            # Exemplo: http://localhost:3000/reset-password?token=SEU_TOKEN
            frontend_reset_url = "http://localhost:5173/reset-password" # Substitua pela URL real do seu frontend
            query_string = urlencode({'token': token, 'userId': user_id})
            reset_link = f"{frontend_reset_url}?{query_string}"

            subject = "Redefinição de Senha para sua Conta"
            text_content = f"""
            Olá {username},

            Você solicitou uma redefinição de senha para sua conta.
            Por favor, clique no link abaixo para redefinir sua senha:

            {reset_link}

            Este link expirará em 1 hora. Se você não solicitou esta redefinição, por favor, ignore este e-mail.

            Atenciosamente,
            Sua Equipe
            """
            html_content = f"""
            <p>Olá {username},</p>
            <p>Você solicitou uma redefinição de senha para sua conta.</p>
            <p>Por favor, clique no link abaixo para redefinir sua senha:</p>
            <p><a href="{reset_link}">Redefinir Senha</a></p>
            <p>Este link expirará em 1 hora. Se você não solicitou esta redefinição, por favor, ignore este e-mail.</p>
            <p>Atenciosamente,<br>Sua Equipe</p>
            """

            email_sent = send_email(user_email, subject, text_content, html_content)

            if email_sent:
                app_server.logger.info(f"E-mail de redefinição enviado para {user_email}.")
                return jsonify({"message": "Se o usuário existir, um e-mail com instruções de redefinição de senha foi enviado."}), 200
            else:
                app_server.logger.error(f"Falha ao enviar e-mail de redefinição para {user_email}.")
                return jsonify({"message": "Erro ao enviar e-mail de redefinição de senha."}), 500
        except Exception as e:
            app_server.logger.error(f"Erro inesperado ao solicitar redefinição de senha: {e}", exc_info=True)
            return jsonify({"error": "Erro interno do servidor ao solicitar redefinição de senha"}), 500

    @app_server.route('/api/reset-password', methods=['POST'])
    def reset_password():
        try:
            data = request.get_json()
            if data is None:
                app_server.logger.warning("Corpo da requisição inválido ou vazio para /api/reset-password.")
                return jsonify({"message": "Corpo da requisição inválido ou vazio. Esperado JSON."}), 400
            
            token = data.get('token')
            user_id_from_frontend = data.get('userId')
            new_password = data.get('newPassword')

            app_server.logger.debug(f"reset_password received - Token: {token}, User ID (from frontend): {user_id_from_frontend}, New Password Length: {len(new_password) if new_password else 0}")

            if not token or not new_password:
                app_server.logger.warning("Token ou nova senha ausentes para redefinição.")
                return jsonify({"message": "Token e nova senha são obrigatórios."}), 400

            token_data = bot_instance.db.get_password_reset_token(token)

            if not token_data:
                app_server.logger.warning(f"Token inválido ou expirado para redefinição: {token}")
                return jsonify({"message": "Token inválido ou expirado."}), 400

            # Afirma para o Pyright que 'token_data' não é None neste ponto
            assert token_data is not None

            # Validação extra: verificar se o user_id do token corresponde ao user_id fornecido (se fornecido)
            if user_id_from_frontend:
                try:
                    app_server.logger.debug(f"Raw token_data['user_id'] type: {type(token_data['user_id'])}, value: {token_data['user_id']}")
                    app_server.logger.debug(f"Raw user_id_from_frontend type: {type(user_id_from_frontend)}, value: {user_id_from_frontend}")

                    # CONVERTER user_id_from_frontend PARA INTEIRO ANTES DE COMPARAR
                    user_id_from_frontend_int = int(user_id_from_frontend)
                    
                    # Garante que token_data['user_id'] também é um inteiro para comparação
                    token_user_id_int = int(token_data['user_id'])

                    app_server.logger.debug(f"Converted token_user_id_int type: {type(token_user_id_int)}, value: {token_user_id_int}")
                    app_server.logger.debug(f"Converted user_id_from_frontend_int type: {type(user_id_from_frontend_int)}, value: {user_id_from_frontend_int}")
                    app_server.logger.debug(f"Comparison result (token_user_id_int == user_id_from_frontend_int): {token_user_id_int == user_id_from_frontend_int}")

                    if token_user_id_int != user_id_from_frontend_int:
                        app_server.logger.warning(f"User ID mismatch: token_user_id_int ({token_user_id_int}) != user_id_from_frontend_int ({user_id_from_frontend_int})")
                        return jsonify({"message": "Token inválido para este usuário."}), 400
                except ValueError:
                    app_server.logger.error(f"ValueError during ID conversion. user_id_from_frontend: '{user_id_from_frontend}', token_data['user_id']: '{token_data['user_id']}'")
                    return jsonify({"message": "ID de usuário fornecido ou no token é inválido."}), 400

            # Hash da nova senha
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            # Atualiza a senha do usuário
            password_updated = bot_instance.db.update_user_password(token_data['user_id'], hashed_password)

            if password_updated:
                # Marca o token como usado para evitar reutilização
                bot_instance.db.mark_token_as_used(token)
                app_server.logger.info(f"Senha redefinida com sucesso para user_id: {token_data['user_id']}")
                return jsonify({"message": "Senha redefinida com sucesso."}), 200
            else:
                app_server.logger.error(f"Erro ao redefinir a senha para user_id: {token_data['user_id']}")
                return jsonify({"message": "Erro ao redefinir a senha."}), 500
        except Exception as e:
            app_server.logger.error(f"Erro inesperado ao redefinir senha: {e}", exc_info=True)
            return jsonify({"error": "Erro interno do servidor ao redefinir senha"}), 500

    @app_server.route('/api/chat', methods=['POST'])
    # @jwt_required # Opcional: Descomente se quiser proteger esta rota com JWT
    def chat_with_agent():
        """
        Endpoint para encaminhar mensagens para o agente Zion da Evo AI
        e retornar a resposta.
        """
        try:
            data = request.get_json()
            if data is None:
                app_server.logger.warning("Corpo da requisição inválido ou vazio para /api/chat.")
                return jsonify({"message": "Corpo da requisição inválido ou vazio. Esperado JSON."}), 400

            user_message = data.get('message')
            if not user_message:
                app_server.logger.warning("Mensagem do usuário ausente na requisição /api/chat.")
                return jsonify({"message": "Mensagem é obrigatória."}), 400

            app_server.logger.info(f"Recebida mensagem do frontend: {user_message}")

            # Preparar cabeçalhos para a requisição ao agente Evo AI
            headers = {
                'Content-Type': 'application/json',
            }
            # Adicionar a chave da API se ela estiver definida
            if EVO_AI_API_KEY:
                headers['x-api-key'] = EVO_AI_API_KEY
                app_server.logger.debug("Usando x-api-key para autenticação com Evo AI.")
            else:
                app_server.logger.debug("EVO_AI_API_KEY não definida. Prosseguindo sem x-api-key.")

            agent_endpoint = cast(str, EVO_AI_AGENT_BASE_URL)

            # Corpo da requisição para o agente Evo AI no formato JSON-RPC 2.0
            agent_payload = {
                "jsonrpc": "2.0",
                "method": "message/send",
                "params": [user_message], # MODIFIED: Agora envia a mensagem como um parâmetro posicional em um array
                "id": 1 # Um ID de requisição simples
            }

            app_server.logger.debug(f"Enviando para Evo AI: {agent_endpoint} com payload: {agent_payload}")

            # Fazer a requisição POST para o agente Evo AI
            response = requests.post(agent_endpoint, headers=headers, json=agent_payload)
            response.raise_for_status() # Levanta um erro para códigos de status HTTP ruins (4xx ou 5xx)

            agent_response_data = response.json()
            app_server.logger.info(f"Resposta recebida do agente Evo AI: {agent_response_data}")

            # Extrair a resposta relevante do formato JSON-RPC
            if "result" in agent_response_data:
                # Se a resposta do agente estiver dentro de 'result', use-a
                return jsonify({"response": agent_response_data["result"]}), 200
            elif "error" in agent_response_data:
                # Se houver um erro na resposta JSON-RPC, retorne-o
                app_server.logger.error(f"Erro na resposta JSON-RPC da Evo AI: {agent_response_data['error']}")
                return jsonify({"message": f"Erro do agente Evo AI: {agent_response_data['error'].get('message', 'Erro desconhecido')}"}), 500
            else:
                # Caso a resposta não siga o padrão esperado, retorne a resposta completa para depuração
                app_server.logger.warning(f"Resposta inesperada da Evo AI: {agent_response_data}")
                return jsonify({"response": agent_response_data}), 200

        except requests.exceptions.HTTPError as http_err:
            app_server.logger.error(f"HTTP error communicating with Evo AI: {http_err}")
            app_server.logger.error(f"Evo AI response status code: {http_err.response.status_code}")
            app_server.logger.error(f"Evo AI response content: {http_err.response.text}")
            # Return the actual status code from Evo AI if it's a 4xx or 5xx
            return jsonify({"message": f"Erro ao se comunicar com o agente Evo AI: {http_err.response.text}"}), http_err.response.status_code
        except requests.exceptions.ConnectionError as conn_err:
            app_server.logger.error(f"Connection error communicating with Evo AI: {conn_err}")
            return jsonify({"message": "Erro de conexão com o agente Evo AI. Verifique a URL ou sua conexão de internet."}), 503
        except requests.exceptions.Timeout as timeout_err:
            app_server.logger.error(f"Timeout error communicating with Evo AI: {timeout_err}")
            return jsonify({"message": "Tempo limite excedido ao se comunicar com o agente Evo AI."}), 504
        except requests.exceptions.RequestException as req_err:
            app_server.logger.error(f"An unexpected error occurred during request to Evo AI: {req_err}")
            return jsonify({"message": "Ocorreu um erro inesperado ao se comunicar com o agente Evo AI."}), 500
        except Exception as e:
            app_server.logger.error(f"Erro interno no chat_with_agent: {str(e)}", exc_info=True)
            return jsonify({"message": "Ocorreu um erro interno no servidor."}), 500
