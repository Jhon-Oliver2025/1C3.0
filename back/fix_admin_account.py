import bcrypt
import pandas as pd
import os

def fix_admin_account():
    """Corrige a conta admin com as credenciais corretas"""
    users_file = os.path.join(os.path.dirname(__file__), 'users.csv')
    
    # Gerar hash da nova senha
    password_hash = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Ler o arquivo atual
    df = pd.read_csv(users_file)
    
    # Atualizar a conta admin
    admin_index = df[df['username'] == 'admin'].index
    if not admin_index.empty:
        df.loc[admin_index, 'email'] = 'jontasprojetos2013@gmail.com'
        df.loc[admin_index, 'password'] = password_hash
        df.loc[admin_index, 'status'] = 'active'  # Adicionar coluna status
    
    # Salvar as alterações
    df.to_csv(users_file, index=False)
    print("✅ Conta admin corrigida!")

if __name__ == '__main__':
    fix_admin_account()