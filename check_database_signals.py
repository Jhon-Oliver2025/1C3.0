#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'back'))

from back.core.database import Database

def check_database_signals():
    print("🔍 Verificando sinais no banco de dados...")
    
    try:
        db = Database()
        
        # Verificar sinais no arquivo CSV
        print("\n📊 Verificando sinais no arquivo CSV...")
        
        all_signals = db.get_all_signals()
        print(f"Total de sinais no CSV: {len(all_signals)}")
        
        if all_signals:
            # Filtrar sinais confirmados
            confirmed_signals = [s for s in all_signals if s.get('status') == 'CONFIRMED']
            print(f"Sinais confirmados no CSV: {len(confirmed_signals)}")
            
            if confirmed_signals:
                print("\n📋 Primeiros 5 sinais confirmados:")
                for i, signal in enumerate(confirmed_signals[:5]):
                    print(f"  {i+1}. {signal.get('symbol')} - {signal.get('type')} - {signal.get('status')} - {signal.get('entry_time')}")
                    
                print("\n🔍 Exemplo completo de sinal confirmado:")
                example = confirmed_signals[0]
                for key, value in example.items():
                    print(f"   {key}: {value}")
            else:
                print("⚠️ Nenhum sinal confirmado encontrado no CSV")
                
            # Mostrar estatísticas por status
            status_counts = {}
            for signal in all_signals:
                status = signal.get('status', 'UNKNOWN')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            print("\n📊 Estatísticas por status:")
            for status, count in status_counts.items():
                print(f"   {status}: {count}")
        else:
            print("⚠️ Nenhum sinal encontrado no CSV")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    check_database_signals()