from flask import Flask
from flask_login import LoginManager
from flask_cors import CORS
import time  # Add this import

# Configurar Flask com pasta static correta
server = Flask(__name__, static_folder='static', static_url_path='')
# Permite requisições de http://localhost:5173 e de qualquer outra origem
CORS(server, resources={r"/*": {"origins": ["http://localhost:5173", "*"]}})
# Ou, se quiser ser mais restritivo e permitir APENAS o seu frontend:
# CORS(server, resources={r"/*": {"origins": "http://localhost:5173"}})
server.config['SECRET_KEY'] = 'chave-secreta-krypton-2024'

# --- Início da Edição ---
# Adicionar chaves da API da Binance diretamente ao config do Flask
# Binance Futures API Configuration
# Adicionar após a configuração da Binance
server.config['BINANCE_FUTURES'] = {
    'api_url': 'https://fapi.binance.com',
    'ws_url': 'wss://fstream.binance.com',
    'API_KEY': 'CBeEjFuDgfCCdAuyC9ITwP9cRd5mc4AIGaK8eWgDisEdzjdt32S2JflZwMLwIjFp',
    'API_SECRET': 'RS5p0K6l6802saRfE23erEZMtwoZu65GrAfBWP6r5BCAyrUasN4fQCGjS9UzB7Xk',
    'time_offset': 0  # Adicionar esta linha
}

# Adicionar função para sincronizar o tempo
def sync_binance_time():
    from binance.client import Client
    client = Client()
    server_time = client.get_server_time()
    return server_time['serverTime'] - int(time.time() * 1000)

# Atualizar o time_offset
server.config['BINANCE_FUTURES']['time_offset'] = sync_binance_time()
# --- Fim da Edição ---

# Telegram Configuration
server.config['TELEGRAM_TOKEN'] = "7690455274:AAHB64l8csWoE5UpV1Pnn9c8chJzd5sZTXQ"
server.config['TELEGRAM_CHAT_ID'] = "1249100206"

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