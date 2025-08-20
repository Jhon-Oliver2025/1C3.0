from flask import Flask
import os
from typing import cast
from flask_cors import CORS # Importar CORS

# Importar a configuração do servidor do config.py
from config import server

# Importar blueprints
from api_routes.auth import auth_bp
from api_routes.signals import signals_bp
from api_routes.btc_signals import btc_signals_bp
from api_routes.trading import trading_bp
from api_routes.users import users_bp
from api_routes.notifications import notifications_bp
from api_routes.market_times import market_times_bp
from api_routes.market_status import market_status_bp
from api_routes.cleanup_status import cleanup_status_bp
from api_routes.signal_monitoring import signal_monitoring_bp
# from api_routes.analytics import analytics_bp  # Módulo não existe
from api_routes.scheduler_management import scheduler_management_bp
from api_routes.restart_system import restart_system_bp

def create_app():
    """Factory function para criar a aplicação Flask"""
    # Usar o servidor já configurado do config.py
    app = server
    app.url_map.strict_slashes = False # Desabilitar redirecionamento de barras finais
    CORS(app, resources={r"/*": {"origins": ["http://localhost:3001", "http://localhost:3000", "http://localhost:5173", "https://1crypten.space", "https://www.1crypten.space"], "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"], "allow_headers": ["Content-Type", "Authorization"], "supports_credentials": True}})
    
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
    
    # Definir bot_instance no contexto da aplicação para acesso global
    app_instance.bot_instance = bot_instance
    print(f"🔍 [DEBUG] bot_instance definido no app: {bot_instance}")
    
    # Inicializar rotas BTC Signals com o btc_signal_manager do bot
    if hasattr(bot_instance, 'analyzer') and hasattr(bot_instance.analyzer, 'btc_signal_manager'):
        from api_routes.btc_signals import init_btc_signals_routes
        init_btc_signals_routes(bot_instance.db, bot_instance.analyzer.btc_signal_manager)
        print("✅ Rotas BTC Signals inicializadas com btc_signal_manager!")
        print(f"🔍 [DEBUG] btc_signal_manager: {bot_instance.analyzer.btc_signal_manager}")
        
        # Inicializar rotas Market Status com btc_analyzer
        if hasattr(bot_instance.analyzer.btc_signal_manager, 'btc_analyzer'):
            from api_routes.market_status import init_market_status_routes
            init_market_status_routes(bot_instance.analyzer.btc_signal_manager.btc_analyzer)
            print("✅ Rotas Market Status inicializadas com btc_analyzer!")
        else:
            print("⚠️ btc_analyzer não encontrado no btc_signal_manager")
    else:
        print("⚠️ btc_signal_manager não encontrado no bot_instance")
    
    # Inicializar rotas de Monitoramento de Sinais
    if hasattr(bot_instance, 'analyzer') and hasattr(bot_instance.analyzer, 'binance') and hasattr(bot_instance, 'db'):
        from api_routes.signal_monitoring import init_signal_monitoring_routes
        init_signal_monitoring_routes(bot_instance.db, bot_instance.analyzer.binance)
        print("✅ Rotas de Monitoramento de Sinais inicializadas!")
        print(f"🔍 [DEBUG] binance_client: {bot_instance.analyzer.binance}")
    else:
        print("⚠️ Dependências para monitoramento não encontradas no bot_instance")
        print(f"🔍 [DEBUG] bot_instance.analyzer: {getattr(bot_instance, 'analyzer', 'NOT_FOUND')}")
        print(f"🔍 [DEBUG] analyzer.binance: {getattr(getattr(bot_instance, 'analyzer', None), 'binance', 'NOT_FOUND')}")
        print(f"🔍 [DEBUG] bot_instance.db: {getattr(bot_instance, 'db', 'NOT_FOUND')}")
    
    # Registrar blueprints
    app_instance.register_blueprint(auth_bp, url_prefix='/api/auth')
    app_instance.register_blueprint(signals_bp, url_prefix='/api/signals')
    app_instance.register_blueprint(btc_signals_bp)  # Já tem url_prefix='/api/btc-signals' definido no blueprint
    app_instance.register_blueprint(signal_monitoring_bp)  # Já tem url_prefix='/api/signal-monitoring' definido no blueprint
    app_instance.register_blueprint(trading_bp, url_prefix='/api/trading')
    app_instance.register_blueprint(users_bp, url_prefix='/api/users')
    app_instance.register_blueprint(notifications_bp, url_prefix='/api/notifications')
    app_instance.register_blueprint(market_times_bp, url_prefix='/api')
    app_instance.register_blueprint(market_status_bp, url_prefix='/api')
    app_instance.register_blueprint(cleanup_status_bp, url_prefix='/api')
    # app_instance.register_blueprint(analytics_bp, url_prefix='/api/analytics')  # Módulo não existe
    app_instance.register_blueprint(scheduler_management_bp, url_prefix='/api')
    app_instance.register_blueprint(restart_system_bp)  # Já tem url_prefix='/api/restart-system' definido no blueprint
    
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
        health_status = {"status": "healthy", "service": "crypto-signals-api"}
        
        # Verificar conectividade com PostgreSQL
        try:
            from core.db_config import DatabaseConfig
            db_config = DatabaseConfig()
            with db_config.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    health_status["database"] = "connected"
        except Exception as e:
            health_status["database"] = f"error: {str(e)}"
            health_status["status"] = "degraded"
        
        # Verificar Redis
        try:
            from core.db_config import DatabaseConfig
            db_config = DatabaseConfig()
            if db_config.redis_client:
                db_config.redis_client.ping()
                health_status["redis"] = "connected"
            else:
                health_status["redis"] = "not_available"
        except Exception as e:
            health_status["redis"] = "not_available"
            # Redis não é crítico para o funcionamento do sistema
        
        return health_status, 200
    
    # NOVA: Adicionar rota /api/scheduler-status
    @app_instance.route('/api/scheduler-status', methods=['GET'])
    def scheduler_status():
        """Retorna o status do agendador de limpeza de sinais"""
        try:
            from market_scheduler import get_scheduler_status, restart_scheduler
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
    
    # NOVA: Adicionar rota /api/restart-scheduler
    @app_instance.route('/api/restart-scheduler', methods=['POST'])
    def restart_scheduler_endpoint():
        """Reinicia o scheduler se não estiver rodando"""
        try:
            from datetime import datetime
            import pytz
            
            # Obter timezone de São Paulo
            tz = pytz.timezone('America/Sao_Paulo')
            now = datetime.now(tz)
            
            # Reiniciar o scheduler
            from market_scheduler import restart_scheduler
            scheduler_instance = restart_scheduler()
            
            return {
                'success': True,
                'message': 'Scheduler reiniciado com sucesso',
                'scheduler_running': scheduler_instance.running if scheduler_instance else False,
                'timestamp': now.strftime('%Y-%m-%d %H:%M:%S %z')
            }, 200
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }, 500
    
    # NOVA: Endpoint público para estatísticas dos sinais
    @app_instance.route('/api/signals/stats', methods=['GET'])
    def signals_stats():
        """Endpoint público para verificar estatísticas dos sinais"""
        try:
            from core.database import Database
            from datetime import datetime
            import pytz
            
            db = Database()
            
            # Obter estatísticas dos sinais
            query = """
            SELECT 
                DATE(created_at) as signal_date,
                COUNT(*) as count
            FROM signals 
            GROUP BY DATE(created_at)
            ORDER BY signal_date DESC
            LIMIT 10
            """
            
            results = db.execute_query(query)
            
            # Obter contagem total
            total_query = "SELECT COUNT(*) as total FROM signals"
            total_result = db.execute_query(total_query)
            total_signals = total_result[0]['total'] if total_result else 0
            
            # Obter timezone de São Paulo
            tz = pytz.timezone('America/Sao_Paulo')
            now = datetime.now(tz)
            
            stats = {
                'timestamp': now.strftime('%Y-%m-%d %H:%M:%S %Z'),
                'total_signals': total_signals,
                'signals_by_date': results,
                'current_date': now.strftime('%Y-%m-%d')
            }
            
            return stats, 200
            
        except Exception as e:
            return {"error": f"Erro ao obter estatísticas: {str(e)}"}, 500
    
    # NOVO: Endpoint público para sinais (sem autenticação)
    @app_instance.route('/api/signals/public', methods=['GET'])
    def get_public_signals():
        """Endpoint público para obter sinais sem autenticação"""
        try:
            import csv
            import os
            from flask import jsonify
            
            # Caminho para o arquivo CSV
            signals_file = os.path.join(os.path.dirname(__file__), 'sinais_lista.csv')
            
            if not os.path.exists(signals_file):
                return jsonify({
                    'success': False,
                    'error': 'Arquivo de sinais não encontrado'
                }), 404
            
            # Ler o CSV usando o módulo csv nativo
            signals = []
            with open(signals_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Filtrar apenas sinais PREMIUM e ELITE
                    if row.get('signal_class') in ['PREMIUM', 'ELITE']:
                        signals.append(row)
            
            return jsonify({
                'success': True,
                'signals': signals,
                'total': len(signals)
            })
        except Exception as e:
            import traceback
            return jsonify({
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc()
            }), 500
    
    # Armazenar bot_instance para uso nos blueprints
    app_instance.bot_instance = bot_instance

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)