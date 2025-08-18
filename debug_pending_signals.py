#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar sinais pendentes diretamente no banco Supabase
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

try:
    from supabase import create_client, Client
except ImportError:
    print("❌ Erro: biblioteca supabase não encontrada")
    print("Execute: pip install supabase")
    sys.exit(1)

def check_pending_signals():
    """
    Verifica sinais pendentes diretamente no banco Supabase
    """
    print("\n" + "="*60)
    print("🔍 VERIFICANDO SINAIS PENDENTES NO SUPABASE")
    print("="*60)
    
    try:
        # Configurar cliente Supabase
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not supabase_url or not supabase_key:
            print("❌ Erro: Variáveis SUPABASE_URL ou SUPABASE_SERVICE_ROLE_KEY não configuradas")
            return False
        
        print(f"✅ Conectando ao Supabase: {supabase_url}")
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Verificar sinais pendentes
        print("\n🔍 Buscando sinais pendentes...")
        
        # Tentar diferentes nomes de tabela possíveis
        table_names = ['signals', 'btc_signals', 'crypto_signals', 'pending_signals']
        
        for table_name in table_names:
            try:
                print(f"\n📊 Tentando tabela: {table_name}")
                
                # Buscar todos os registros da tabela
                response = supabase.table(table_name).select("*").limit(10).execute()
                
                if response.data:
                    print(f"✅ Tabela {table_name} encontrada com {len(response.data)} registros")
                    
                    # Mostrar estrutura da tabela
                    if response.data:
                        print("\n📋 Estrutura da tabela:")
                        first_record = response.data[0]
                        for key in first_record.keys():
                            print(f"  - {key}: {type(first_record[key]).__name__}")
                    
                    # Buscar sinais pendentes especificamente
                    try:
                        pending_response = supabase.table(table_name).select("*").eq('status', 'pending').execute()
                        print(f"\n🔍 Sinais com status 'pending': {len(pending_response.data)}")
                        
                        if pending_response.data:
                            print("\n📊 Primeiros 5 sinais pendentes:")
                            for i, signal in enumerate(pending_response.data[:5]):
                                print(f"\n{i+1}. ID: {signal.get('id', 'N/A')}")
                                print(f"   Symbol: {signal.get('symbol', 'N/A')}")
                                print(f"   Type: {signal.get('type', 'N/A')}")
                                print(f"   Status: {signal.get('status', 'N/A')}")
                                print(f"   Created: {signal.get('created_at', 'N/A')}")
                                print(f"   Entry Price: {signal.get('entry_price', 'N/A')}")
                    except Exception as e:
                        print(f"⚠️ Erro ao buscar sinais pendentes: {e}")
                    
                    # Buscar sinais confirmados
                    try:
                        confirmed_response = supabase.table(table_name).select("*").eq('status', 'confirmed').execute()
                        print(f"\n✅ Sinais confirmados: {len(confirmed_response.data)}")
                    except Exception as e:
                        print(f"⚠️ Erro ao buscar sinais confirmados: {e}")
                    
                    # Buscar sinais rejeitados
                    try:
                        rejected_response = supabase.table(table_name).select("*").eq('status', 'rejected').execute()
                        print(f"❌ Sinais rejeitados: {len(rejected_response.data)}")
                    except Exception as e:
                        print(f"⚠️ Erro ao buscar sinais rejeitados: {e}")
                    
                    break
                    
            except Exception as e:
                print(f"❌ Tabela {table_name} não encontrada: {e}")
                continue
        
        else:
            print("❌ Nenhuma tabela de sinais encontrada")
            
            # Listar todas as tabelas disponíveis
            print("\n📋 Tentando listar tabelas disponíveis...")
            try:
                # Isso pode não funcionar dependendo das permissões
                tables_response = supabase.rpc('get_tables').execute()
                if tables_response.data:
                    print("Tabelas disponíveis:")
                    for table in tables_response.data:
                        print(f"  - {table}")
            except Exception as e:
                print(f"⚠️ Não foi possível listar tabelas: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao conectar com Supabase: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """
    Função principal
    """
    print(f"🚀 Iniciando verificação em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    success = check_pending_signals()
    
    if success:
        print("\n✅ Verificação concluída com sucesso!")
    else:
        print("\n❌ Verificação falhou!")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()