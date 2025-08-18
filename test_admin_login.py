#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar login admin e APIs BTC
"""

import requests
import json

def test_admin_login():
    """Testa login do usuário admin"""
    print("🔑 Testando login do usuário admin...")
    
    # Dados de login do admin
    login_data = {
        "username": "jonatasprojetos2013@gmail.com",
        "password": "admin123"  # Senha padrão comum
    }
    
    try:
        # Fazer login
        response = requests.post(
            "http://localhost:5000/api/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            
            if token:
                print(f"✅ Login bem-sucedido! Token: {token[:20]}...")
                return token
            else:
                print("❌ Login falhou - token não encontrado")
                return None
        else:
            print(f"❌ Login falhou - Status: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Erro no login: {e}")
        return None

def test_btc_apis(token):
    """Testa as APIs BTC com token válido"""
    print("\n📊 Testando APIs BTC...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Lista de APIs para testar
    apis = [
        "/api/btc-signals/status",
        "/api/btc-signals/pending",
        "/api/btc-signals/metrics",
        "/api/btc-signals/rejected?limit=5"
    ]
    
    for api in apis:
        try:
            print(f"\n🔍 Testando: {api}")
            response = requests.get(
                f"http://localhost:5000{api}",
                headers=headers
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Sucesso! Dados: {json.dumps(data, indent=2)[:200]}...")
            else:
                print(f"❌ Erro: {response.text}")
                
        except Exception as e:
            print(f"❌ Erro na API {api}: {e}")

def main():
    """Função principal"""
    print("🧪 Iniciando teste de login admin e APIs BTC...")
    
    # Testar login
    token = test_admin_login()
    
    if token:
        # Testar APIs BTC
        test_btc_apis(token)
        print(f"\n🎯 Token para usar no frontend: {token}")
        print("\n💡 Para usar no frontend:")
        print(f"   localStorage.setItem('token', '{token}');")
    else:
        print("\n❌ Não foi possível obter token. Verifique as credenciais.")
        print("\n🔑 Credenciais testadas:")
        print("   Email: jonatasprojetos2013@gmail.com")
        print("   Senha: admin123")
        print("\n💡 Tente outras senhas comuns: admin, 123456, password")

if __name__ == "__main__":
    main()