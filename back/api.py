from flask import Flask
from flask_cors import CORS
import os
from typing import cast

# Importar blueprints - CORRIGIDO: usar api_routes em vez de api
from api_routes.auth import auth_bp
from api_routes.signals import signals_bp
from api_routes.trading import trading_bp
from api_routes.users import users_bp
from api_routes.notifications import notifications_bp

def create_app():
    """Factory function para criar a aplicação Flask"""
    app = Flask(__name__)
    CORS(app)
    
    # Configurações
    app.config['JWT_SECRET'] = os.getenv('JWT_SECRET')
    app.config['EVO_AI_AGENT_BASE_URL'] = os.getenv('EVO_AI_AGENT_BASE_URL')
    app.config['EVO_AI_API_KEY'] = os.getenv('EVO_AI_API_KEY')
    
    # Validar configurações obrigatórias
    if not app.config['JWT_SECRET']:
        raise ValueError("❌ JWT_SECRET não está definido!")
    
    if not app.config['EVO_AI_AGENT_BASE_URL']:
        raise ValueError("❌ EVO_AI_AGENT_BASE_URL não está definido!")
    
    print(f"✅ JWT_SECRET configurado: {app.config['JWT_SECRET'][:5]}...")
    
    return app

app = create_app()

def register_api_routes(app_instance, bot_instance):
    """Registra todas as rotas da API"""
    print("DEBUG: register_api_routes foi chamada!")
    
    # Registrar blueprints
    app_instance.register_blueprint(auth_bp, url_prefix='/api/auth')
    app_instance.register_blueprint(signals_bp, url_prefix='/api/signals')
    app_instance.register_blueprint(trading_bp, url_prefix='/api/trading')
    app_instance.register_blueprint(users_bp, url_prefix='/api/users')
    app_instance.register_blueprint(notifications_bp, url_prefix='/api/notifications')
    
    # Rota raiz
    @app_instance.route('/')
    def index():
        return {"message": "API do backend Flask está online!"}, 200
    
    @app_instance.route('/status', methods=['GET', 'HEAD'])
    def health_check():
        return {"status": "ok"}, 200
    
    # Adicionar rota direta para compatibilidade com frontend
    @app_instance.route('/signals', methods=['GET'])
    def get_signals_direct():
        """Rota direta para /signals (compatibilidade)"""
        from api_routes.signals import get_signals
        return get_signals()
    
    # Armazenar bot_instance para uso nos blueprints
    app_instance.bot_instance = bot_instance

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)