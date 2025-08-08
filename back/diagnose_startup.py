#!/usr/bin/env python3
"""
Script de diagnóstico para identificar problemas na inicialização
"""

import os
import sys
import traceback
import importlib

def check_python_environment():
    """
    Verifica o ambiente Python
    """
    print("🐍 === DIAGNÓSTICO DO AMBIENTE PYTHON ===")
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Working directory: {os.getcwd()}")
    print(f"Python path: {sys.path[:3]}...")  # Primeiros 3 paths
    print()

def check_environment_variables():
    """
    Verifica variáveis de ambiente críticas
    """
    print("🔧 === DIAGNÓSTICO DE VARIÁVEIS DE AMBIENTE ===")
    critical_vars = [
        'FLASK_ENV', 'FLASK_DEBUG', 'FLASK_PORT',
        'DATABASE_URL', 'REDIS_URL', 'SECRET_KEY', 'JWT_SECRET',
        'BINANCE_API_KEY', 'BINANCE_SECRET_KEY',
        'TELEGRAM_TOKEN', 'TELEGRAM_CHAT_ID'
    ]
    
    for var in critical_vars:
        value = os.getenv(var)
        if value:
            if 'SECRET' in var or 'KEY' in var or 'TOKEN' in var or 'URL' in var:
                print(f"✅ {var}: {'*' * min(len(value), 10)}... (mascarado)")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: NÃO DEFINIDA")
    print()

def check_critical_imports():
    """
    Verifica se todas as importações críticas funcionam
    """
    print("📦 === DIAGNÓSTICO DE IMPORTAÇÕES ===")
    
    critical_modules = [
        'flask',
        'psycopg2',
        'redis',
        'requests',
        'pandas',
        'numpy',
        'ta',
        'binance',
        'jwt',
        'config',
        'core.database',
        'core.binance_client',
        'core.technical_analysis',
        'core.telegram_notifier',
        'api'
    ]
    
    for module in critical_modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module}: OK")
        except ImportError as e:
            print(f"❌ {module}: FALHA - {e}")
        except Exception as e:
            print(f"⚠️ {module}: ERRO - {e}")
    print()

def check_file_permissions():
    """
    Verifica permissões de arquivos críticos
    """
    print("📁 === DIAGNÓSTICO DE ARQUIVOS ===")
    
    critical_files = [
        'app.py',
        'api.py',
        'config.py',
        'core/database.py',
        'core/binance_client.py'
    ]
    
    for file_path in critical_files:
        if os.path.exists(file_path):
            stat = os.stat(file_path)
            print(f"✅ {file_path}: Existe (tamanho: {stat.st_size} bytes)")
        else:
            print(f"❌ {file_path}: NÃO ENCONTRADO")
    print()

def test_database_connection():
    """
    Testa conexão com banco de dados
    """
    print("🗄️ === TESTE DE CONEXÃO COM BANCO ===")
    
    try:
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL não definida")
            return
        
        print(f"🔍 Testando conexão com: {database_url[:30]}...")
        
        import psycopg2
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ PostgreSQL conectado: {version[0][:50]}...")
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro na conexão com PostgreSQL: {e}")
    print()

def test_redis_connection():
    """
    Testa conexão com Redis
    """
    print("🔴 === TESTE DE CONEXÃO COM REDIS ===")
    
    try:
        redis_url = os.getenv('REDIS_URL')
        if not redis_url:
            print("❌ REDIS_URL não definida")
            return
        
        print(f"🔍 Testando conexão com: {redis_url[:30]}...")
        
        import redis
        r = redis.from_url(redis_url)
        r.ping()
        print("✅ Redis conectado com sucesso")
        
    except Exception as e:
        print(f"❌ Erro na conexão com Redis: {e}")
    print()

def main():
    """
    Executa todos os diagnósticos
    """
    print("🚀 === INICIANDO DIAGNÓSTICO COMPLETO ===")
    print()
    
    try:
        check_python_environment()
        check_environment_variables()
        check_critical_imports()
        check_file_permissions()
        test_database_connection()
        test_redis_connection()
        
        print("✅ === DIAGNÓSTICO CONCLUÍDO ===")
        
    except Exception as e:
        print(f"💥 ERRO DURANTE DIAGNÓSTICO: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()