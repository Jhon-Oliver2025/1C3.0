#!/usr/bin/env python3
"""
Script de healthcheck mais robusto para o backend Flask
"""

import sys
import time
import urllib.request
import urllib.error
import json
import subprocess

def run_pre_checks():
    """
    Executa pré-verificações de serviços
    
    Returns:
        bool: True se todas as pré-verificações passaram
    """
    try:
        print("🔧 Executando pré-verificações...")
        result = subprocess.run(["python", "pre_healthcheck.py"], 
                              capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ Pré-verificações passaram")
            return True
        else:
            print(f"❌ Pré-verificações falharam: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Timeout nas pré-verificações")
        return False
    except Exception as e:
        print(f"❌ Erro nas pré-verificações: {e}")
        return False

def check_health(max_retries=10, delay=5):
    """
    Verifica a saúde da aplicação Flask
    
    Args:
        max_retries (int): Número máximo de tentativas
        delay (int): Delay entre tentativas em segundos
    
    Returns:
        bool: True se saudável, False caso contrário
    """
    url = "http://localhost:5000/api/health"
    
    for attempt in range(max_retries):
        try:
            print(f"🔍 Tentativa {attempt + 1}/{max_retries} - Verificando {url}")
            
            # Fazer requisição HTTP
            with urllib.request.urlopen(url, timeout=10) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    print(f"✅ Healthcheck passou: {data}")
                    return True
                else:
                    print(f"❌ Status HTTP inválido: {response.status}")
                    
        except urllib.error.URLError as e:
            print(f"❌ Erro de conexão (tentativa {attempt + 1}): {e}")
        except json.JSONDecodeError as e:
            print(f"❌ Erro ao decodificar JSON: {e}")
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
        
        if attempt < max_retries - 1:
            print(f"⏳ Aguardando {delay}s antes da próxima tentativa...")
            time.sleep(delay)
    
    print(f"💥 Healthcheck falhou após {max_retries} tentativas")
    return False

if __name__ == "__main__":
    print("🚀 Iniciando healthcheck...")
    time.sleep(30)  # Aguardar 30s para a aplicação inicializar completamente
    
    # Executar pré-verificações primeiro
    if not run_pre_checks():
        print("💥 Pré-verificações falharam, abortando healthcheck")
        sys.exit(1)
    
    # Se pré-verificações passaram, testar endpoint HTTP
    success = check_health(max_retries=15, delay=10)
    sys.exit(0 if success else 1)