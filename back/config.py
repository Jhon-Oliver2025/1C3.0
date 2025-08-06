from flask import Flask
from flask import Flask
from flask_login import LoginManager
from flask_cors import CORS
import time
import os
import logging
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Detectar ambiente
ENVIRONMENT = os.getenv('FLASK_ENV', 'development')
IS_PRODUCTION = ENVIRONMENT == 'production'

# Forçar desenvolvimento para ambiente local
if not os.getenv('FLASK_ENV'):
    IS_PRODUCTION = False
    ENVIRONMENT = 'development'

# Configurar Flask com pasta static correta
server = Flask(__name__, static_folder='static', static_url_path='')



# Configurações de segurança
# Configurações de segurança
server.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'crypto_signals_secret_key_2025_muito_segura')
server.config['JWT_SECRET'] = os.getenv('JWT_SECRET')
# Remover as linhas 39-40
# server.config['EVO_AI_AGENT_BASE_URL'] = os.getenv('EVO_AI_AGENT_BASE_URL')
# server.config['EVO_AI_API_KEY'] = os.getenv('EVO_AI_API_KEY')

# Configurações de produção
if IS_PRODUCTION:
    server.config['SESSION_COOKIE_SECURE'] = True
    server.config['SESSION_COOKIE_HTTPONLY'] = True
    server.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    server.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hora

# Validar configurações obrigatórias
if not server.config['JWT_SECRET']:
    raise ValueError("❌ JWT_SECRET não está definido!")

print(f"✅ Ambiente: {ENVIRONMENT}")
print(f"✅ JWT_SECRET configurado: {server.config['JWT_SECRET'][:5]}...")

# Configuração da Binance
# Configuração da Binance
# Configuração da Binance
server.config['BINANCE_FUTURES'] = {
    'api_url': 'https://fapi.binance.com',
    'ws_url': 'wss://fstream.binance.com',
    'API_KEY': os.getenv('BINANCE_API_KEY', ''),
    'API_SECRET': os.getenv('BINANCE_SECRET_KEY', ''),
    'time_offset': 0
}

# Configuração do Telegram
server.config['TELEGRAM_TOKEN'] = os.getenv('TELEGRAM_BOT_TOKEN', "7690455274:AAHB64l8csWoE5UpV1Pnn9c8chJzd5sZTXQ")
server.config['TELEGRAM_CHAT_ID'] = os.getenv('TELEGRAM_CHAT_ID', "1249100206")

# Configuração de Logs
if IS_PRODUCTION:
    # Criar diretório de logs se não existir
    logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    log_file_path = os.path.join(logs_dir, 'app.log')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s %(message)s',
        handlers=[
            logging.FileHandler(log_file_path),
            logging.StreamHandler()
        ]
    )
else:
    logging.basicConfig(level=logging.DEBUG)

# Trading Configuration
server.config['TRADING'] = {
    'DEFAULT_TIMEFRAME': '4h',
    'MIN_VOLUME_USD': 500000,
    'MIN_SCORE': 7,
    'PREMIUM_SCORE': 8,

    'INDICATORS': {
        'RSI': {'window': 14, 'long_threshold': 30, 'short_threshold': 70},
        'EMA': {'fast': 9, 'slow': 21},
        'MACD': {'fast': 12, 'slow': 26, 'signal': 9},
        'BB': {'window': 20, 'std': 2},
        'SUPERTREND': {'period': 10, 'multiplier': 2.0}
    },

    'SCORE_WEIGHTS': {
        'trend_alignment': 2.0,
        'volume': 1.0,
        'momentum': 1.0,
        'pattern': 1.5,
        'correlation': 0.5
    }
}

login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = 'login'  # type: ignore

@login_manager.user_loader
def load_user(user_id):
    class User:
        def __init__(self, username):
            self.id = username
            self.is_authenticated = True
            self.is_active = True
            self.is_anonymous = False

        def get_id(self):
            return str(self.id)

    if user_id == 'admin':
        return User(user_id)
    return None

# Adicionar após as configurações existentes
# Configurações de performance
server.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000  # 1 ano
server.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
server.config['JSON_SORT_KEYS'] = False
server.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# Configurações de timeout para requests
server.config['REQUESTS_TIMEOUT'] = 60
server.config['BINANCE_TIMEOUT'] = 60