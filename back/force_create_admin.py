#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para forçar a criação do usuário administrador
"""

import bcrypt
import uuid
import os
import pandas as pd
from core.database import Database

def force_create_admin_user():
    """Força a criação de um usuário administrador"""
    print("=== Forçando Criação do Usuário Administrador ===")
    
    # Dados do usuário admin
    username = "admin"
    email = "jonatasprojetos2013@gmail.com"
    password = "admin123"
    
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
    
    # Criar instância do banco
    db = Database()
    
    # Remover usuário existente se houver
    try:
        users = db.get_all_users()
        users_filtered = [u for u in users if u.get('username') != username and u.get('email') != email]
        
        # Salvar usuários filtrados
        if users_filtered:
            df = pd.DataFrame(users_filtered)
        else:
            df = pd.DataFrame(columns=['id', 'username', 'email', 'password', 'is_admin', 'status'])
        
        # Garantir que o diretório existe
        os.makedirs(os.path.dirname(db.users_file), exist_ok=True)
        
        # Salvar arquivo
        df.to_csv(db.users_file, index=False)
        print(f"✅ Usuários existentes removidos")
        
    except Exception as e:
        print(f"⚠️ Erro ao limpar usuários: {e}")
    
    # Adicionar novo usuário admin
    if db.add_user(user_data):
        print(f"✅ Usuário administrador criado com sucesso!")
        print(f"   Username: {username}")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        print(f"   ID: {user_data['id']}")
        print("\n⚠️ IMPORTANTE: Altere a senha após o primeiro login!")
        return True
    else:
        print("❌ Erro ao criar usuário administrador")
        return False

if __name__ == "__main__":
    force_create_admin_user()