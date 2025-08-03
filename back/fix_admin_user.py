#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corrigir o usuário administrador
"""

import bcrypt
import uuid
import pandas as pd
import os
from core.database import Database

def fix_admin_user():
    """Corrige o usuário administrador"""
    print("=== Corrigindo Usuário Administrador ===")
    
    # Dados corretos do usuário admin
    username = "admin"
    email = "jonatasprojetos2013@gmail.com"  # Email correto
    password = "admin123"
    
    # Criar instância do banco
    db = Database()
    
    # Remover usuário existente se houver
    users_file = db.users_file
    if os.path.exists(users_file):
        df = pd.read_csv(users_file)
        # Remover usuário admin existente
        df = df[df['username'] != username]
        df.to_csv(users_file, index=False)
        print(f"✅ Usuário admin existente removido")
    
    # Criar hash da senha
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Dados do usuário
    user_data = {
        'id': str(uuid.uuid4()),
        'username': username,
        'email': email,
        'password': password_hash,
        'is_admin': True,
        'status': 'active'
    }
    
    # Adicionar usuário
    if db.add_user(user_data):
        print(f"✅ Usuário administrador corrigido com sucesso!")
        print(f"   Username: {username}")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        print(f"   ID: {user_data['id']}")
        return True
    else:
        print("❌ Erro ao corrigir usuário administrador")
        return False

if __name__ == "__main__":
    fix_admin_user()