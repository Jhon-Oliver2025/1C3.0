#!/usr/bin/env python3
"""
Script para testar a correção do middleware de autenticação
Testa diferentes cenários de tokens para verificar se o problema foi resolvido
"""

import requests
import json

def test_auth_scenarios():
    """Testa diferentes cenários de autenticação"""
    base_url = "http://localhost:5000"  # Ajuste conforme necessário
    
    print("🧪 Testando correções do middleware de autenticação...\n")
    
    # Cenários de teste
    test_cases = [
        {
            "name": "Token válido",
            "headers": {"Authorization": "Bearer valid-token-123"},
            "expected_status": [401, 403]  # Esperado falhar pois token não existe no DB
        },
        {
            "name": "Token null (problema original)",
            "headers": {"Authorization": "Bearer null"},
            "expected_status": [401]  # Deve ser rejeitado imediatamente
        },
        {
            "name": "Token vazio",
            "headers": {"Authorization": "Bearer "},
            "expected_status": [401]  # Deve ser rejeitado imediatamente
        },
        {
            "name": "Token NULL maiúsculo",
            "headers": {"Authorization": "Bearer NULL"},
            "expected_status": [401]  # Deve ser rejeitado imediatamente
        },
        {
            "name": "Sem header Authorization",
            "headers": {},
            "expected_status": [401]  # Deve ser rejeitado
        },
        {
            "name": "Header Authorization malformado",
            "headers": {"Authorization": "InvalidFormat"},
            "expected_status": [401]  # Deve ser rejeitado
        }
    ]
    
    # Endpoint protegido para testar
    test_endpoint = f"{base_url}/api/auth/check-admin"
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"📋 Teste {i}: {test_case['name']}")
        
        try:
            response = requests.get(
                test_endpoint,
                headers=test_case["headers"],
                timeout=5
            )
            
            status_code = response.status_code
            
            if status_code in test_case["expected_status"]:
                print(f"   ✅ PASSOU - Status: {status_code}")
            else:
                print(f"   ❌ FALHOU - Status esperado: {test_case['expected_status']}, obtido: {status_code}")
                print(f"   📄 Resposta: {response.text[:200]}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ⚠️  ERRO DE CONEXÃO: {e}")
            
        print()
    
    print("🏁 Testes concluídos!")
    print("\n💡 Dicas:")
    print("   - Se todos os testes passaram, o middleware está funcionando corretamente")
    print("   - Tokens 'null' agora devem ser rejeitados imediatamente")
    print("   - Isso deve reduzir significativamente os logs de erro em produção")

def test_production_scenario():
    """Simula o cenário específico de produção"""
    print("\n🌐 Testando cenário de produção...")
    
    # Simular múltiplas requisições com token 'null' como estava acontecendo
    production_url = "https://1crypten.space"  # URL de produção
    
    headers = {
        "Authorization": "Bearer null",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/603.1.30"
    }
    
    try:
        response = requests.get(
            f"{production_url}/api/auth/check-admin",
            headers=headers,
            timeout=10
        )
        
        print(f"📊 Status de produção: {response.status_code}")
        
        if response.status_code == 401:
            print("   ✅ Produção está rejeitando tokens 'null' corretamente")
        else:
            print(f"   ⚠️  Resposta inesperada: {response.text[:200]}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ⚠️  Erro ao testar produção: {e}")

if __name__ == "__main__":
    print("🔧 Teste de Correção do Middleware de Autenticação")
    print("=" * 50)
    
    # Testar localmente primeiro
    test_auth_scenarios()
    
    # Testar produção (opcional)
    test_production = input("\n❓ Testar também em produção? (y/N): ").lower().strip()
    if test_production == 'y':
        test_production_scenario()
    
    print("\n🎯 Resumo da correção aplicada:")
    print("   1. Middleware agora filtra tokens 'null', vazios ou inválidos")
    print("   2. Logs de debug excessivos foram removidos")
    print("   3. Tokens inválidos são rejeitados antes de consultar o banco")
    print("   4. Isso deve eliminar o spam de logs em produção")