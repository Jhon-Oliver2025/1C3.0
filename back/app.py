# System imports
from dotenv import load_dotenv
import os
import sys
import subprocess
import atexit
import threading
import time
import pytz
import pandas as pd
from datetime import datetime, timedelta
import cryptocompare
import traceback
import signal
import logging
from typing import cast
import importlib.util

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Flask imports
from config import server

# Core imports
from core.database import Database
from core.db_config import DatabaseConfig
from core.binance_client import BinanceClient
from core.technical_analysis import TechnicalAnalysis
from core.gerenciar_sinais import GerenciadorSinais
from core.telegram_notifier import TelegramNotifier
# Corrigir esta linha - importar a função em vez da classe
from core.email_service import send_email

# Importar diretamente do arquivo api.py (CORRIGIDO)
from api import create_app, register_api_routes

# Import market scheduler
from market_scheduler import setup_market_scheduler

# Inicializar variável global para o processo Node.js
node_process = None

def start_nodejs_backend():
    """Inicia o servidor Node.js em segundo plano."""
    global node_process
    print("🚀 Tentando iniciar o backend Node.js...")
    try:
        # Verificar se o Node.js está rodando
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js detectado: {result.stdout.strip()}")
            
            # Define o caminho para o diretório do backend Node.js
            nodejs_dir = os.path.dirname(os.path.abspath(__file__))

            # Cria uma cópia das variáveis de ambiente atuais
            env_for_nodejs = os.environ.copy()
            # Define explicitamente a porta para o processo Node.js
            env_for_nodejs['PORT'] = '5001'
            
            # Comando para iniciar o servidor Node.js
            node_process = subprocess.Popen(
                ['node', 'server.js'],
                cwd=nodejs_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env_for_nodejs,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            )
            print(f"✅ Backend Node.js iniciado com PID: {node_process.pid}")
            
            # Thread para ler a saída do Node.js
            def read_nodejs_output(pipe, prefix):
                for line in iter(pipe.readline, b''):
                    print(f"[{prefix}] {line.decode().strip()}")
                pipe.close()

            threading.Thread(target=read_nodejs_output, args=(node_process.stdout, "NODE_OUT"), daemon=True).start()
            threading.Thread(target=read_nodejs_output, args=(node_process.stderr, "NODE_ERR"), daemon=True).start()
        else:
            print("⚠️ Node.js não encontrado")
            
    except FileNotFoundError:
        print("❌ Erro: 'node' não encontrado. Certifique-se de que Node.js está instalado e no PATH.")
        node_process = None
    except Exception as e:
        print(f"❌ Erro ao iniciar o backend Node.js: {e}")
        node_process = None

def stop_nodejs_backend():
    """Para o servidor Node.js se estiver rodando."""
    global node_process
    if node_process and node_process.poll() is None:
        print("🛑 Tentando parar o backend Node.js...")
        try:
            node_process.terminate()
            node_process.wait(timeout=5)
            print("✅ Backend Node.js parado.")
        except subprocess.TimeoutExpired:
            print("⚠️ Backend Node.js não respondeu ao terminate, forçando parada...")
            node_process.kill()
            node_process.wait()
            print("✅ Backend Node.js forçado a parar.")
        except Exception as e:
            print(f"❌ Erro ao parar o backend Node.js: {e}")
    else:
        print("Backend Node.js não estava rodando ou já parou.")

# Register the cleanup function to be called on exit
atexit.register(stop_nodejs_backend)

def run_bot_scanning():
    """Função para rodar o scan de mercado do bot periodicamente."""
    scan_interval_seconds = 60 * 5  # Scan a cada 5 minutos
    while True:
        try:
            print("\n--- Executando scan de mercado do bot ---")
            bot.analyzer.scan_market(verbose=True)
            print("--- Scan de mercado concluído ---")
        except Exception as e:
            print(f"❌ Erro durante o scan de mercado do bot: {e}")
            traceback.print_exc()
        time.sleep(scan_interval_seconds)

class KryptonBot:
    def __init__(self):
        # Usar PostgreSQL em produção, CSV em desenvolvimento
        environment = os.getenv('FLASK_ENV', 'development')
        if environment == 'production' and os.getenv('DATABASE_URL'):
            print("🗄️ Usando PostgreSQL em produção")
            self.db_config = DatabaseConfig()
            # Para compatibilidade, ainda usar Database para métodos específicos
            self.db = Database()
        else:
            print("🗄️ Usando CSV em desenvolvimento")
            self.db = Database()
            self.db_config = None
        
        self.analyzer = TechnicalAnalysis(self.db)
        self.notifier = TelegramNotifier()
        self.gerenciador_sinais = GerenciadorSinais(self.db)

