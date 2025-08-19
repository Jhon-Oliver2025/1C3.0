#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar a importação do blueprint restart_system
Identifica erros que impedem o registro do blueprint
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'back'))

def test_restart_blueprint():
    """
    Testa a importação do blueprint restart_system isoladamente
    """
    print("\n" + "="*80)
    print("🔍 TESTE DE IMPORTAÇÃO DO BLUEPRINT RESTART_SYSTEM")
    print("="*80)
    
    try:
        # 1. Testar importação das dependências
        print("\n📋 1. TESTANDO DEPENDÊNCIAS...")
        
        print("   Importando Flask...")
        from flask import Flask, Blueprint, jsonify
        print("   ✅ Flask importado com sucesso")
        
        print("   Importando middleware...")
        from middleware.auth_middleware import jwt_required, get_current_user
        print("   ✅ Middleware importado com sucesso")
        
        print("   Importando signal_cleanup...")
        from core.signal_cleanup import cleanup_system
        print(f"   ✅ cleanup_system importado: {cleanup_system}")
        
        print("   Importando BTCSignalManager...")
        from core.btc_signal_manager import BTCSignalManager
        print("   ✅ BTCSignalManager importado com sucesso")
        
        print("   Importando datetime e pytz...")
        from datetime import datetime
        import pytz
        print("   ✅ datetime e pytz importados com sucesso")
        
        # 2. Testar importação do blueprint
        print("\n📊 2. TESTANDO IMPORTAÇÃO DO BLUEPRINT...")
        
        print("   Importando restart_system_bp...")
        from api_routes.restart_system import restart_system_bp
        print(f"   ✅ Blueprint importado: {restart_system_bp}")
        print(f"   📍 Nome: {restart_system_bp.name}")
        print(f"   📍 URL Prefix: {restart_system_bp.url_prefix}")
        
        # 3. Testar criação de app Flask e registro
        print("\n🔧 3. TESTANDO REGISTRO NO FLASK...")
        
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test_key'
        
        print("   Registrando blueprint...")
        app.register_blueprint(restart_system_bp)
        print("   ✅ Blueprint registrado com sucesso!")
        
        # 4. Listar rotas registradas
        print("\n📋 4. ROTAS REGISTRADAS:")
        with app.app_context():
            for rule in app.url_map.iter_rules():
                if 'restart-system' in rule.rule:
                    print(f"   📍 {rule.rule} -> {rule.endpoint} [{', '.join(rule.methods)}]")
        
        # 5. Testar métodos do cleanup_system
        print("\n🧹 5. TESTANDO MÉTODOS DO CLEANUP_SYSTEM...")
        
        try:
            next_restart = cleanup_system.get_next_restart_time()
            print(f"   ✅ get_next_restart_time(): {next_restart}")
        except Exception as e:
            print(f"   ❌ Erro em get_next_restart_time(): {e}")
        
        try:
            time_until = cleanup_system.get_time_until_restart()
            print(f"   ✅ get_time_until_restart(): {time_until}")
        except Exception as e:
            print(f"   ❌ Erro em get_time_until_restart(): {e}")
        
        print("\n✅ TODOS OS TESTES PASSARAM!")
        print("\n💡 CONCLUSÃO: O blueprint deveria funcionar corretamente.")
        print("   Pode haver um problema específico no ambiente de produção.")
        
    except ImportError as e:
        print(f"\n❌ ERRO DE IMPORTAÇÃO: {e}")
        print(f"   Módulo: {e.name if hasattr(e, 'name') else 'Desconhecido'}")
        print(f"   Caminho: {e.path if hasattr(e, 'path') else 'Desconhecido'}")
        
        # Sugestões baseadas no erro
        if 'cleanup_system' in str(e):
            print("\n💡 SUGESTÃO: Problema com signal_cleanup.py")
            print("   - Verificar se o arquivo existe")
            print("   - Verificar dependências do Supabase")
        elif 'auth_middleware' in str(e):
            print("\n💡 SUGESTÃO: Problema com middleware de autenticação")
            print("   - Verificar se jwt_required está implementado")
        
    except Exception as e:
        print(f"\n❌ ERRO GERAL: {e}")
        print(f"   Tipo: {type(e).__name__}")
        
        import traceback
        print("\n📋 STACK TRACE:")
        traceback.print_exc()
    
    print("\n" + "="*80)
    print("🏁 TESTE CONCLUÍDO")
    print("="*80)

if __name__ == "__main__":
    test_restart_blueprint()