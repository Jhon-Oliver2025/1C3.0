#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os
from datetime import datetime

def check_signals_database():
    db_path = './Cryptem1.1/back/signals.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Banco não encontrado: {db_path}")
        return
    
    print(f"✅ Verificando banco: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Listar tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"\n📊 Tabelas encontradas: {[t[0] for t in tables]}")
        
        # Verificar tabela signals
        if any(t[0] == 'signals' for t in tables):
            print("\n🔍 Analisando tabela 'signals'...")
            
            # Estrutura da tabela
            cursor.execute("PRAGMA table_info(signals)")
            columns = cursor.fetchall()
            print(f"Colunas: {[col[1] for col in columns]}")
            
            # Total de registros
            cursor.execute("SELECT COUNT(*) FROM signals")
            total = cursor.fetchone()[0]
            print(f"Total de sinais: {total}")
            
            # Contar por status
            cursor.execute("SELECT status, COUNT(*) FROM signals GROUP BY status")
            status_counts = cursor.fetchall()
            print("\n📊 Distribuição por status:")
            for status, count in status_counts:
                print(f"  {status}: {count}")
            
            # Sinais pendentes
            cursor.execute("SELECT COUNT(*) FROM signals WHERE status = 'pending'")
            pending_count = cursor.fetchone()[0]
            
            if pending_count > 0:
                print(f"\n🚨 ENCONTRADOS {pending_count} SINAIS PENDENTES!")
                
                # Mostrar alguns sinais pendentes
                cursor.execute("SELECT * FROM signals WHERE status = 'pending' LIMIT 5")
                pending_signals = cursor.fetchall()
                
                print("\n📋 Primeiros 5 sinais pendentes:")
                for i, signal in enumerate(pending_signals, 1):
                    signal_dict = dict(signal)
                    print(f"\n{i}. ID: {signal_dict.get('id')}")
                    print(f"   Symbol: {signal_dict.get('symbol')}")
                    print(f"   Type: {signal_dict.get('type')}")
                    print(f"   Entry Price: {signal_dict.get('entry_price')}")
                    print(f"   Created: {signal_dict.get('created_at')}")
                    print(f"   Status: {signal_dict.get('status')}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_signals_database()