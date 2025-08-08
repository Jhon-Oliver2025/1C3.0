#!/usr/bin/env python3
"""
Script de pré-verificação para garantir que todos os serviços estão prontos
"""

import os
import sys
import time
import psycopg2
import redis
from urllib.parse import urlparse

def check_postgres():
    """
    Verifica conectividade com PostgreSQL
    """
    try:
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            # Tentar construir URL a partir de variáveis separadas
            host = os.getenv('POSTGRES_HOST', 'postgres')
            port = os.getenv('POSTGRES_PORT', '5432')
            db = os.getenv('POSTGRES_DB', 'crypten')
            user = os.getenv('POSTGRES_USER', 'postgres')
            password = os.getenv('POSTGRES_PASSWORD', '')
            database_url = f"postgresql://{user}:{password}@{host}:{port}/{db}"
        
        print(f"🔍 Testando conexão PostgreSQL...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        cursor.execute('SELECT version();')
        version = cursor.fetchone()[0]
        print(f"✅ PostgreSQL conectado: {version[:50]}...")
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro PostgreSQL: {e}")
        return False

def check_redis():
    """
    Verifica conectividade com Redis
    """
    try:
        redis_url = os.getenv('REDIS_URL', 'redis://redis:6379/0')
        print(f"🔍 Testando conexão Redis...")
        
        r = redis.from_url(redis_url)
        r.ping()
        print(f"✅ Redis conectado")
        return True
        
    except Exception as e:
        print(f"❌ Erro Redis: {e}")
        return False

def check_environment():
    """
    Verifica variáveis de ambiente essenciais
    """
    required_vars = [
        'SECRET_KEY',
        'JWT_SECRET',
        'BINANCE_API_KEY',
        'BINANCE_SECRET_KEY',
        'TELEGRAM_BOT_TOKEN',
        'TELEGRAM_CHAT_ID'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Variáveis de ambiente faltando: {', '.join(missing_vars)}")
        return False
    
    print(f"✅ Todas as variáveis de ambiente estão definidas")
    return True

def main():
    """
    Executa todas as verificações pré-healthcheck
    """
    print("🚀 Iniciando pré-verificações...")
    
    checks = [
        ("Variáveis de ambiente", check_environment),
        ("PostgreSQL", check_postgres),
        ("Redis", check_redis)
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        print(f"\n📋 Verificando {check_name}...")
        if not check_func():
            all_passed = False
            print(f"💥 Falha na verificação: {check_name}")
        else:
            print(f"✅ {check_name} OK")
    
    if all_passed:
        print("\n🎉 Todas as pré-verificações passaram!")
        return True
    else:
        print("\n💥 Algumas pré-verificações falharam!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)