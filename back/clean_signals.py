import os
import sys
import pandas as pd
from datetime import datetime

# Adicionar o diretório raiz do projeto ao PATH
project_root = os.path.dirname(__file__)
sys.path.append(project_root)

from core.database import Database

def clear_signals_from_database(db_instance, status_to_clear=None):
    """
    Limpa sinais diretamente do banco de dados (arquivo CSV).
    Se status_to_clear for None, limpa todos os sinais.
    Se for 'CLOSED' ou 'OPEN', limpa apenas sinais com esse status.
    """
    try:
        # Obter todos os sinais
        signals = db_instance.get_all_signals()
        
        if not signals:
            print("📭 Nenhum sinal encontrado para limpar.")
            return
        
        initial_count = len(signals)
        signals_to_keep = []
        
        if status_to_clear is None:
            # Limpar todos os sinais
            signals_to_keep = []
            print("🧹 Limpando TODOS os sinais...")
        elif status_to_clear.upper() == 'CLOSED':
            # Manter apenas sinais que NÃO são 'CLOSED'
            signals_to_keep = [s for s in signals if s.get('status') != 'CLOSED']
            print("🧹 Limpando sinais com status 'CLOSED'...")
        elif status_to_clear.upper() == 'OPEN':
            # Manter apenas sinais que NÃO são 'OPEN'
            signals_to_keep = [s for s in signals if s.get('status') != 'OPEN']
            print("🧹 Limpando sinais com status 'OPEN'...")
        else:
            print(f"⚠️ Status '{status_to_clear}' inválido para limpeza. Use 'CLOSED', 'OPEN' ou deixe vazio para limpar todos.")
            return
        
        # Criar DataFrame com os sinais que devem ser mantidos
        if signals_to_keep:
            df_to_keep = pd.DataFrame(signals_to_keep)
        else:
            # Criar DataFrame vazio com as colunas corretas
            df_to_keep = pd.DataFrame({
                'symbol': [],
                'type': [],
                'entry_price': [],
                'entry_time': [],
                'target_price': [],
                'projection_percentage': [],
                'signal_class': [],
                'status': []
            })
        
        # Salvar diretamente no arquivo CSV do banco de dados
        signals_file = db_instance.signals_list_file
        df_to_keep.to_csv(signals_file, index=False)
        
        cleaned_count = initial_count - len(signals_to_keep)
        print(f"✅ Limpeza concluída. {cleaned_count} sinais removidos.")
        print(f"📊 Sinais restantes: {len(signals_to_keep)}")
        
    except Exception as e:
        print(f"❌ Erro ao limpar sinais: {e}")
        import traceback
        traceback.print_exc()

def show_current_signals(db_instance):
    """Mostra os sinais atuais antes da limpeza."""
    signals = db_instance.get_all_signals()
    
    if not signals:
        print("📭 Nenhum sinal encontrado.")
        return
    
    print(f"📊 Sinais atuais ({len(signals)} total):")
    
    # Contar por status
    status_count = {}
    for signal in signals:
        status = signal.get('status', 'N/A')
        status_count[status] = status_count.get(status, 0) + 1
    
    for status, count in status_count.items():
        print(f"   {status}: {count} sinais")
    print()

def main():
    print("=== Ferramenta de Limpeza de Sinais (Banco de Dados) ===")
    print()
    
    # Criar instância do banco de dados
    db_instance = Database()
    
    # Mostrar sinais atuais
    show_current_signals(db_instance)
    
    print("Escolha o tipo de sinais para limpar:")
    print("1. Todos os sinais")
    print("2. Apenas sinais 'CLOSED'")
    print("3. Apenas sinais 'OPEN'")
    print("4. Ver sinais detalhados")
    print("5. Cancelar")
    print()
    
    choice = input("Digite o número da sua escolha: ")
    
    if choice == '1':
        confirm = input("⚠️ Tem certeza que deseja limpar TODOS os sinais? (s/N): ")
        if confirm.lower() == 's':
            clear_signals_from_database(db_instance, status_to_clear=None)
        else:
            print("Operação cancelada.")
    elif choice == '2':
        clear_signals_from_database(db_instance, status_to_clear='CLOSED')
    elif choice == '3':
        clear_signals_from_database(db_instance, status_to_clear='OPEN')
    elif choice == '4':
        # Importar e executar o visualizador
        try:
            from view_signals import main as view_main
            view_main()
        except ImportError:
            print("❌ Arquivo view_signals.py não encontrado. Execute-o separadamente.")
    elif choice == '5':
        print("Operação cancelada.")
    else:
        print("Escolha inválida.")

if __name__ == "__main__":
    main()