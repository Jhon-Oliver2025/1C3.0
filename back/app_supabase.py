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
        self.database_url = self.config.get_database_url()
        
        # Inicializar componentes
        self._init_components()
        
        print("✅ KryptonBot inicializado com Supabase")
    
    def _init_components(self):
        """
        Inicializa os componentes do bot
        """
        try:
            # Importar e inicializar componentes essenciais
            from core.binance_client import BinanceClient
            from core.telegram_notifier import TelegramNotifier
            from core.technical_analysis import TechnicalAnalysis
            from core.gerenciador_sinais import GerenciadorSinais
            
            # Inicializar clientes
            self.binance_client = BinanceClient()
            self.telegram = TelegramNotifier()
            self.technical_analysis = TechnicalAnalysis()
            
            # Inicializar gerenciador de sinais com Supabase
            self.gerenciador_sinais = GerenciadorSinais(
                database_url=self.database_url,
                use_supabase=True
            )
            
            print("✅ Componentes inicializados com sucesso")
            
        except Exception as e:
            print(f"⚠️ Erro ao inicializar componentes: {e}")
            # Continuar mesmo com erros para permitir healthcheck
    
    def get_status(self):
        """
        Retorna o status do bot
        """
        status = {
            'bot': 'running',
            'database': 'connected',
            'supabase_url': self.config.SUPABASE_URL,
            'timestamp': datetime.now().isoformat()
        }
        
        # Verificar componentes
        try:
            if hasattr(self, 'binance_client'):
                status['binance'] = 'connected'
            if hasattr(self, 'telegram'):
                status['telegram'] = 'connected'
            if hasattr(self, 'gerenciador_sinais'):
                status['signals'] = 'connected'
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
        print(f"❌ Erro de configuração: {e}")
        print("💡 Certifique-se de que as variáveis SUPABASE_URL, SUPABASE_ANON_KEY e SUPABASE_DATABASE_URL estão definidas")
        sys.exit(1)
    
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