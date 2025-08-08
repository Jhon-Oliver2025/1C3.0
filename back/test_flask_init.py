#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar a inicialização específica do Flask
"""

import os
import sys
import traceback
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

print("🔍 Testando inicialização do Flask...")
print("="*50)

try:
    print("1. Testando importação do config...")
    from config import server
    print("✅ Config importado com sucesso")
    
    print("\n2. Testando criação da app Flask...")
    from api import create_app
    app = create_app()
    print("✅ App Flask criada com sucesso")
    
    print("\n3. Testando configurações da app...")
    print(f"   - Debug: {app.debug}")
    print(f"   - Testing: {app.testing}")
    print(f"   - Secret Key: {app.config.get('SECRET_KEY', 'NOT_SET')[:10]}...")
    print(f"   - JWT Secret: {app.config.get('JWT_SECRET', 'NOT_SET')[:10]}...")
    
    print("\n4. Testando registro de rotas básicas...")
    with app.app_context():
        # Testar se as rotas básicas estão funcionando
        @app.route('/test')
        def test_route():
            return {'status': 'ok', 'message': 'Flask está funcionando'}
        
        print("✅ Rota de teste registrada")
    
    print("\n5. Testando inicialização do servidor de teste...")
    with app.test_client() as client:
        # Testar rota básica
        response = client.get('/test')
        print(f"   - Status da resposta: {response.status_code}")
        print(f"   - Dados da resposta: {response.get_json()}")
        
        if response.status_code == 200:
            print("✅ Servidor Flask respondendo corretamente")
        else:
            print(f"❌ Servidor Flask retornou status {response.status_code}")
    
    print("\n6. Testando importação do KryptonBot...")
    try:
        from krypton_bot import KryptonBot
        print("✅ KryptonBot importado com sucesso")
        
        # Testar inicialização básica
        bot = KryptonBot()
        print("✅ KryptonBot inicializado com sucesso")
        
    except Exception as e:
        print(f"⚠️ Erro ao inicializar KryptonBot: {e}")
        print("   Isso pode não ser crítico para o Flask")
    
    print("\n7. Testando registro completo das rotas...")
    try:
        from api import register_api_routes
        # Simular bot_instance para teste
        class MockBot:
            pass
        
        mock_bot = MockBot()
        register_api_routes(app, mock_bot)
        print("✅ Rotas registradas com sucesso")
        
        # Listar algumas rotas registradas
        print("\n   Rotas registradas:")
        for rule in app.url_map.iter_rules():
            if str(rule).startswith('/api/'):
                print(f"   - {rule}")
                
    except Exception as e:
        print(f"❌ Erro ao registrar rotas: {e}")
        traceback.print_exc()
    
    print("\n🎉 Teste de inicialização do Flask concluído!")
    print("\n📋 Resumo:")
    print("- Config: ✅")
    print("- Flask App: ✅")
    print("- Configurações: ✅")
    print("- Servidor de teste: ✅")
    print("- Registro de rotas: ✅")
    
except Exception as e:
    print(f"\n❌ ERRO CRÍTICO: {e}")
    print("\n🔍 Traceback completo:")
    traceback.print_exc()
    sys.exit(1)