def wait_for_database():
    """Aguarda o PostgreSQL estar disponível"""
    import time
    max_retries = 30
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            from core.db_config import DatabaseConfig
            db_config = DatabaseConfig()
            with db_config.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    print("✅ PostgreSQL conectado com sucesso!")
                    return True
        except Exception as e:
            retry_count += 1
            print(f"⏳ Aguardando PostgreSQL... tentativa {retry_count}/{max_retries}: {e}")
            time.sleep(2)
    
    print("❌ Falha ao conectar com PostgreSQL após 30 tentativas")
    return False

if __name__ == '__main__':
    try:
        print("🚀 Iniciando aplicação...")
        
        # Aguardar PostgreSQL em produção
        environment = os.getenv('FLASK_ENV', 'development')
        if environment == 'production' and os.getenv('DATABASE_URL'):
            print("🗄️ Aguardando PostgreSQL...")
            if not wait_for_database():
                print("❌ Falha ao conectar com PostgreSQL. Encerrando...")
                sys.exit(1)
        
        # Inicializar o bot ANTES de usar
        print("🤖 Inicializando KryptonBot...")
        try:
            bot = KryptonBot()
            print("✅ KryptonBot inicializado com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao inicializar KryptonBot: {e}")
            traceback.print_exc()
            sys.exit(1)
        
        # Configurar logging
        server.logger.setLevel(logging.DEBUG)
        if not server.logger.handlers:
            handler = logging.StreamHandler()
            handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            server.logger.addHandler(handler)

        # Verificar e atualizar credenciais do Telegram
        with server.app_context():
            db_instance = Database()
            current_db_token = db_instance.get_config_value('telegram_token')
            current_db_chat_id = db_instance.get_config_value('telegram_chat_id')
            
            config_token = cast(str, server.config.get('TELEGRAM_TOKEN', ''))
            config_chat_id = cast(str, server.config.get('TELEGRAM_CHAT_ID', ''))
            
            if not current_db_token or not current_db_chat_id or \
               current_db_token != config_token or current_db_chat_id != config_chat_id:
                print("ℹ️ Credenciais do Telegram em config.py diferem do DB ou estão faltando. Tentando salvar/atualizar...")
                if bot.notifier.setup_credentials(config_token, config_chat_id):
                    print("✅ Credenciais do Telegram salvas/atualizadas no DB com sucesso.")
                else:
                    print("❌ Falha ao salvar/atualizar credenciais do Telegram no DB.")
            else:
                print("✅ Credenciais do Telegram no DB estão atualizadas com config.py.")

        # Iniciar backend Node.js
        # start_nodejs_backend()

        # Usar a app configurada do api.py
        try:
            print("🌐 Usando aplicação Flask do api.py...")
            from api import app
            print("✅ Aplicação Flask obtida com sucesso!")
            
            # Register API routes (APENAS UMA VEZ)
            print("🔗 Registrando rotas da API...")
            register_api_routes(app, bot)
            print("✅ Rotas da API registradas com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao configurar aplicação Flask: {e}")
            traceback.print_exc()
            sys.exit(1)
        
        # Iniciar monitoramento em thread separada APÓS o Flask estar pronto
        def start_background_tasks():
            time.sleep(2)  # Aguardar Flask inicializar
            print("🚀 Iniciando monitoramento de mercado...")
            monitor_thread = threading.Thread(target=bot.analyzer.start_monitoring, daemon=True)
            monitor_thread.start()
            
            # Configurar agendador de limpeza automática
            print("🕐 Configurando agendador de limpeza automática...")
            scheduler = setup_market_scheduler(bot.db, bot.gerenciador_sinais)
        
        # Iniciar tarefas em background
        background_thread = threading.Thread(target=start_background_tasks, daemon=True)
        background_thread.start()
        
        print("🚀 Iniciando servidor Flask...")
        try:
            flask_port = int(os.getenv('FLASK_PORT', 5000))
            print(f"🌐 Servidor Flask iniciando na porta {flask_port}...")
            print(f"🔍 Ambiente: {os.getenv('FLASK_ENV', 'development')}")
            print(f"🔍 Debug: {os.getenv('FLASK_DEBUG', 'False')}")
            print("✅ Todas as configurações carregadas com sucesso!")
            app.run(debug=False, host='0.0.0.0', port=flask_port, use_reloader=False)
        except Exception as e:
            print(f"❌ Erro ao iniciar servidor Flask: {e}")
            traceback.print_exc()
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Aplicação interrompida pelo usuário")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 ERRO CRÍTICO NA INICIALIZAÇÃO: {e}")
        traceback.print_exc()
        sys.exit(1)