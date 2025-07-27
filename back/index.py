import threading
import sys
import subprocess
import atexit
import os
import logging # Adicione esta importação
import time
import traceback # Adicione esta importação
from dotenv import load_dotenv # Adicione esta linha

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Importar componentes e módulos necessários
from config import server # Importa o servidor Flask
from api import register_api_routes # Adicione esta linha para importar o módulo api

# Importar a instância global do bot de app.py
from app import bot

# Global variable to hold the Node.js process
node_process = None

def start_nodejs_backend():
    """Inicia o servidor Node.js em segundo plano."""
    global node_process
    print("🚀 Tentando iniciar o backend Node.js...")
    try:
        # Define o caminho para o diretório do backend Node.js
        # Assumindo que server.js está no mesmo diretório de index.py
        nodejs_dir = os.path.dirname(os.path.abspath(__file__))

        # Cria uma cópia das variáveis de ambiente atuais
        # Isso é importante para herdar outras variáveis de ambiente necessárias
        env_for_nodejs = os.environ.copy()
        # Define explicitamente a porta para o processo Node.js
        # Isso irá sobrescrever qualquer variável PORT herdada e garantir que o Node.js use 5001
        env_for_nodejs['PORT'] = '5001'
        
        # Comando para iniciar o servidor Node.js
        # No Windows, 'node' deve estar no PATH.
        # Usamos creationflags para criar um novo grupo de processo no Windows,
        # o que ajuda no tratamento de Ctrl+C para o processo Python sem matar o Node.js imediatamente.
        node_process = subprocess.Popen(
            ['node', 'server.js'],
            cwd=nodejs_dir,
            stdout=subprocess.PIPE, # Descomente para capturar a saída do Node.js
            stderr=subprocess.PIPE, # Descomente para capturar erros do Node.js
            env=env_for_nodejs, # Passa o ambiente personalizado para o subprocesso
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
        )
        print(f"✅ Backend Node.js iniciado com PID: {node_process.pid}")
        # Adicionar um thread para ler a saída do Node.js
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
    if node_process and node_process.poll() is None: # Verifica se o processo está rodando
        print("🛑 Tentando parar o backend Node.js...")
        try:
            # Tenta terminar o processo de forma graciosa
            node_process.terminate()
            node_process.wait(timeout=5) # Espera até 5 segundos para o processo terminar
            print("✅ Backend Node.js parado.")
        except subprocess.TimeoutExpired:
            print("⚠️ Backend Node.js não respondeu ao terminate, forçando parada...")
            node_process.kill() # Força a parada se não terminar
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
    scan_interval_seconds = 60 * 5 # Scan a cada 5 minutos (300 segundos), ajuste conforme necessário
    while True:
        try:
            print("\n--- Executando scan de mercado do bot ---")
            bot.analyzer.scan_market(verbose=True) # Chama o método de scan do analyzer
            print("--- Scan de mercado concluído ---")
        except Exception as e:
            print(f"❌ Erro durante o scan de mercado do bot: {e}")
            traceback.print_exc() # Para depuração
        time.sleep(scan_interval_seconds)

if __name__ == '__main__':
    # Configure o nível de log para DEBUG para o aplicativo Flask
    server.logger.setLevel(logging.DEBUG)
    # Opcional: Adicione um handler para garantir que as mensagens sejam exibidas no console
    # Isso é útil se você não estiver vendo logs mesmo com o nível DEBUG
    if not server.logger.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        server.logger.addHandler(handler)

    # Inicia o backend Node.js primeiro
    start_nodejs_backend()

    # Inicia o scan de mercado do bot em uma thread separada
    bot_scan_thread = threading.Thread(target=run_bot_scanning, daemon=True)
    bot_scan_thread.start()
    print("✅ Thread de scan de mercado do bot iniciada.")

    # Registra as rotas da API Flask
    register_api_routes(server, bot)

    # Inicia o servidor Flask
    print("🚀 Iniciando servidor Flask...")
    server.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)