#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Krypton Trading Bot - Versão com Supabase
Sistema de trading automatizado com análise técnica avançada
"""

import os
import sys
import time
import logging
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Importar configurações
from config import server
from supabase_config import supabase_config

# Importar blueprints das rotas
from api_routes.auth import auth_bp
from api_routes.signals import signals_bp
from api_routes.trading import trading_bp
from api_routes.users import users_bp
from api_routes.notifications import notifications_bp
from api_routes.market_times import market_times_bp
from api_routes.market_status import market_status_bp
from api_routes.cleanup_status import cleanup_status_bp

# Configurar CORS
CORS(server, resources={
    r"/api/*": {
        "origins": ["*"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

class KryptonBotSupabase:
    """
    Bot de trading principal com integração Supabase
    """
    
    def __init__(self):
        self.config = supabase_config
        self.is_supabase_configured = self.config.is_configured
        
        if self.is_supabase_configured:
            self.database_url = self.config.get_database_url()
            print("✅ Supabase configurado")
        else:
            self.database_url = None
            print("⚠️ Supabase não configurado - modo degradado")
        
        # Inicializar componentes
        self._init_components()
        
        print("✅ KryptonBot inicializado")
    
    def _init_components(self):
        """
        Inicializa os componentes do bot
        """
        try:
            # Importar e inicializar componentes essenciais
            from core.binance_client import BinanceClient
            from core.telegram_notifier import TelegramNotifier
            from core.technical_analysis import TechnicalAnalysis
            from core.gerenciar_sinais import GerenciadorSinais
            from core.database import Database
            from core.market_scheduler import MarketScheduler
            
            # Inicializar instância do banco de dados
            self.db = Database()
            
            # Inicializar clientes
            self.binance_client = BinanceClient()
            self.telegram = TelegramNotifier()
            
            # Inicializar análise técnica com instância do banco
            try:
                self.technical_analysis = TechnicalAnalysis(self.db)
            except TypeError:
                # Fallback se TechnicalAnalysis não aceitar db_instance
                self.technical_analysis = TechnicalAnalysis()
            
            # Inicializar gerenciador de sinais
            if self.is_supabase_configured and self.database_url:
                self.gerenciador_sinais = GerenciadorSinais(self.db)
            else:
                # Modo degradado sem banco
                self.gerenciador_sinais = None
                print("⚠️ Gerenciador de sinais desabilitado - Supabase não configurado")
            
            # Inicializar scheduler de mercado
            try:
                self.market_scheduler = MarketScheduler(self.db, self.technical_analysis)
                self.market_scheduler.start()
                print("✅ Market Scheduler inicializado e ativo")
            except Exception as scheduler_error:
                print(f"⚠️ Erro ao inicializar Market Scheduler: {scheduler_error}")
                self.market_scheduler = None
            
            # Inicializar monitoramento contínuo de mercado
            try:
                import threading
                import time
                
                def start_monitoring():
                    """Inicia o monitoramento contínuo após 5 segundos"""
                    time.sleep(5)  # Aguardar Flask inicializar
                    print("🔍 Iniciando monitoramento contínuo de mercado...")
                    if hasattr(self, 'technical_analysis') and self.technical_analysis:
                        self.technical_analysis.start_monitoring()
                    else:
                        print("⚠️ TechnicalAnalysis não disponível para monitoramento")
                
                # Iniciar thread de monitoramento
                monitor_thread = threading.Thread(target=start_monitoring, daemon=True)
                monitor_thread.start()
                print("✅ Thread de monitoramento iniciada")
                
            except Exception as monitor_error:
                print(f"⚠️ Erro ao inicializar monitoramento: {monitor_error}")
            
            print("✅ Componentes inicializados com sucesso")
            
        except Exception as e:
            print(f"⚠️ Erro ao inicializar componentes: {e}")
            # Continuar mesmo com erros para permitir healthcheck
            # Garantir que pelo menos a instância do banco existe
            if not hasattr(self, 'db'):
                try:
                    from core.database import Database
                    self.db = Database()
                    print("✅ Instância do banco inicializada em modo de recuperação")
                except Exception as db_error:
                    print(f"⚠️ Erro ao inicializar banco em modo de recuperação: {db_error}")
                    # Criar um mock do banco para evitar erros
                    class MockDatabase:
                        def get_user_by_username(self, username):
                            return None
                        def get_user_by_email(self, email):
                            return None
                    self.db = MockDatabase()
    
    def get_status(self):
        """
        Retorna o status do bot
        """
        status = {
            'bot': 'running',
            'database': 'connected' if self.is_supabase_configured else 'degraded',
            'supabase_configured': self.is_supabase_configured,
            'timestamp': datetime.now().isoformat()
        }
        
        if self.is_supabase_configured:
            status['supabase_url'] = self.config.SUPABASE_URL
        
        # Verificar componentes
        try:
            if hasattr(self, 'binance_client'):
                status['binance'] = 'connected'
            if hasattr(self, 'telegram'):
                status['telegram'] = 'connected'
            if hasattr(self, 'gerenciador_sinais') and self.gerenciador_sinais:
                status['signals'] = 'connected'
            else:
                status['signals'] = 'degraded'
        except:
            pass
        
        return status

# Instância global do bot
bot = None

def create_app():
    """
    Factory function para criar a aplicação Flask
    """
    global bot
    
    try:
        # Inicializar o bot
        bot = KryptonBotSupabase()
        print("✅ Bot inicializado com sucesso")
    except Exception as e:
        print(f"⚠️ Erro ao inicializar bot: {e}")
        # Criar um bot mock para permitir que a aplicação inicie
        class MockBot:
            def get_status(self):
                return {
                    'bot': 'degraded',
                    'error': 'Initialization failed',
                    'timestamp': datetime.now().isoformat()
                }
        bot = MockBot()
    
    # Configurações adicionais
    server.config['JWT_SECRET'] = os.getenv('JWT_SECRET', 'default-jwt-secret-key')
    
    # Adicionar instância do bot ao contexto da aplicação
    server.bot_instance = bot
    
    # Registrar blueprints das rotas de API
    server.register_blueprint(auth_bp, url_prefix='/api/auth')
    server.register_blueprint(signals_bp, url_prefix='/api/signals')
    server.register_blueprint(trading_bp, url_prefix='/api/trading')
    server.register_blueprint(users_bp, url_prefix='/api/users')
    server.register_blueprint(notifications_bp, url_prefix='/api/notifications')
    server.register_blueprint(market_times_bp, url_prefix='/api')
    server.register_blueprint(market_status_bp, url_prefix='/api')
    server.register_blueprint(cleanup_status_bp, url_prefix='/api')
    
    # Registrar rotas básicas
    @server.route('/api/health')
    def health_check():
        """
        Endpoint de health check para Docker
        """
        try:
            status = bot.get_status()
            return jsonify({
                'status': 'healthy',
                'service': 'krypton-bot-supabase',
                'details': status
            }), 200
        except Exception as e:
            return jsonify({
                'status': 'unhealthy',
                'service': 'krypton-bot-supabase',
                'error': str(e)
            }), 500
    
    @server.route('/api/status')
    def api_status():
        """
        Endpoint de status da API
        """
        try:
            status = bot.get_status()
            return jsonify(status), 200
        except Exception as e:
            return jsonify({
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }), 500
    
    @server.route('/api/test-telegram')
    def test_telegram():
        """
        Endpoint de teste para Telegram
        """
        try:
            telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
            telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
            
            if not telegram_token or not telegram_chat_id:
                return jsonify({
                    'status': 'error',
                    'message': 'Telegram não configurado',
                    'configured': False
                }), 400
            
            return jsonify({
                'status': 'success',
                'message': 'Telegram configurado',
                'configured': True,
                'bot_token_configured': bool(telegram_token),
                'chat_id_configured': bool(telegram_chat_id)
            }), 200
            
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    
    @server.route('/api/test-binance')
    def test_binance():
        """
        Endpoint de teste para Binance API
        """
        try:
            binance_api_key = os.getenv('BINANCE_API_KEY')
            binance_secret_key = os.getenv('BINANCE_SECRET_KEY')
            
            if not binance_api_key or not binance_secret_key:
                return jsonify({
                    'status': 'error',
                    'message': 'Binance API não configurada',
                    'configured': False
                }), 400
            
            return jsonify({
                'status': 'success',
                'message': 'Binance API configurada',
                'configured': True,
                'api_key_configured': bool(binance_api_key),
                'secret_key_configured': bool(binance_secret_key)
            }), 200
            
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    
    @server.route('/api/scan-market', methods=['POST'])
    def scan_market_manual():
        """
        Endpoint para executar escaneamento manual do mercado
        """
        try:
            from datetime import datetime
            import pytz
            
            # Obter horário de São Paulo
            tz = pytz.timezone('America/Sao_Paulo')
            now = datetime.now(tz)
            
            print(f"\n🔍 ESCANEAMENTO MANUAL SOLICITADO - {now.strftime('%d/%m/%Y %H:%M:%S')}")
            
            if not hasattr(bot, 'technical_analysis') or not bot.technical_analysis:
                return jsonify({
                    'status': 'error',
                    'message': 'TechnicalAnalysis não inicializado'
                }), 500
            
            # Executar escaneamento
            signals = bot.technical_analysis.scan_market(verbose=True)
            
            result = {
                'status': 'success',
                'timestamp': now.strftime('%Y-%m-%d %H:%M:%S %Z'),
                'signals_found': len(signals),
                'signals': signals
            }
            
            if signals:
                print(f"\n🎯 ESCANEAMENTO MANUAL CONCLUÍDO:")
                print(f"✨ {len(signals)} novos sinais encontrados!")
                for signal in signals:
                    print(f"   • {signal['symbol']}: {signal['type']} - {signal['signal_class']} (Score: {signal['quality_score']:.1f})")
            else:
                print(f"\n📊 Nenhum sinal de qualidade encontrado no escaneamento manual")
            
            return jsonify(result), 200
            
        except Exception as e:
            print(f"❌ Erro no escaneamento manual: {e}")
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    
    @server.route('/')
    def index():
        """
        Página inicial
        """
        return jsonify({
            'service': 'Krypton Trading Bot - Supabase',
            'version': '2.0.0',
            'status': 'running',
            'database': 'supabase'
        })
    
    # NOVO: Endpoint público para sinais (sem autenticação)
    @server.route('/api/signals/public', methods=['GET'])
    def get_public_signals():
        """Endpoint público para obter sinais sem autenticação diretamente do banco"""
        try:
            from datetime import datetime, timedelta
            from supabase import create_client, Client
            
            # Inicializar cliente Supabase
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_ANON_KEY')
            
            if not supabase_url or not supabase_key:
                return jsonify({
                    'success': False,
                    'error': 'Supabase não configurado',
                    'message': 'Configuração do banco de dados não encontrada'
                }), 500
            
            supabase: Client = create_client(supabase_url, supabase_key)
            
            # Buscar sinais diretamente do banco de dados (com filtro de 24h restaurado)
            try:
                from datetime import timezone
                utc_24h_ago = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
                result = supabase.table('signals').select('*').eq('status', 'OPEN').gte('created_at', utc_24h_ago).order('created_at', desc=True).limit(20).execute()
            except Exception as e:
                print(f"⚠️ Erro na consulta Supabase: {e}")
                return jsonify({
                    'signals': [],
                    'success': True,
                    'total': 0,
                    'message': 'Sistema temporariamente indisponível'
                }), 200
            
            signals = []
            for signal in result.data:
                # Filtrar apenas sinais de alta qualidade (80+ pontos)
                quality_score = float(signal.get('quality_score') or 0)
                if quality_score < 80.0:
                    continue  # Pular sinais de baixa qualidade
                
                # Calcular projection_percentage e signal_class baseado nos dados existentes
                entry_price = float(signal.get('entry_price') or 0)
                target_price = float(signal.get('target_price') or 0)
                signal_type = signal.get('type', '')
                
                # Calcular projeção
                if entry_price > 0 and target_price > 0:
                    if signal_type == 'COMPRA':
                        projection_percentage = ((target_price - entry_price) / entry_price) * 100
                    else:  # VENDA
                        projection_percentage = ((entry_price - target_price) / entry_price) * 100
                else:
                    projection_percentage = 0
                
                # Determinar signal_class baseado no quality_score
                if quality_score >= 110:
                    signal_class = "ELITE+"
                elif quality_score >= 95:
                    signal_class = "ELITE"
                elif quality_score >= 85:
                    signal_class = "PREMIUM+"
                elif quality_score >= 80:
                    signal_class = "PREMIUM"
                else:
                    signal_class = "STANDARD"
                
                # Formatar dados para o frontend
                formatted_signal = {
                    'symbol': signal.get('symbol', ''),
                    'type': signal_type,
                    'entry_price': entry_price,
                    'entry_time': signal.get('entry_time', signal.get('created_at', '')),
                    'target_price': target_price,
                    'projection_percentage': round(projection_percentage, 2),
                    'signal_class': signal_class,
                    'status': signal.get('status', ''),
                    'quality_score': quality_score
                }
                signals.append(formatted_signal)
            
            print(f"📊 Retornando {len(signals)} sinais do banco de dados")
            
            return jsonify({
                'success': True,
                'signals': signals,
                'total': len(signals)
            })
        except Exception as e:
            import traceback
            print(f"❌ Erro ao buscar sinais: {e}")
            print(traceback.format_exc())
            return jsonify({
                'success': False,
                'error': str(e),
                'message': 'Erro ao buscar sinais do banco de dados'
            }), 500
    
    return server

def main():
    """
    Função principal
    """
    print("🚀 Iniciando Krypton Trading Bot com Supabase...")
    
    # Verificar variáveis de ambiente críticas
    try:
        supabase_config._validate_config()
    except ValueError as e:
        print(f"⚠️ Aviso de configuração: {e}")
        print("💡 Executando em modo degradado - configure as variáveis do Supabase para funcionalidade completa")
        # Não sair, continuar em modo degradado
    
    # Criar aplicação
    app = create_app()
    
    # Configurações do servidor
    port = int(os.getenv('FLASK_PORT', 5000))
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"🌐 Servidor iniciando em {host}:{port}")
    print(f"🔧 Debug mode: {debug}")
    print(f"🗄️ Database: Supabase")
    
    # Iniciar servidor
    try:
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n👋 Encerrando aplicação...")
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()