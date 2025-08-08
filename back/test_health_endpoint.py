#!/usr/bin/env python3
"""
Script para testar o endpoint de health da aplicação Flask.
Útil para debugging e verificação manual do healthcheck.
"""

import requests
import time
import sys
import os
from urllib.parse import urljoin

def test_health_endpoint(base_url="http://localhost:5000", max_attempts=10, delay=5):
    """
    Testa o endpoint de health da aplicação.
    
    Args:
        base_url (str): URL base da aplicação
        max_attempts (int): Número máximo de tentativas
        delay (int): Delay entre tentativas em segundos
    
    Returns:
        bool: True se o endpoint responder corretamente, False caso contrário
    """
    health_url = urljoin(base_url, "/api/health")
    
    print(f"🔍 Testando endpoint de health: {health_url}")
    print(f"📊 Máximo de {max_attempts} tentativas com {delay}s de intervalo")
    print("-" * 60)
    
    for attempt in range(1, max_attempts + 1):
        try:
            print(f"🔄 Tentativa {attempt}/{max_attempts}...")
            
            # Fazer requisição com timeout
            response = requests.get(health_url, timeout=10)
            
            print(f"📡 Status Code: {response.status_code}")
            print(f"📄 Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"✅ Response JSON: {data}")
                    
                    # Verificar se a resposta contém os campos esperados
                    if isinstance(data, dict) and data.get('status') == 'healthy':
                        print(f"🎉 Endpoint de health funcionando corretamente!")
                        return True
                    else:
                        print(f"⚠️ Resposta inesperada: {data}")
                        
                except ValueError as e:
                    print(f"⚠️ Resposta não é JSON válido: {response.text[:200]}")
                    
            else:
                print(f"❌ Status code inesperado: {response.status_code}")
                print(f"📄 Response: {response.text[:200]}")
                
        except requests.exceptions.ConnectionError as e:
            print(f"🔌 Erro de conexão: {e}")
        except requests.exceptions.Timeout as e:
            print(f"⏰ Timeout: {e}")
        except requests.exceptions.RequestException as e:
            print(f"🌐 Erro de requisição: {e}")
        except Exception as e:
            print(f"💥 Erro inesperado: {e}")
        
        if attempt < max_attempts:
            print(f"⏳ Aguardando {delay}s antes da próxima tentativa...")
            time.sleep(delay)
        
        print("-" * 40)
    
    print(f"❌ Falha após {max_attempts} tentativas")
    return False

def main():
    """
    Função principal do script.
    """
    print("🏥 Teste do Endpoint de Health")
    print("=" * 60)
    
    # Verificar argumentos da linha de comando
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
    
    # Verificar variáveis de ambiente
    flask_port = os.getenv('FLASK_PORT', '5000')
    if base_url == "http://localhost:5000" and flask_port != '5000':
        base_url = f"http://localhost:{flask_port}"
    
    print(f"🎯 URL alvo: {base_url}")
    print(f"🔍 Porta Flask: {flask_port}")
    print()
    
    # Executar teste
    success = test_health_endpoint(base_url)
    
    # Resultado final
    print("=" * 60)
    if success:
        print("✅ SUCESSO: Endpoint de health está funcionando!")
        sys.exit(0)
    else:
        print("❌ FALHA: Endpoint de health não está respondendo corretamente")
        sys.exit(1)

if __name__ == "__main__":
    main()