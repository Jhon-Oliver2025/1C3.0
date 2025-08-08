#!/usr/bin/env python3
"""
Script para verificar se o ambiente está pronto para deploy
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_files():
    """
    Verifica se todos os arquivos necessários existem
    """
    print("📁 Verificando arquivos necessários...")
    
    required_files = [
        'back/app.py',
        'back/api.py',
        'back/config.py',
        'back/healthcheck.py',
        'back/pre_healthcheck.py',
        'back/requirements.txt',
        'back/Dockerfile',
        'docker-compose.coolify.yml',
        'front/package.json'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Arquivos faltando: {', '.join(missing_files)}")
        return False
    
    print("✅ Todos os arquivos necessários estão presentes")
    return True

def check_docker_compose():
    """
    Verifica se o docker-compose.coolify.yml está válido
    """
    print("🐳 Verificando docker-compose.coolify.yml...")
    
    try:
        result = subprocess.run(
            ['docker-compose', '-f', 'docker-compose.coolify.yml', 'config'],
            capture_output=True, text=True, timeout=30
        )
        
        if result.returncode == 0:
            print("✅ docker-compose.coolify.yml é válido")
            return True
        else:
            print(f"❌ Erro no docker-compose.coolify.yml: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Timeout ao verificar docker-compose")
        return False
    except FileNotFoundError:
        print("⚠️ docker-compose não encontrado, pulando verificação")
        return True
    except Exception as e:
        print(f"❌ Erro ao verificar docker-compose: {e}")
        return False

def check_environment_template():
    """
    Verifica se as variáveis de ambiente estão documentadas
    """
    print("🔧 Verificando template de variáveis de ambiente...")
    
    required_env_vars = [
        'DATABASE_URL',
        'REDIS_URL',
        'SECRET_KEY',
        'JWT_SECRET',
        'BINANCE_API_KEY',
        'BINANCE_SECRET_KEY',
        'TELEGRAM_BOT_TOKEN',
        'TELEGRAM_CHAT_ID',
        'SENDPULSE_CLIENT_ID',
        'SENDPULSE_CLIENT_SECRET',
        'SENDPULSE_SENDER_EMAIL',
        'POSTGRES_PASSWORD'
    ]
    
    # Verificar se estão no docker-compose.coolify.yml
    try:
        with open('docker-compose.coolify.yml', 'r') as f:
            content = f.read()
            
        missing_vars = []
        for var in required_env_vars:
            if var not in content:
                missing_vars.append(var)
        
        if missing_vars:
            print(f"⚠️ Variáveis não encontradas no docker-compose: {', '.join(missing_vars)}")
        else:
            print("✅ Todas as variáveis de ambiente estão no docker-compose")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar variáveis de ambiente: {e}")
        return False

def check_healthcheck_scripts():
    """
    Verifica se os scripts de healthcheck podem ser executados
    """
    print("🏥 Verificando scripts de healthcheck...")
    
    try:
        # Verificar sintaxe do pre_healthcheck.py
        result = subprocess.run(
            ['python', '-m', 'py_compile', 'back/pre_healthcheck.py'],
            capture_output=True, text=True, timeout=10
        )
        
        if result.returncode != 0:
            print(f"❌ Erro de sintaxe em pre_healthcheck.py: {result.stderr}")
            return False
        
        # Verificar sintaxe do healthcheck.py
        result = subprocess.run(
            ['python', '-m', 'py_compile', 'back/healthcheck.py'],
            capture_output=True, text=True, timeout=10
        )
        
        if result.returncode != 0:
            print(f"❌ Erro de sintaxe em healthcheck.py: {result.stderr}")
            return False
        
        print("✅ Scripts de healthcheck estão sintaticamente corretos")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar scripts de healthcheck: {e}")
        return False

def check_git_status():
    """
    Verifica se todas as alterações foram commitadas
    """
    print("📝 Verificando status do Git...")
    
    try:
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            capture_output=True, text=True, timeout=10
        )
        
        if result.stdout.strip():
            print("⚠️ Há alterações não commitadas:")
            print(result.stdout)
            return False
        else:
            print("✅ Todas as alterações foram commitadas")
            return True
            
    except Exception as e:
        print(f"❌ Erro ao verificar Git: {e}")
        return False

def main():
    """
    Executa todas as verificações
    """
    print("🚀 Verificando prontidão para deploy...\n")
    
    checks = [
        ("Arquivos necessários", check_files),
        ("Docker Compose", check_docker_compose),
        ("Variáveis de ambiente", check_environment_template),
        ("Scripts de healthcheck", check_healthcheck_scripts),
        ("Status do Git", check_git_status)
    ]
    
    all_passed = True
    results = []
    
    for check_name, check_func in checks:
        print(f"\n📋 {check_name}...")
        try:
            result = check_func()
            results.append((check_name, result))
            if not result:
                all_passed = False
        except Exception as e:
            print(f"❌ Erro inesperado em {check_name}: {e}")
            results.append((check_name, False))
            all_passed = False
    
    # Resumo final
    print("\n" + "="*50)
    print("📊 RESUMO DAS VERIFICAÇÕES")
    print("="*50)
    
    for check_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{check_name}: {status}")
    
    print("\n" + "="*50)
    
    if all_passed:
        print("🎉 TODAS AS VERIFICAÇÕES PASSARAM!")
        print("✅ O ambiente está pronto para deploy no Coolify")
        print("\n📋 Próximos passos:")
        print("1. Fazer um novo deploy no Coolify")
        print("2. Monitorar os logs durante o deploy")
        print("3. Verificar se o healthcheck passa")
        print("4. Testar a aplicação após o deploy")
        return True
    else:
        print("💥 ALGUMAS VERIFICAÇÕES FALHARAM!")
        print("❌ Corrija os problemas antes de fazer deploy")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)