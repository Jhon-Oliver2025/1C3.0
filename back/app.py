# System imports
from dotenv import load_dotenv
import os
import sys
import subprocess
import atexit

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()
import threading
import time
import pytz
import pandas as pd
from datetime import datetime, timedelta
import cryptocompare
import traceback
import signal # Add this line
# REMOVIDO: from dash.exceptions import PreventUpdate

# REMOVIDO: Flask and Dash imports
# from flask_login import login_required, current_user
from config import server # Descomente esta linha
# from dash import Dash, html, dcc, dash_table, ALL
# from dash.dependencies import Input, Output, State
# import dash_bootstrap_components as dbc # Adicionar esta linha

# Core components
from core.database import Database
from core.technical_analysis import TechnicalAnalysis
from core.telegram_notifier import TelegramNotifier
from core.monitor import Monitor
from core.gerenciar_sinais import GerenciadorSinais

# Importar as rotas da API
import api # Adicione esta linha

# REMOVIDO: UI components
# from ui.components.signals_container import create_signals_container
# REMOVIDO: Importar a função de registro de callbacks do dashboard
# from pages.dashboard import create_dashboard_layout, register_dashboard_callbacks


class KryptonBot:
    def __init__(self):
        # Inicializar Database primeiro
        self.db = Database()
        # Agora passe a instância do banco de dados para as outras classes
        self.gerenciador = GerenciadorSinais(self.db)
        self.analyzer = TechnicalAnalysis(self.db)

        # Pegando credenciais do config
        from config import server
        telegram_token = server.config.get('TELEGRAM_TOKEN')
        telegram_chat_id = server.config.get('TELEGRAM_CHAT_ID')
        self.notifier = TelegramNotifier(telegram_token, telegram_chat_id)

        # O erro na linha 42 para Monitor indica que ele também precisa da instância do DB.
        # A inicialização do Monitor não está neste snippet, mas você precisará
        # encontrar onde Monitor() é chamado em app.py (provavelmente em um bloco principal
        # ou outra função) e passá-lo a instância do DB:
        # self.monitor = Monitor(self.db) # Exemplo de como deve ser a chamada
        # REMOVIDO: Inicialização do TickerComponent
        # self.ticker = TickerComponent()
        # Pass the database instance to the Monitor
        self.monitor = Monitor(self.db) # <-- Modify this line

        # Configurando logger
        import logging
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        self._cleanup_handler = None

    def send_all_today_signals(self):
        """Envia todos os sinais do dia para o Telegram"""
        try:
            # Pega os sinais do dia
            today = datetime.now().strftime('%Y-%m-%d')
            signals_df = self.gerenciador.processar_sinais_abertos()  # Corrigido para usar o método correto
            # Filtrar por data no DataFrame, não na string
            today_signals = signals_df[signals_df['entry_time'].dt.date == datetime.now().date()]

            if today_signals.empty:
                self.logger.info("Nenhum sinal encontrado para hoje")
                return

            self.logger.info(f"Enviando {len(today_signals)} sinais para o Telegram")

            # Envia cada sinal
            for _, signal in today_signals.iterrows():
                timeframe = signal.get('timeframe')
                if timeframe is None:
                    timeframe = '4h'  # valor padrão se não existir

                # Obtém o quality_score
                raw_quality_score = signal.get('quality_score')
                quality_score_float = 0.0 # Default value

                # --- Início da Edição ---
                # Check if the value is not None and not NaN before attempting conversion
                # Explicitly check for None and use pd.isna for NaN
                if raw_quality_score is not None and pd.notna(raw_quality_score):
                    try:
                        # Attempt to convert to float
                        quality_score_float = float(raw_quality_score) # Erro na linha 100
                    except (ValueError, TypeError):
                        # If conversion fails, keep the default 0.0 and log a warning
                        self.logger.warning(f"Invalid quality_score received for {signal.get('symbol')}: {raw_quality_score}. Using default 0.0.")
                # Else: If it's NaN or None, the default 0.0 is already set
                # --- Fim da Edição ---

                # Get and validate entry_price
                raw_entry_price = signal.get('entry_price')
                entry_price_float = 0.0 # Default value

                # --- Início da Edição ---
                # Check if the value is not None and not NaN before attempting conversion
                # Explicitly check for None and use pd.isna for NaN
                if raw_entry_price is not None and pd.notna(raw_entry_price):
                     try:
                         entry_price_float = float(raw_entry_price) # Erro na linha 112
                     except (ValueError, TypeError):
                         self.logger.warning(f"Invalid entry_price received for {signal.get('symbol')}: {raw_entry_price}. Using default 0.0.")
                # Else: If it's NaN or None, the default 0.0 is already set
                # --- Fim da Edição ---

                # Envia o sinal usando os valores tratados
                self.notifier.send_signal(
                    symbol=signal['symbol'],
                    signal_type=signal['type'],
                    price=entry_price_float, # Use the treated float value
                    quality_score=quality_score_float, # Use the treated float value
                    timeframe=str(timeframe)
                )
                time.sleep(1)

            self.logger.info("✅ Todos os sinais foram enviados com sucesso")

        except Exception as e:
            self.logger.error(f"❌ Erro ao enviar sinais: {e}")

    def test_telegram(self):
        """Testa a conexão com o Telegram"""
        try:
            result = self.notifier.test_connection()
            if result:
                self.logger.info("✅ Conexão com Telegram estabelecida com sucesso")
            else:
                self.logger.error("❌ Falha ao conectar com Telegram")

        except Exception as e:
            self.logger.error(f"❌ Erro ao testar conexão com Telegram: {e}")

    def initialize(self):
        """Inicializa o bot e seus componentes."""
        try:
            # Exemplo de inicialização de componentes
            # self.db.connect() # Se houver um método de conexão explícito
            # self.analyzer.load_data() # Se houver dados a carregar
            self.logger.info("KryptonBot inicializado com sucesso.")
            return True
        except Exception as e:
            self.logger.error(f"❌ Erro na inicialização do KryptonBot: {e}")
            return False

    def cleanup(self, signum, frame):
        """Lida com o encerramento do bot."""
        self.logger.info("Recebido sinal de encerramento. Iniciando limpeza...")
        # Altera is_running() para is_alive()
        if self.monitor and self.monitor.is_alive(): # Chamar is_alive() como método
            self.monitor.stop()
            # --- Início da Edição ---
            # Adicionar um timeout ao join() para evitar bloqueio indefinido
            self.monitor.join(timeout=5) # Espera a thread de monitoramento terminar por no máximo 5 segundos
            # --- Fim da Edição ---
            self.logger.info("Monitoramento parado.")
        # Adicione aqui qualquer outra lógica de limpeza necessária
        self.logger.info("Limpeza concluída. Encerrando aplicação.")
        sys.exit(0)

    def register_cleanup_handler(self):
        """Registra o handler de limpeza para sinais de encerramento."""
        self._cleanup_handler = self.cleanup
        signal.signal(signal.SIGINT, self._cleanup_handler)
        signal.signal(signal.SIGTERM, self._cleanup_handler)

    def check_system_status(self):
        """Verifica status de todos os componentes"""
        # --- Início da Edição ---
        # Chamar is_alive() como método
        monitor_alive = hasattr(self.monitor, 'is_alive') and self.monitor.is_alive()
        # --- Fim da Edição ---
        return {
            'sinais_file': os.path.exists('sinais_lista.csv'),
            'monitor': monitor_alive,
            # REMOVIDO: Verificação do ticker
            # 'ticker': bool(self.ticker and self.ticker.client),
            # Removido a chamada para check_connection que não existe
            'database': True # Assume que a instância do DB foi criada com sucesso
        }

