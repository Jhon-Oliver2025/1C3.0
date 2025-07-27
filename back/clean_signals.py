import os
import sys

# Adicionar o diretório raiz do projeto ao PATH para importar core.gerenciar_sinais e config
# Assumindo que clean_signals.py está no diretório raiz
project_root = os.path.dirname(__file__)
sys.path.append(project_root)

from core.gerenciar_sinais import GerenciadorSinais
# --- Início da Edição ---
# Importar a classe Database
from core.database import Database
# --- Fim da Edição ---

def main():
    print("=== Ferramenta de Limpeza de Sinais ===")
    print("Escolha o tipo de sinais para limpar:")
    print("1. Todos os sinais")
    print("2. Apenas sinais 'CLOSED'")
    print("3. Apenas sinais 'OPEN'")
    print("4. Cancelar")

    choice = input("Digite o número da sua escolha: ")

    # --- Início da Edição ---
    # Criar uma instância do banco de dados
    db_instance = Database()
    # Passar a instância do banco de dados para o GerenciadorSinais
    gerenciador = GerenciadorSinais(db_instance)
    # --- Fim da Edição ---

    if choice == '1':
        gerenciador.clear_signals(status_to_clear=None)
    elif choice == '2':
        gerenciador.clear_signals(status_to_clear='CLOSED')
    elif choice == '3':
        gerenciador.clear_signals(status_to_clear='OPEN')
    elif choice == '4':
        print("Operação cancelada.")
    else:
        print("Escolha inválida.")

if __name__ == "__main__":
    main()