#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar get_user_by_token diretamente
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'back'))

from core.database import Database
import requests
import json

def test_token_flow():
    """Testa o fluxo completo do token"""
    print("🔍 Testando fluxo completo do token...")
    
    # 1. Fazer login e obter token
    login_data = {
        "username": "jonatasprojetos2013@gmail.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(
            "http://localhost:5000/api/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            user_from_login = data.get('user', {})
            
            print(f"✅ Login bem-sucedido! Token: {token[:20]}...")
            print(f"📊 Usuário do login: {json.dumps(user_from_login, indent=2)}")
            
            # 2. Testar get_user_by_token diretamente
            print("\n🔍 Testando get_user_by_token diretamente...")
            db = Database()
            user_from_token = db.get_user_by_token(token)
            
            print(f"📊 Usuário do token: {json.dumps(user_from_token, indent=2)}")
            
            if user_from_token:
                print(f"\n🧪 Análise do is_admin do token:")
                is_admin = user_from_token.get('is_admin')
                print(f"  is_admin value: {is_admin}")
                print(f"  is_admin type: {type(is_admin)}")
                print(f"  not user_data.get('is_admin'): {not is_admin}")
                
                # Verificação como nas rotas BTC
                if not user_from_token or not user_from_token.get('is_admin'):
                    print("  ❌ Verificação BTC falharia")
                else:
                    print("  ✅ Verificação BTC passaria")
                    
                # 3. Testar API BTC com token
                print("\n🔍 Testando API BTC com token...")
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
                
                btc_response = requests.get(
                    "http://localhost:5000/api/btc-signals/status",
                    headers=headers
                )
                
                print(f"Status API BTC: {btc_response.status_code}")
                print(f"Response: {btc_response.text[:200]}...")
                
            else:
                print("❌ get_user_by_token retornou None")
                
        else:
            print(f"❌ Login falhou: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

def main():
    test_token_flow()

if __name__ == "__main__":
    main()