# Instância global do bot
bot = KryptonBot()

# --- LÓGICA DE INICIALIZAÇÃO MOVIDA DE INDEX.PY ---

# Variável global para o processo Node.js
node_process = None

def start_nodejs_backend():
    """Inicia o servidor Node.js em segundo plano."""
    global node_process
    print("🚀 Tentando iniciar o backend Node.js...")
    try:
        nodejs_dir = os.path.dirname(os.path.abspath(__file__))
        env_for_nodejs = os.environ.copy()
        env_for_nodejs['PORT'] = '5001'
        
        node_process = subprocess.Popen(
            ['node', 'server.js'],
            cwd=nodejs_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env_for_nodejs,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
        )
        print(f"✅ Backend Node.js iniciado com PID: {node_process.pid}")
        
        def read_nodejs_output(pipe, prefix):
            for line in iter(pipe.readline, b''):
                print(f"[{prefix}] {line.decode().strip()}")
            pipe.close()

        threading.Thread(target=read_nodejs_output, args=(node_process.stdout, "NODE_OUT"), daemon=True).start()
        threading.Thread(target=read_nodejs_output, args=(node_process.stderr, "NODE_ERR"), daemon=True).start()
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

atexit.register(stop_nodejs_backend)

def run_bot_scanning():
    """Função para rodar o scan de mercado do bot periodicamente."""
    scan_interval_seconds = 60 * 5
    while True:
        try:
            print("\n--- Executando scan de mercado do bot ---")
            bot.analyzer.scan_market(verbose=True)
            print("--- Scan de mercado concluído ---")
        except Exception as e:
            print(f"❌ Erro durante o scan de mercado do bot: {e}")
            traceback.print_exc()
        time.sleep(scan_interval_seconds)

