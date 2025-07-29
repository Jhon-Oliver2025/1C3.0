import os
import sys
from datetime import datetime

# Adicionar o diretório raiz do projeto ao PATH
project_root = os.path.dirname(__file__)
sys.path.append(project_root)

from core.database import Database

def format_signal_display(signal):
    """Formata um sinal para exibição."""
    entry_time = signal.get('entry_time', 'N/A')
    if entry_time != 'N/A':
        try:
            dt = datetime.strptime(entry_time, '%Y-%m-%d %H:%M:%S')
            entry_time = dt.strftime('%d/%m/%Y %H:%M')
        except:
            pass
    
    return f"""
┌─────────────────────────────────────────────────────────────┐
│ 🪙 {signal.get('symbol', 'N/A'):<15} │ 📊 {signal.get('type', 'N/A'):<8} │ ⭐ {signal.get('signal_class', 'N/A'):<8} │
│ 💰 Entrada: {signal.get('entry_price', 'N/A'):<12} │ 🎯 Alvo: {signal.get('target_price', 'N/A'):<12} │
│ 📈 Projeção: {signal.get('projection_percentage', 'N/A'):<8}% │ 🔄 Status: {signal.get('status', 'N/A'):<8} │
│ 📅 Data: {entry_time:<20} │
└─────────────────────────────────────────────────────────────┘"""

def main():
    print("=== Visualizador de Sinais do Banco de Dados ===")
    print()
    
    # Criar instância do banco de dados
    db = Database()
    
    # Obter todos os sinais
    signals = db.get_all_signals()
    
    if not signals:
        print("📭 Nenhum sinal encontrado no banco de dados.")
        return
    
    print(f"📊 Total de sinais encontrados: {len(signals)}")
    print()
    
    # Contar sinais por status
    status_count = {}
    type_count = {}
    class_count = {}
    
    for signal in signals:
        status = signal.get('status', 'N/A')
        signal_type = signal.get('type', 'N/A')
        signal_class = signal.get('signal_class', 'N/A')
        
        status_count[status] = status_count.get(status, 0) + 1
        type_count[signal_type] = type_count.get(signal_type, 0) + 1
        class_count[signal_class] = class_count.get(signal_class, 0) + 1
    
    # Exibir estatísticas
    print("📈 ESTATÍSTICAS:")
    print(f"   Status: {dict(status_count)}")
    print(f"   Tipos: {dict(type_count)}")
    print(f"   Classes: {dict(class_count)}")
    print()
    
    # Perguntar se quer ver todos os sinais
    if len(signals) > 10:
        choice = input(f"Deseja ver todos os {len(signals)} sinais? (s/N): ").lower()
        if choice != 's':
            signals = signals[:10]
            print(f"Mostrando apenas os primeiros 10 sinais...")
            print()
    
    # Exibir sinais
    print("🔍 SINAIS ENCONTRADOS:")
    for i, signal in enumerate(signals, 1):
        print(f"\n{i}. {format_signal_display(signal)}")
    
    print("\n✅ Visualização concluída!")

if __name__ == "__main__":
    main()