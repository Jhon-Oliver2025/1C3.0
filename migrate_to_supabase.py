#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Migração para Supabase
Ajuda na transição do PostgreSQL local para o Supabase
"""

import os
import sys
from dotenv import load_dotenv

def check_supabase_env():
    """
    Verifica se as variáveis de ambiente do Supabase estão configuradas
    """
    print("🔍 Verificando configurações do Supabase...")
    
    required_vars = [
        'SUPABASE_URL',
        'SUPABASE_ANON_KEY', 
        'SUPABASE_SERVICE_ROLE_KEY',
        'SUPABASE_DATABASE_URL'
    ]
    
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
            print(f"❌ {var}: Não definida")
        else:
            # Mostrar apenas os primeiros caracteres por segurança
            display_value = value[:20] + "..." if len(value) > 20 else value
            print(f"✅ {var}: {display_value}")
    
    if missing_vars:
        print(f"\n❌ Variáveis faltando: {', '.join(missing_vars)}")
        print("\n💡 Passos para configurar o Supabase:")
        print("1. Acesse https://supabase.com e crie um projeto")
        print("2. Vá em Settings > API para obter as chaves")
        print("3. Vá em Settings > Database para obter a connection string")
        print("4. Copie .env.supabase.example para .env e preencha as variáveis")
        return False
    
    print("\n✅ Todas as variáveis do Supabase estão configuradas!")
    return True

def test_supabase_connection():
    """
    Testa a conexão com o Supabase
    """
    print("\n🔗 Testando conexão com Supabase...")
    
    try:
        import psycopg2
        from urllib.parse import urlparse
        
        database_url = os.getenv('SUPABASE_DATABASE_URL')
        
        if not database_url:
            print("❌ SUPABASE_DATABASE_URL não definida")
            return False
        
        # Analisar URL
        parsed = urlparse(database_url)
        print(f"🔍 Conectando ao Supabase: {parsed.hostname}")
        
        # Tentar conexão
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Testar consulta simples
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✅ Conexão bem-sucedida! PostgreSQL: {version.split()[1]}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except ImportError:
        print("❌ psycopg2 não instalado. Execute: pip install psycopg2-binary")
        return False
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        print("\n💡 Verifique:")
        print("- Se a SUPABASE_DATABASE_URL está correta")
        print("- Se o projeto Supabase está ativo")
        print("- Se a senha do banco está correta")
        return False

def create_tables_if_needed():
    """
    Cria as tabelas necessárias no Supabase se não existirem
    """
    print("\n📋 Verificando/criando tabelas necessárias...")
    
    try:
        import psycopg2
        
        database_url = os.getenv('SUPABASE_DATABASE_URL')
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # SQL para criar tabelas básicas (adapte conforme necessário)
        tables_sql = """
        -- Tabela de sinais de trading
        CREATE TABLE IF NOT EXISTS trading_signals (
            id SERIAL PRIMARY KEY,
            symbol VARCHAR(20) NOT NULL,
            signal_type VARCHAR(10) NOT NULL,
            price DECIMAL(20, 8),
            score INTEGER,
            timeframe VARCHAR(10),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata JSONB
        );
        
        -- Tabela de configurações
        CREATE TABLE IF NOT EXISTS bot_config (
            id SERIAL PRIMARY KEY,
            key VARCHAR(100) UNIQUE NOT NULL,
            value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Índices para performance
        CREATE INDEX IF NOT EXISTS idx_trading_signals_symbol ON trading_signals(symbol);
        CREATE INDEX IF NOT EXISTS idx_trading_signals_created_at ON trading_signals(created_at);
        """
        
        cursor.execute(tables_sql)
        conn.commit()
        
        print("✅ Tabelas criadas/verificadas com sucesso!")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        return False

def show_deployment_instructions():
    """
    Mostra instruções para deploy no Coolify
    """
    print("\n🚀 Instruções para Deploy no Coolify:")
    print("\n1. No Coolify, vá para seu projeto")
    print("2. Adicione as seguintes variáveis de ambiente:")
    print("   - SUPABASE_URL")
    print("   - SUPABASE_ANON_KEY")
    print("   - SUPABASE_SERVICE_ROLE_KEY")
    print("   - SUPABASE_DATABASE_URL")
    print("\n3. Faça commit e push das alterações:")
    print("   git add .")
    print("   git commit -m 'feat: migração para Supabase'")
    print("   git push origin main")
    print("\n4. Faça o deploy no Coolify")
    print("\n✨ O backend agora usará Supabase em vez do PostgreSQL local!")

def main():
    """
    Função principal do script de migração
    """
    print("🔄 Script de Migração para Supabase")
    print("=" * 50)
    
    # Carregar variáveis de ambiente
    load_dotenv()
    
    # Verificar configurações
    if not check_supabase_env():
        sys.exit(1)
    
    # Testar conexão
    if not test_supabase_connection():
        sys.exit(1)
    
    # Criar tabelas se necessário
    if not create_tables_if_needed():
        print("⚠️ Aviso: Erro ao criar tabelas, mas você pode continuar")
    
    # Mostrar instruções de deploy
    show_deployment_instructions()
    
    print("\n✅ Migração para Supabase concluída com sucesso!")
    print("🎉 Seu projeto está pronto para usar o Supabase!")

if __name__ == '__main__':
    main()