if __name__ == '__main__':
    import logging
    # --- Início da Edição ---
    from typing import cast # Adicionar esta importação
    # --- Fim da Edição ---
    server.logger.setLevel(logging.DEBUG)
    if not server.logger.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        server.logger.addHandler(handler)

    # Garante que as credenciais do Telegram de config.py sejam salvas/atualizadas no banco de dados
    with server.app_context():
        db_instance = Database() # Obtém uma nova instância do DB para este contexto
        current_db_token = db_instance.get_config_value('telegram_token')
        current_db_chat_id = db_instance.get_config_value('telegram_chat_id')

        # --- Início da Edição ---
        # Garante que os valores são strings, mesmo que server.config.get retorne None
        config_token = cast(str, server.config.get('TELEGRAM_TOKEN', ''))
        config_chat_id = cast(str, server.config.get('TELEGRAM_CHAT_ID', ''))
        # --- Fim da Edição ---

        if not current_db_token or not current_db_chat_id or \
           current_db_token != config_token or current_db_chat_id != config_chat_id:
            print("ℹ️ Credenciais do Telegram em config.py diferem do DB ou estão faltando. Tentando salvar/atualizar...")
            if bot.notifier.setup_credentials(config_token, config_chat_id):
                print("✅ Credenciais do Telegram salvas/atualizadas no DB com sucesso.")
            else:
                print("❌ Falha ao salvar/atualizar credenciais do Telegram no DB.")
        else:
            print("✅ Credenciais do Telegram no DB estão atualizadas com config.py.")
    # --- Fim da Edição ---

    start_nodejs_backend()

    bot_scan_thread = threading.Thread(target=run_bot_scanning, daemon=True)
    bot_scan_thread.start()
    print("✅ Thread de scan de mercado do bot iniciada.")

    api.register_api_routes(server, bot)

    print("🚀 Iniciando servidor Flask...")
    # Usar a porta do .env ou 5000 como padrão
    flask_port = int(os.getenv('FLASK_PORT', 5000))
    server.run(debug=True, host='0.0.0.0', port=flask_port, use_reloader=False)


@server.route('/api/chat', methods=['POST']) # MODIFIED: Changed 'app' to 'server'
def chat():
    pass

# Inicializar componentes principais
db = Database()
technical_analysis = TechnicalAnalysis(db)
telegram_notifier = TelegramNotifier()

# Criar instância do Monitor e iniciar
monitor = Monitor(db)
monitor.start()  # Inicia o monitoramento em uma thread separada
