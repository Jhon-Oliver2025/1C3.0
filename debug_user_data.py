#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para debugar dados do usuário
"""

import requests
import json

def debug_user_data():
    """Debug dos dados do usuário"""
    print("🔍 Debugando dados do usuário...")
    
    # Fazer login
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
            user = data.get('user', {})
            
            print("\n📊 Dados do usuário retornados pelo login:")
            print(json.dumps(user, indent=2))
            
            print("\n🔍 Análise detalhada:")
            print(f"  is_admin value: {user.get('is_admin')}")
            print(f"  is_admin type: {type(user.get('is_admin'))}")
            print(f"  is_admin == True: {user.get('is_admin') == True}")
            print(f"  is_admin == 'True': {user.get('is_admin') == 'True'}")
            print(f"  bool(is_admin): {bool(user.get('is_admin'))}")
            
            # Testar verificação como nas rotas BTC
            is_admin_check = user.get('is_admin')
            print(f"\n🧪 Teste de verificação admin:")
            print(f"  user_data.get('is_admin'): {is_admin_check}")
            print(f"  not user_data.get('is_admin'): {not is_admin_check}")
            
            if not is_admin_check:
                print("  ❌ Verificação falharia - usuário seria rejeitado")
            else:
                print("  ✅ Verificação passaria - usuário seria aceito")
                
            # Testar com conversão
            if isinstance(is_admin_check, str):
                is_admin_bool = is_admin_check.lower() == 'true'
                print(f"\n🔄 Conversão string para bool:")
                print(f"  is_admin_check.lower() == 'true': {is_admin_bool}")
                
        else:
            print(f"❌ Login falhou: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

def main():
    debug_user_data()

if __name__ == "__main__":
    main()