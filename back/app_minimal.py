#!/usr/bin/env python3
"""
Versão simplificada do app.py para debug de deploy
"""

import os
import sys
import time
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()

print("🚀 Iniciando aplicação minimal...")
print(f"🔍 Python version: {sys.version}")
print(f"🔍 Working directory: {os.getcwd()}")
print(f"🔍 Environment variables:")
for key in ['FLASK_ENV', 'FLASK_DEBUG', 'DATABASE_URL', 'REDIS_URL']:
    value = os.getenv(key, 'NOT_SET')
    if 'URL' in key and value != 'NOT_SET':
        print(f"🔍   {key}: {value[:20]}...")
    else:
        print(f"🔍   {key}: {value}")

try:
    # Importar Flask e criar aplicação básica
    from api import create_app, register_api_routes
    print("✅ Módulos importados com sucesso")
    
    # Criar aplicação Flask
    app = create_app()
    print("✅ Aplicação Flask criada")
    
    # Criar um mock do bot para registrar as rotas
    class MockBot:
        def __init__(self):
            self.db = None
            self.analyzer = None
            self.notifier = None
            self.gerenciador_sinais = None
    
    mock_bot = MockBot()
    
    # Registrar rotas da API
    print("🔗 Registrando rotas da API...")
    register_api_routes(app, mock_bot)
    print("✅ Rotas da API registradas")
    
    # Listar rotas registradas
    print("📋 Rotas registradas:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.rule} -> {rule.endpoint}")
    
    # Iniciar servidor Flask
    flask_port = int(os.getenv('FLASK_PORT', 5000))
    print(f"🌐 Servidor Flask iniciando na porta {flask_port}...")
    print(f"🔍 Ambiente: {os.getenv('FLASK_ENV', 'development')}")
    print(f"🔍 Debug: {os.getenv('FLASK_DEBUG', 'False')}")
    print("✅ Todas as configurações carregadas com sucesso!")
    
    app.run(debug=False, host='0.0.0.0', port=flask_port, use_reloader=False)
    
except Exception as e:
    print(f"❌ Erro na inicialização: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)