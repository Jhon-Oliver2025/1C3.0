#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar login do usuário admin
"""

import bcrypt
from core.database import Database

def test_admin_login():
    """Testa o login do usuário admin"""
    print("=== Testando Login do Admin ===")
    
    # Dados de teste
    username = "admin"
    password = "admin123"
    
    # Criar instância do banco
    db = Database()
    
    # Buscar usuário
    user = db.get_user_by_username(username)
    if not user:
        print(f"❌ Usuário '{username}' não encontrado!")
        return False
    
    print(f"✅ Usuário encontrado:")
    print(f"   Username: {user.get('username')}")
    print(f"   Email: {user.get('email')}")
    print(f"   Status: {user.get('status')}")
    print(f"   Is Admin: {user.get('is_admin')}")
    print(f"   Password Hash: {user.get('password')[:50]}...")
    
    # Testar senha
    stored_password = user.get('password', '')
    if stored_password.startswith('$2b$'):
        # Senha com hash bcrypt
        if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
            print(f"✅ Senha '{password}' está CORRETA!")
            return True
        else:
            print(f"❌ Senha '{password}' está INCORRETA!")
            return False
    else:
        print(f"❌ Hash da senha não está no formato bcrypt!")
        return False

if __name__ == "__main__":
    test_admin_login()