#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para criar usuário administrador inicial
"""

import bcrypt
import uuid
from core.database import Database

def create_admin_user():
    """Cria um usuário administrador inicial"""
    print("=== Criando Usuário Administrador ===")
    
    # Dados do usuário admin
    username = "admin"
    email = "jonatasprojetos2013@gmail.com"  # E-mail solicitado
    password = "admin123"  # Senha padrão - ALTERE em produção!
    
    # Criar hash da senha
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Dados do usuário
    user_data = {
        'id': str(uuid.uuid4()),
        'username': username,
        'email': email,
        'password': password_hash,
        'is_admin': True
    }
    
    # Criar instância do banco
    db = Database()
    
    # Verificar se usuário já existe
    existing_user = db.get_user_by_username(username)
    if existing_user:
        print(f"⚠️ Usuário '{username}' já existe!")
        return False
    
    # Verificar se e-mail já existe (se o método existir)
    try:
        existing_email = db.get_user_by_email(email)
        if existing_email:
            print(f"⚠️ E-mail '{email}' já está em uso!")
            return False
    except AttributeError:
        # Método get_user_by_email não existe ainda
        pass
    
    # Adicionar usuário
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
    create_admin_user()