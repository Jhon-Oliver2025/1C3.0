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
    
    # NOVA: Adicionar rota /api/health
    @app_instance.route('/api/health', methods=['GET', 'HEAD'])
    def api_health():
        return {"status": "healthy", "service": "crypto-signals-api"}, 200
    
    # NOVA: Adicionar rota /api/scheduler-status
    @app_instance.route('/api/scheduler-status', methods=['GET'])
    def scheduler_status():
        """Retorna o status do agendador de limpeza de sinais"""
        try:
            from market_scheduler import get_scheduler_status
            from datetime import datetime
            import pytz
            
            # Obter timezone de São Paulo
            tz = pytz.timezone('America/Sao_Paulo')
            now = datetime.now(tz)
            
            status = get_scheduler_status()
            status['current_time'] = now.strftime('%Y-%m-%d %H:%M:%S %Z')
            status['next_morning_cleanup'] = '10:00 (Brasília)'
            status['next_evening_cleanup'] = '21:00 (Brasília)'
            
            return status, 200
        except Exception as e:
            return {"error": f"Erro ao obter status do scheduler: {str(e)}"}, 500
    
    # NOVA: Adicionar rota /api/force-cleanup
    @app_instance.route('/api/force-cleanup', methods=['POST'])
    def force_cleanup():
        """Endpoint para forçar limpeza manual dos sinais"""
        try:
            from core.gerenciar_sinais import GerenciadorSinais
            from core.database import Database
            import pytz
            from datetime import datetime
            
            # Inicializar componentes
            db = Database()
            gerenciador = GerenciadorSinais(db)
            
            # Obter horário atual
            tz = pytz.timezone('America/Sao_Paulo')
            now = datetime.now(tz)
            
            results = {
                'timestamp': now.strftime('%Y-%m-%d %H:%M:%S %Z'),
                'cleanups_executed': []
            }
            
            # Executar limpeza matinal
            try:
                gerenciador.limpar_sinais_antes_das_10h()
                results['cleanups_executed'].append('morning_cleanup_10h')
            except Exception as e:
                results['morning_cleanup_error'] = str(e)
            
            # Executar limpeza noturna
            try:
                gerenciador.limpar_sinais_antes_das_21h()
                results['cleanups_executed'].append('evening_cleanup_21h')
            except Exception as e:
                results['evening_cleanup_error'] = str(e)
            
            # Executar limpeza de sinais futuros
            try:
                gerenciador.limpar_sinais_futuros()
                results['cleanups_executed'].append('future_signals_cleanup')
            except Exception as e:
                results['future_signals_error'] = str(e)
            
            return results, 200
        except Exception as e:
            return {"error": f"Erro ao executar limpeza: {str(e)}"}, 500
    
    # NOVA: Adicionar rota /api/scheduler-logs
    @app_instance.route('/api/scheduler-logs', methods=['GET'])
    def scheduler_logs():
        """Endpoint para verificar logs do scheduler"""
        try:
            import os
            
            log_file = '/tmp/scheduler_log.txt'
            
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    logs = f.read().strip().split('\n')
                
                # Retornar apenas as últimas 50 linhas
                recent_logs = logs[-50:] if len(logs) > 50 else logs
                
                return {
                    'logs': recent_logs,
                    'total_entries': len(logs),
                    'log_file_exists': True
                }, 200
            else:
                return {
                    'logs': [],
                    'total_entries': 0,
                    'log_file_exists': False,
                    'message': 'Arquivo de log não encontrado - scheduler pode não ter executado ainda'
                }, 200
        except Exception as e:
            return {"error": str(e)}, 500
    
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