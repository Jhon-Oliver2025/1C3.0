#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar sinais pendentes usando banco local SQLite
"""

import os
import sys
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

def find_database_file():
    """
    Procura pelo arquivo de banco SQLite
    """
    possible_paths = [
        'back/crypto_signals.db',
        'back/data/crypto_signals.db',
        'crypto_signals.db',
        'data/crypto_signals.db',
        'back/trading_signals.db',
        'trading_signals.db'
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return None

def check_pending_signals():
    """
    Verifica sinais pendentes no banco SQLite local
    """
    print("\n" + "="*60)
    print("🔍 VERIFICANDO SINAIS PENDENTES NO BANCO LOCAL")
    print("="*60)
    
    # Procurar arquivo de banco
    db_path = find_database_file()
    
    if not db_path:
        print("❌ Arquivo de banco SQLite não encontrado")
        print("\n📋 Procurando por arquivos .db...")
        
        # Procurar todos os arquivos .db
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.endswith('.db'):
                    full_path = os.path.join(root, file)
                    print(f"  📄 Encontrado: {full_path}")
        
        return False
    
    print(f"✅ Banco encontrado: {db_path}")
    
    try:
        # Conectar ao banco
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Para acessar colunas por nome
        cursor = conn.cursor()
        
        # Listar todas as tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"\n📊 Tabelas encontradas: {len(tables)}")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Procurar tabelas de sinais
        signal_tables = []
        for table in tables:
            table_name = table[0]
            if any(keyword in table_name.lower() for keyword in ['signal', 'btc', 'crypto', 'trading']):
                signal_tables.append(table_name)
        
        if not signal_tables:
            print("\n❌ Nenhuma tabela de sinais encontrada")
            return False
        
        print(f"\n🎯 Tabelas de sinais: {signal_tables}")
        
        # Analisar cada tabela de sinais
        for table_name in signal_tables:
            print(f"\n📋 Analisando tabela: {table_name}")
            
            # Verificar estrutura da tabela
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            print(f"  📊 Colunas ({len(columns)}):")
            for col in columns:
                print(f"    - {col[1]} ({col[2]})")
            
            # Contar total de registros
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            total_count = cursor.fetchone()[0]
            print(f"  📈 Total de registros: {total_count}")
            
            if total_count == 0:
                continue
            
            # Verificar se há coluna de status
            column_names = [col[1].lower() for col in columns]
            
            if 'status' in column_names:
                # Contar por status
                cursor.execute(f"SELECT status, COUNT(*) FROM {table_name} GROUP BY status")
                status_counts = cursor.fetchall()
                
                print(f"  📊 Distribuição por status:")
                pending_count = 0
                for status, count in status_counts:
                    print(f"    - {status}: {count}")
                    if status and status.lower() == 'pending':
                        pending_count = count
                
                if pending_count > 0:
                    print(f"\n🚨 ENCONTRADOS {pending_count} SINAIS PENDENTES!")
                    
                    # Mostrar alguns sinais pendentes
                    cursor.execute(f"SELECT * FROM {table_name} WHERE status = 'pending' LIMIT 5")
                    pending_signals = cursor.fetchall()
                    
                    print(f"\n📋 Primeiros 5 sinais pendentes:")
                    for i, signal in enumerate(pending_signals, 1):
                        signal_dict = dict(signal)
                        print(f"\n{i}. ID: {signal_dict.get('id', 'N/A')}")
                        print(f"   Symbol: {signal_dict.get('symbol', 'N/A')}")
                        print(f"   Type: {signal_dict.get('type', 'N/A')}")
                        print(f"   Entry Price: {signal_dict.get('entry_price', 'N/A')}")
                        print(f"   Created: {signal_dict.get('created_at', 'N/A')}")
                        
                        # Verificar idade do sinal
                        created_at = signal_dict.get('created_at')
                        if created_at:
                            try:
                                # Tentar diferentes formatos de data
                                for fmt in ['%Y-%m-%d %H:%M:%S', '%d/%m/%Y %H:%M:%S', '%Y-%m-%dT%H:%M:%S']:
                                    try:
                                        created_date = datetime.strptime(created_at, fmt)
                                        age = datetime.now() - created_date
                                        print(f"   Idade: {age.days} dias, {age.seconds//3600} horas")
                                        break
                                    except ValueError:
                                        continue
                            except:
                                print(f"   Idade: Não foi possível calcular")
                    
                    # Verificar sinais muito antigos (mais de 1 dia)
                    cursor.execute(f"""
                        SELECT COUNT(*) FROM {table_name} 
                        WHERE status = 'pending' 
                        AND datetime(created_at) < datetime('now', '-1 day')
                    """)
                    old_signals = cursor.fetchone()[0]
                    
                    if old_signals > 0:
                        print(f"\n⚠️ {old_signals} sinais pendentes há mais de 1 dia!")
                        print("   Estes sinais provavelmente deveriam ter sido processados.")
            
            else:
                print(f"  ⚠️ Tabela não possui coluna 'status'")
                
                # Mostrar algumas linhas de exemplo
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                sample_rows = cursor.fetchall()
                
                if sample_rows:
                    print(f"  📋 Exemplo de registros:")
                    for i, row in enumerate(sample_rows, 1):
                        row_dict = dict(row)
                        print(f"    {i}. {dict(list(row_dict.items())[:3])}...")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao acessar banco: {e}")
        import traceback
        traceback.print_exc()
        return False

def suggest_solutions():
    """
    Sugere soluções para o problema dos sinais pendentes
    """
    print("\n" + "="*60)
    print("💡 POSSÍVEIS SOLUÇÕES")
    print("="*60)
    
    print("\n🔧 1. PROBLEMA: Sistema de monitoramento não está rodando")
    print("   Solução: Iniciar o backend com monitoramento ativo")
    print("   Comando: cd back && python app_supabase.py")
    
    print("\n🔧 2. PROBLEMA: Configuração do Supabase incorreta")
    print("   Solução: Configurar URL real do Supabase ou usar SQLite local")
    print("   Arquivo: .env (verificar SUPABASE_URL)")
    
    print("\n🔧 3. PROBLEMA: Sinais muito antigos acumulados")
    print("   Solução: Limpar sinais antigos ou forçar processamento")
    print("   Script: cleanup_old_signals.py")
    
    print("\n🔧 4. PROBLEMA: Sistema de confirmação com erro")
    print("   Solução: Verificar logs e reiniciar monitoramento")
    print("   Verificar: BTCSignalManager.start_monitoring()")
    
    print("\n🔧 5. SOLUÇÃO IMEDIATA: Confirmar sinais manualmente")
    print("   Script: confirm_signal.py")
    print("   API: POST /api/btc-signals/confirm/{signal_id}")

def main():
    """
    Função principal
    """
    print(f"🚀 Iniciando diagnóstico em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    success = check_pending_signals()
    
    if success:
        suggest_solutions()
        print("\n✅ Diagnóstico concluído!")
    else:
        print("\n❌ Não foi possível completar o diagnóstico")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()