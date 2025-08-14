#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste para o sistema de limpeza de sinais
Testa todas as funcionalidades do scheduler e endpoints
"""

import requests
import json
import time
from datetime import datetime
import sys
import os

# Adicionar o diretório back ao path para imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_scheduler_endpoints(base_url="http://localhost:5000"):
    """
    Testa todos os endpoints do sistema de scheduler
    """
    print("🧪 === TESTE DO SISTEMA DE SCHEDULER ===")
    print(f"🌐 Base URL: {base_url}")
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Lista de endpoints para testar
    endpoints = [
        {
            'name': 'Health Check do Scheduler',
            'method': 'GET',
            'url': f'{base_url}/api/scheduler/health-check',
            'expected_status': 200
        },
        {
            'name': 'Status Detalhado do Scheduler',
            'method': 'GET',
            'url': f'{base_url}/api/scheduler/status',
            'expected_status': 200
        },
        {
            'name': 'Logs do Scheduler',
            'method': 'GET',
            'url': f'{base_url}/api/scheduler/logs',
            'expected_status': 200
        },
        {
            'name': 'Limpeza Manual (Morning)',
            'method': 'POST',
            'url': f'{base_url}/api/scheduler/manual-cleanup',
            'data': {'type': 'morning'},
            'expected_status': 200
        },
        {
            'name': 'Limpeza Manual (Evening)',
            'method': 'POST',
            'url': f'{base_url}/api/scheduler/manual-cleanup',
            'data': {'type': 'evening'},
            'expected_status': 200
        },
        {
            'name': 'Restart do Scheduler',
            'method': 'POST',
            'url': f'{base_url}/api/scheduler/restart',
            'expected_status': 200
        }
    ]
    
    results = []
    
    for endpoint in endpoints:
        print(f"🔍 Testando: {endpoint['name']}")
        
        try:
            if endpoint['method'] == 'GET':
                response = requests.get(endpoint['url'], timeout=30)
            elif endpoint['method'] == 'POST':
                data = endpoint.get('data', {})
                response = requests.post(
                    endpoint['url'], 
                    json=data, 
                    headers={'Content-Type': 'application/json'},
                    timeout=30
                )
            
            # Verificar status code
            status_ok = response.status_code == endpoint['expected_status']
            
            # Tentar parsear JSON
            try:
                json_data = response.json()
                json_ok = True
            except:
                json_data = None
                json_ok = False
            
            result = {
                'name': endpoint['name'],
                'url': endpoint['url'],
                'method': endpoint['method'],
                'status_code': response.status_code,
                'expected_status': endpoint['expected_status'],
                'status_ok': status_ok,
                'json_ok': json_ok,
                'response_data': json_data,
                'success': status_ok and json_ok
            }
            
            results.append(result)
            
            if result['success']:
                print(f"   ✅ Sucesso - Status: {response.status_code}")
                if json_data and 'message' in json_data:
                    print(f"   📝 Mensagem: {json_data['message']}")
            else:
                print(f"   ❌ Falha - Status: {response.status_code} (esperado: {endpoint['expected_status']})")
                if not json_ok:
                    print(f"   📝 Resposta: {response.text[:200]}...")
                elif json_data and 'error' in json_data:
                    print(f"   📝 Erro: {json_data['error']}")
            
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Erro de conexão: {e}")
            results.append({
                'name': endpoint['name'],
                'url': endpoint['url'],
                'method': endpoint['method'],
                'error': str(e),
                'success': False
            })
        
        print()
        time.sleep(1)  # Pequena pausa entre requests
    
    # Resumo dos resultados
    print("📊 === RESUMO DOS TESTES ===")
    successful = sum(1 for r in results if r.get('success', False))
    total = len(results)
    
    print(f"✅ Sucessos: {successful}/{total}")
    print(f"❌ Falhas: {total - successful}/{total}")
    print(f"📈 Taxa de sucesso: {(successful/total)*100:.1f}%")
    
    if successful == total:
        print("🎉 Todos os testes passaram! Sistema funcionando corretamente.")
    else:
        print("⚠️ Alguns testes falharam. Verifique os logs acima.")
    
    return results

def test_local_scheduler():
    """
    Testa o scheduler localmente (sem servidor web)
    """
    print("🧪 === TESTE LOCAL DO SCHEDULER ===")
    
    try:
        # Importar módulos locais
        from market_scheduler import setup_market_scheduler, is_scheduler_running
        from core.database import Database
        from core.gerenciar_sinais import GerenciadorSinais
        
        print("✅ Imports realizados com sucesso")
        
        # Inicializar componentes
        print("🔧 Inicializando componentes...")
        db = Database()
        gerenciador = GerenciadorSinais(db)
        
        print("✅ Componentes inicializados")
        
        # Testar configuração do scheduler
        print("⚙️ Configurando scheduler...")
        scheduler_instance = setup_market_scheduler(db, gerenciador)
        
        if scheduler_instance:
            print("✅ Scheduler configurado com sucesso")
            
            # Verificar se está rodando
            if is_scheduler_running():
                print("✅ Scheduler está rodando")
                
                # Listar jobs
                jobs = scheduler_instance.get_jobs()
                print(f"📅 Jobs configurados: {len(jobs)}")
                
                for job in jobs:
                    print(f"   • {job.name} - Próxima execução: {job.next_run_time}")
                
                return True
            else:
                print("❌ Scheduler não está rodando")
                return False
        else:
            print("❌ Falha ao configurar scheduler")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste local: {e}")
        import traceback
        print(f"📝 Traceback: {traceback.format_exc()}")
        return False

def main():
    """
    Função principal - executa todos os testes
    """
    print("🚀 === INICIANDO TESTES DO SISTEMA DE SCHEDULER ===")
    print(f"📅 Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Teste 1: Scheduler local
    print("1️⃣ Testando scheduler localmente...")
    local_test_success = test_local_scheduler()
    print()
    
    # Teste 2: Endpoints da API (se o servidor estiver rodando)
    print("2️⃣ Testando endpoints da API...")
    try:
        api_results = test_scheduler_endpoints()
        api_test_success = all(r.get('success', False) for r in api_results)
    except Exception as e:
        print(f"❌ Erro nos testes da API: {e}")
        api_test_success = False
    
    print()
    print("🏁 === RESULTADO FINAL ===")
    print(f"🔧 Teste Local: {'✅ Passou' if local_test_success else '❌ Falhou'}")
    print(f"🌐 Teste API: {'✅ Passou' if api_test_success else '❌ Falhou'}")
    
    if local_test_success and api_test_success:
        print("🎉 Todos os testes passaram! Sistema pronto para produção.")
        return True
    else:
        print("⚠️ Alguns testes falharam. Verifique os problemas antes do deploy.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)