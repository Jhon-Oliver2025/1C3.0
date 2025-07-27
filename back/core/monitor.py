import threading
import time
import os
import traceback  # Add traceback import
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Union
from binance.client import Client
from colorama import Fore, Style, init
from tabulate import tabulate
from tqdm import tqdm
from .database import Database
from .technical_analysis import TechnicalAnalysis
from .telegram_notifier import TelegramNotifier
from .gerenciar_sinais import GerenciadorSinais
from threading import Thread
import pandas as pd  # Adicione esta linha no topo do arquivo junto com os outros imports

# Initialize colorama
init()

class Monitor(Thread):
    VERSION = "7.6.0"

    def __init__(self, db_instance: Database):
        super().__init__()
        print("\n" + "="*70)
        print(f"🤖 Iniciando K-10 Bot v{self.VERSION}")
        print("="*70)

        # Use a instância do banco de dados que foi passada para o construtor
        self.db = db_instance
        # Passe a instância do banco de dados para o GerenciadorSinais
        self.gerenciador = GerenciadorSinais(self.db)

        from config import server

        # --- Início da Edição ---
        # Passar a instância do banco de dados para TechnicalAnalysis
        self.analyzer = TechnicalAnalysis(self.db)
        # --- Fim da Edição ---

        self.binance = Client()
        self.check_interval = 60
        self._monitor_running = True
        self._is_running = False
        self.daemon = True

        # Get Telegram credentials from config
        telegram_token = server.config.get('TELEGRAM_TOKEN')
        telegram_chat_id = server.config.get('TELEGRAM_CHAT_ID')

        self.notifier = TelegramNotifier(telegram_token, telegram_chat_id)
        if self.notifier.test_connection():
            print("✅ Telegram configurado com sucesso!")
        else:
            print("⚠️ Aviso: Telegram não configurado corretamente")
            # Remover a linha self.notifier = None  # Este é o problema principal

        self.stats = {
            'wins': 0,
            'losses': 0,
            'total_pairs': 0
        }
        print("✅ Sistema inicializado com sucesso!\n")

    def get_current_price(self, symbol: str) -> Optional[float]:
        """Obtém o preço atual de um par"""
        try:
            ticker = self.binance.futures_symbol_ticker(symbol=symbol)
            return float(ticker['price'])
        except Exception as e:
            print(f"❌ Erro ao buscar preço de {symbol}: {e}")
            return None

    def calcular_variacao(self, entrada: float, atual: float, tipo: str) -> float:
        """Calcula a variação percentual do preço"""
        if tipo.upper() == 'LONG':
            return ((atual - entrada) / entrada) * 100
        return ((entrada - atual) / entrada) * 100

    def monitor_loop(self):
        """Loop principal de monitoramento"""
        try:
            sinais_abertos = self.gerenciador.processar_sinais_abertos()
            if not sinais_abertos.empty:
                print("\n[MONITOR] 📊 MONITORAMENTO DE SINAIS ATIVOS")
                print("="*50)
                table_data = []
                for _, sinal in sinais_abertos.iterrows():
                    try:
                        symbol = str(sinal['symbol'])
                        preco_atual = self.get_current_price(symbol)
                        if not preco_atual:
                            continue

                        entry_time = pd.to_datetime(sinal['entry_time'])
                        horas_ativas = (datetime.now() - entry_time).total_seconds() / 3600

                        variacao = self.calcular_variacao(
                            float(sinal['entry_price']),
                            preco_atual,
                            str(sinal['type'])
                        )

                        cor = Fore.GREEN if variacao > 0 else Fore.RED
                        table_data.append([
                            f"{Fore.CYAN}{symbol}{Style.RESET_ALL}",
                            f"{Fore.YELLOW}{sinal['type']}{Style.RESET_ALL}",
                            f"{cor}{variacao:+.2f}%{Style.RESET_ALL}",
                            f"{Fore.WHITE}{horas_ativas:.1f}h{Style.RESET_ALL}"
                        ])

                    except Exception as e:
                        print(f"❌ Erro ao processar sinal: {e}")
                        continue

                if table_data:
                    print(tabulate(
                        table_data,
                        headers=[
                            f'{Fore.CYAN}Par{Style.RESET_ALL}',
                            f'{Fore.YELLOW}Tipo{Style.RESET_ALL}',
                            f'{Fore.WHITE}Variação{Style.RESET_ALL}',
                            f'{Fore.WHITE}Tempo{Style.RESET_ALL}'
                        ],
                        tablefmt='grid'
                    ))
                print("="*50 + "\n")
            else:
                print("[INFO] Nenhum sinal ativo para monitorar")
            
            # --- Início da Edição ---
            # REMOVIDO: O loop de sleep foi movido para o método run()
            # for _ in range(self.check_interval):
            #     if not self._monitor_running:
            #         break
            #     time.sleep(1)
            # --- Fim da Edição ---
                
        except Exception as e:
            print(f"[ERROR] ❌ Erro no loop de monitoramento: {e}")
            print(f"[TRACE] {traceback.format_exc()}")
            # --- Início da Edição ---
            # Tornar este sleep também interrompível
            for _ in range(5): # Dorme por 5 segundos, verificando a flag a cada segundo
                if not self._monitor_running:
                    break
                time.sleep(1)
            # --- Fim da Edição ---

    def run(self):
        """Método principal que executa o monitoramento"""
        try:
            print(f"{Fore.GREEN}✨ Monitor iniciado com sucesso{Style.RESET_ALL}")
            
            while True:
                try:
                    # Executar análise técnica (usando analyzer ao invés de technical_analysis)
                    self.analyzer.scan_market()
                    
                    # Processar sinais abertos (usando gerenciador ao invés de gerenciador_sinais)
                    self.gerenciador.processar_sinais_abertos()
                    
                    # Aguardar 5 minutos antes da próxima verificação
                    print(f"\n⏳ Aguardando próxima verificação...")
                    time.sleep(300)  # 5 minutos
                    
                except Exception as e:
                    print(f"{Fore.RED}❌ Erro durante monitoramento: {e}{Style.RESET_ALL}")
                    traceback.print_exc()
                    time.sleep(60)  # Aguarda 1 minuto antes de tentar novamente
                    
        except KeyboardInterrupt:
            print(f"{Fore.YELLOW}⚠️ Monitoramento interrompido pelo usuário{Style.RESET_ALL}")
        """Método principal da thread"""
        print("\n" + "="*70)
        print(f"🚀 INICIANDO MONITORAMENTO DE MERCADO - v{self.VERSION}")
        print("="*70)
        self._is_running = True
        
        # Variável para controlar se a limpeza diária já foi feita hoje
        self._last_cleanup_day = None
        
        while self._monitor_running:
            try:
                print("\n" + "="*70)
                now = datetime.now()
                print(f"⏰ {now.strftime('%d/%m/%Y %H:%M:%S')}")
                print(f"[INFO] 🔄 Iniciando novo ciclo de verificação")
                print("="*70)
                
                # Verificar se é hora de fazer a limpeza diária (próximo da meia-noite)
                # Executa a limpeza entre 00:00 e 00:05
                if now.hour == 0 and now.minute < 5 and self._last_cleanup_day != now.date():
                    print("\n[CLEANUP] 🧹 Executando limpeza diária de sinais abertos do dia anterior...")
                    self.gerenciador.limpar_sinais_abertos_do_dia_anterior()
                    self._last_cleanup_day = now.date()
                    print("[CLEANUP] ✅ Limpeza diária concluída.")
                
                print("\n[SCAN] 📡 Escaneando mercado...")
                novos_sinais = self.analyzer.scan_market(verbose=True)
                
                if novos_sinais:
                    print(f"\n[ALERT] ✨ {len(novos_sinais)} NOVOS SINAIS ENCONTRADOS!")
                    print("-"*40)
                    for sinal in novos_sinais:
                        print(f"[SIGNAL] 📊 {sinal['symbol']} - {sinal['type']} @ {sinal['entry_price']}")
                        if self.notifier:
                            self.notifier.send_signal(
                                sinal['symbol'],
                                sinal['type'],
                                float(sinal['entry_price']),
                                sinal.get('quality_score', 0),
                                sinal.get('entry_timeframe', '4h'),
                                sinal.get('target_price')
                            )
                    print("-"*40)
                else:
                    print("[INFO] Nenhum novo sinal encontrado")
                
                self.monitor_loop() # Esta chamada agora NÃO tem sleep interno
                
                print("\n[WAIT] ⏳ AGUARDANDO PRÓXIMO CICLO")
                print(f"[INFO] ⏰ Próxima verificação em {self.check_interval} segundos")
                print("="*70)
                
                # --- Início da Edição ---
                # Este é o ÚNICO loop de espera principal, e ele é interrompível
                for i in range(self.check_interval, 0, -1):
                    if not self._monitor_running:
                        break
                    print(f"\r⌛ Aguardando: {i:3d}s", end="")
                    time.sleep(1)
                print("\r" + " "*50, end="") # Limpa a linha após o loop, mesmo que interrompido
                # --- Fim da Edição ---
                
            except Exception as e:
                print(f"\n❌ ERRO NO CICLO: {e}")
                if not self._monitor_running:
                    break
                # --- Início da Edição ---
                # Tornar este sleep também interrompível
                for _ in range(5): # Dorme por 5 segundos, verificando a flag a cada segundo
                    if not self._monitor_running:
                        break
                    time.sleep(1)
                # --- Fim da Edição ---
        
        print("\n" + "="*70)
        print("✅ MONITORAMENTO ENCERRADO")
        print("="*70 + "\n")

    def stop(self):
        """Para o monitoramento"""
        print("🛑 Parando monitoramento...")
        self._monitor_running = False
        self._is_running = False
        # --- Início da Edição ---
        # REMOVIDO: A chamada join() deve ser feita pela thread que chama stop()
        # if self.is_alive():
        #     self.join(timeout=2)
        # --- Fim da Edição ---

# --- Início da Edição ---
# Modificar a função start_monitoring para aceitar db_instance
def start_monitoring(db_instance: Database):
    """Função para iniciar o monitoramento em background"""
    try:
        # Passar a instância db ao criar o Monitor
        monitor = Monitor(db_instance)
        monitor.start()  # Inicia a thread
        print("✅ Monitoramento iniciado com sucesso!")
        return monitor
    except Exception as e:
        print(f"❌ Erro ao iniciar monitoramento: {e}")
        return None
# --- Fim da Edição ---


if __name__ == "__main__":
    # --- Início da Edição ---
    # Se você executa Monitor.py diretamente (python core/monitor.py),
    # você precisa criar uma instância de Database aqui para passar para Monitor.
    # Se você sempre executa index.py, esta seção __main__ em Monitor.py
    # pode ser removida ou modificada para fins de teste.
    # Exemplo para teste:
    test_db = Database() # Criar instância do Database
    monitor = Monitor(test_db) # Passar a instância db
    monitor.start()
    # --- Fim da Edição ---

# --- Início da Edição ---
# Adicionar esta linha no final do arquivo para exportar a classe Monitor (manter)
__all__ = ['Monitor']
# --- Fim da Edição ---