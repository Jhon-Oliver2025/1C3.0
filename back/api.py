from flask import Flask
import os
from typing import cast

# Importar a configuração do servidor do config.py
from config import server

# Importar blueprints
from api_routes.auth import auth_bp
from api_routes.signals import signals_bp
from api_routes.trading import trading_bp
from api_routes.users import users_bp
from api_routes.notifications import notifications_bp
from api_routes.market_times import market_times_bp

def create_app():
    """Factory function para criar a aplicação Flask"""
    # Usar o servidor já configurado do config.py (que já tem CORS configurado)
    app = server
    
    # Configurações adicionais
    app.config['JWT_SECRET'] = os.getenv('JWT_SECRET')
    
    # Validar configurações obrigatórias
    if not app.config['JWT_SECRET']:
        raise ValueError("❌ JWT_SECRET não está definido!")
    
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
    app_instance.register_blueprint(market_times_bp, url_prefix='/api')
    
    # Rota raiz
    @app_instance.route('/')
    def index():
        return {"message": "API do backend Flask está online!"}, 200
    
    @app_instance.route('/status', methods=['GET', 'HEAD'])
    def health_check():
        return {"status": "ok"}, 200
    
    # Adicionar rota /api/status para compatibilidade com frontend
    @app_instance.route('/api/status', methods=['GET', 'HEAD'])
    def api_health_check():
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