#!/usr/bin/env python3
"""
Script para testar inicialização mínima do Flask
"""

import os
import sys
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()

print("🔍 === TESTE DE INICIALIZAÇÃO MÍNIMA DO FLASK ===")
print(f"🐍 Python version: {sys.version}")
print(f"📁 Working directory: {os.getcwd()}")

# Verificar variáveis de ambiente críticas
print("\n🔧 === VARIÁVEIS DE AMBIENTE ===")
env_vars = [
    'FLASK_ENV', 'DATABASE_URL', 'SECRET_KEY', 'JWT_SECRET',
    'BINANCE_API_KEY', 'BINANCE_SECRET_KEY', 'TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHAT_ID'
]

for var in env_vars:
    value = os.getenv(var)
    if value:
        if 'SECRET' in var or 'KEY' in var or 'TOKEN' in var:
            print(f"✅ {var}: {value[:10]}...")
        else:
            print(f"✅ {var}: {value}")
    else:
        print(f"❌ {var}: NOT SET")

# Testar importação da API
print("\n📦 === TESTANDO IMPORTAÇÕES ===")
try:
    from api import create_app
    print("✅ api.create_app importado com sucesso")
except Exception as e:
    print(f"❌ Erro ao importar api.create_app: {e}")
    sys.exit(1)

# Testar criação da aplicação Flask
print("\n🌐 === TESTANDO CRIAÇÃO DA APLICAÇÃO FLASK ===")
try:
    app = create_app()
    print(f"✅ Aplicação Flask criada: {app}")
    
    # Listar rotas básicas
    print("\n📋 === ROTAS BÁSICAS REGISTRADAS ===")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.rule} -> {rule.endpoint}")
        
except Exception as e:
    print(f"❌ Erro ao criar aplicação Flask: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Testar servidor Flask básico
print("\n🚀 === TESTANDO SERVIDOR FLASK ===")
try:
    with app.test_client() as client:
        # Testar rota básica
        response = client.get('/')
        print(f"📡 GET / -> Status: {response.status_code}")
        
        # Testar rota de status
        response = client.get('/status')
        print(f"📡 GET /status -> Status: {response.status_code}")
        
        print("✅ Servidor Flask básico funcionando")
        
except Exception as e:
    print(f"❌ Erro ao testar servidor Flask: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n🎉 === TESTE CONCLUÍDO COM SUCESSO ===")
print("✅ A aplicação Flask pode ser inicializada corretamente")