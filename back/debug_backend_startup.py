#!/usr/bin/env python3
"""
Script de debug específico para problemas de inicialização do backend
"""

import os
import sys
import time
import subprocess
import traceback
from datetime import datetime

def test_environment_variables():
    """
    Testa se todas as variáveis de ambiente necessárias estão definidas
    """
    print("🔧 === TESTANDO VARIÁVEIS DE AMBIENTE ===")
    
    required_vars = [
        'SECRET_KEY',
        'JWT_SECRET', 
        'DATABASE_URL',
        'REDIS_URL',
        'BINANCE_API_KEY',
        'BINANCE_SECRET_KEY',
        'TELEGRAM_BOT_TOKEN',
        'TELEGRAM_CHAT_ID'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
            print(f"❌ {var}: NÃO DEFINIDA")
        else:
            # Mostrar apenas primeiros caracteres para segurança
            display_value = value[:10] + "..." if len(value) > 10 else value
            print(f"✅ {var}: {display_value}")
    
    if missing_vars:
        print(f"\n💥 VARIÁVEIS FALTANDO: {', '.join(missing_vars)}")
        return False
    
    print("\n✅ Todas as variáveis de ambiente estão definidas")
    return True

def test_database_connection():
    """
    Testa conexão com PostgreSQL
    """
    print("\n🗄️ === TESTANDO CONEXÃO POSTGRESQL ===")
    
    try:
        import psycopg2
        database_url = os.getenv('DATABASE_URL')
        
        if not database_url:
            print("❌ DATABASE_URL não definida")
            return False
            
        print(f"🔍 Conectando em: {database_url[:30]}...")
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        cursor.execute('SELECT version();')
        version = cursor.fetchone()[0]
        print(f"✅ PostgreSQL conectado: {version[:50]}...")
        
        # Testar se as tabelas existem
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
        tables = cursor.fetchall()
        print(f"📋 Tabelas encontradas: {[t[0] for t in tables]}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro PostgreSQL: {e}")
        return False

def test_redis_connection():
    """
    Testa conexão com Redis
    """
    print("\n🔴 === TESTANDO CONEXÃO REDIS ===")
    
    try:
        import redis
        redis_url = os.getenv('REDIS_URL', 'redis://redis:6379/0')
        
        print(f"🔍 Conectando em: {redis_url}")
        
        r = redis.from_url(redis_url)
        r.ping()
        print("✅ Redis conectado")
        return True
        
    except Exception as e:
        print(f"❌ Erro Redis: {e}")
        return False

def test_flask_imports():
    """
    Testa se todas as importações críticas funcionam
    """
    print("\n📦 === TESTANDO IMPORTAÇÕES CRÍTICAS ===")
    
    critical_imports = [
        ('flask', 'Flask'),
        ('config', 'server'),
        ('api', 'create_app'),
        ('core.database', 'Database'),
        ('core.binance_client', 'BinanceClient'),
        ('core.technical_analysis', 'TechnicalAnalysis'),
        ('core.telegram_notifier', 'TelegramNotifier')
    ]
    
    failed_imports = []
    
    for module_name, class_name in critical_imports:
        try:
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)
            print(f"✅ {module_name}.{class_name}")
        except Exception as e:
            print(f"❌ {module_name}.{class_name}: {e}")
            failed_imports.append(f"{module_name}.{class_name}")
    
    if failed_imports:
        print(f"\n💥 IMPORTAÇÕES FALHARAM: {', '.join(failed_imports)}")
        return False
    
    print("\n✅ Todas as importações críticas funcionam")
    return True

def test_flask_app_creation():
    """
    Testa se consegue criar a aplicação Flask
    """
    print("\n🌐 === TESTANDO CRIAÇÃO DA APLICAÇÃO FLASK ===")
    
    try:
        from api import create_app
        app = create_app()
        print(f"✅ Aplicação Flask criada: {app}")
        print(f"📋 Configurações: {list(app.config.keys())[:5]}...")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar aplicação Flask: {e}")
        traceback.print_exc()
        return False

def test_health_endpoint_locally():
    """
    Testa se consegue acessar o endpoint de health localmente
    """
    print("\n🏥 === TESTANDO ENDPOINT DE HEALTH ===")
    
    try:
        # Tentar importar e testar o endpoint diretamente
        from api import create_app, register_api_routes
        app = create_app()
        
        # Criar um mock do bot_instance para registrar as rotas
        class MockBot:
            pass
        
        mock_bot = MockBot()
        
        # Registrar as rotas da API
        print("🔗 Registrando rotas da API...")
        register_api_routes(app, mock_bot)
        
        # Listar todas as rotas registradas
        print("📋 Rotas registradas:")
        for rule in app.url_map.iter_rules():
            print(f"  {rule.rule} -> {rule.endpoint}")
        
        with app.test_client() as client:
            response = client.get('/api/health')
            print(f"📡 Status Code: {response.status_code}")
            print(f"📄 Response: {response.get_json()}")
            
            if response.status_code == 200:
                print("✅ Endpoint de health funcionando")
                return True
            else:
                print(f"❌ Status code inesperado: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Erro ao testar endpoint: {e}")
        traceback.print_exc()
        return False

def main():
    """
    Executa todos os testes de diagnóstico
    """
    print("🚀 === DEBUG DO BACKEND - INICIANDO ===")
    print(f"⏰ Timestamp: {datetime.now()}")
    print(f"📁 Diretório: {os.getcwd()}")
    print("=" * 60)
    
    tests = [
        ("Variáveis de ambiente", test_environment_variables),
        ("Conexão PostgreSQL", test_database_connection),
        ("Conexão Redis", test_redis_connection),
        ("Importações críticas", test_flask_imports),
        ("Criação da aplicação Flask", test_flask_app_creation),
        ("Endpoint de health", test_health_endpoint_locally)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🔍 Executando: {test_name}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"💥 ERRO CRÍTICO em {test_name}: {e}")
            traceback.print_exc()
            results[test_name] = False
    
    # Resumo final
    print("\n" + "=" * 60)
    print("📊 === RESUMO DOS TESTES ===")
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\n📈 Resultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 TODOS OS TESTES PASSARAM! O backend deveria funcionar.")
        return True
    else:
        print("💥 ALGUNS TESTES FALHARAM! Verifique os erros acima.")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 ERRO CRÍTICO: {e}")
        traceback.print_exc()
        sys.exit(1)