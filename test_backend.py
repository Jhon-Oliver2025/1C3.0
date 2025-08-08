#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste para verificar a inicialização do backend
"""

import os
import sys
import traceback
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

print("🧪 Testando inicialização do backend...")
print(f"📁 Diretório atual: {os.getcwd()}")
print(f"🐍 Python: {sys.version}")
print(f"📦 Caminho do Python: {sys.executable}")

# Testar importações básicas
print("\n📦 Testando importações básicas...")
try:
    import flask
    print(f"✅ Flask: {flask.__version__}")
except ImportError as e:
    print(f"❌ Erro ao importar Flask: {e}")
    sys.exit(1)

try:
    import psycopg2
    print(f"✅ psycopg2: {psycopg2.__version__}")
except ImportError as e:
    print(f"❌ Erro ao importar psycopg2: {e}")
    sys.exit(1)

try:
    import redis
    print(f"✅ redis: {redis.__version__}")
except ImportError as e:
    print(f"❌ Erro ao importar redis: {e}")
    sys.exit(1)

# Testar variáveis de ambiente
print("\n🔧 Verificando variáveis de ambiente...")
env_vars = [
    'FLASK_ENV',
    'DATABASE_URL',
    'REDIS_URL',
    'SECRET_KEY',
    'JWT_SECRET'
]

for var in env_vars:
    value = os.getenv(var)
    if value:
        if 'SECRET' in var or 'PASSWORD' in var:
            print(f"✅ {var}: {'*' * 10}")
        else:
            print(f"✅ {var}: {value}")
    else:
        print(f"⚠️ {var}: não definida")

# Testar importações do projeto
print("\n📦 Testando importações do projeto...")
sys.path.insert(0, os.path.join(os.getcwd(), 'back'))

try:
    from config import server
    print("✅ config.server importado")
except Exception as e:
    print(f"❌ Erro ao importar config.server: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    from core.database import Database
    print("✅ core.database.Database importado")
except Exception as e:
    print(f"❌ Erro ao importar Database: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    from core.db_config import DatabaseConfig
    print("✅ core.db_config.DatabaseConfig importado")
except Exception as e:
    print(f"❌ Erro ao importar DatabaseConfig: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    from core.telegram_notifier import TelegramNotifier
    print("✅ core.telegram_notifier.TelegramNotifier importado")
except Exception as e:
    print(f"❌ Erro ao importar TelegramNotifier: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    from api import create_app, register_api_routes
    print("✅ api.create_app e register_api_routes importados")
except Exception as e:
    print(f"❌ Erro ao importar api: {e}")
    traceback.print_exc()
    sys.exit(1)

# Testar criação da aplicação Flask
print("\n🌐 Testando criação da aplicação Flask...")
try:
    app = create_app()
    print("✅ Aplicação Flask criada com sucesso")
except Exception as e:
    print(f"❌ Erro ao criar aplicação Flask: {e}")
    traceback.print_exc()
    sys.exit(1)

# Testar inicialização do KryptonBot
print("\n🤖 Testando inicialização do KryptonBot...")
try:
    # Importar a classe KryptonBot do app.py
    import importlib.util
    spec = importlib.util.spec_from_file_location("app", "back/app.py")
    app_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(app_module)
    
    bot = app_module.KryptonBot()
    print("✅ KryptonBot inicializado com sucesso")
except Exception as e:
    print(f"❌ Erro ao inicializar KryptonBot: {e}")
    traceback.print_exc()
    sys.exit(1)

# Testar registro das rotas
print("\n🔗 Testando registro das rotas...")
try:
    register_api_routes(app, bot)
    print("✅ Rotas registradas com sucesso")
except Exception as e:
    print(f"❌ Erro ao registrar rotas: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n🎉 Todos os testes passaram! O backend deve estar funcionando.")
print("\n📋 Resumo:")
print("- Importações: ✅")
print("- Variáveis de ambiente: ✅")
print("- Flask app: ✅")
print("- KryptonBot: ✅")
print("- Rotas: ✅")