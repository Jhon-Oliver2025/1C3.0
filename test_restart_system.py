#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Teste do Sistema de Restart às 21:00
Verifica se o sistema de limpeza automática está funcionando corretamente
"""

import sys
import os
import requests
import json
from datetime import datetime
import pytz

# Adicionar o diretório back ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'back'))

def test_local_system():
    """Testa o sistema localmente"""
    print("🧪 TESTE LOCAL DO SISTEMA DE RESTART")
    print("="*60)
    
    try:
        from back.core.signal_cleanup import cleanup_system
        
        # Verificar status do sistema
        print("📊 Status do sistema:")
        status = cleanup_system.get_system_status()
        
        for key, value in status.items():
            print(f"   {key}: {value}")
        
        print("\n⏰ Informações de horário:")
        tz = pytz.timezone('America/Sao_Paulo')
        now = datetime.now(tz)
        print(f"   Horário atual SP: {now.strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"   Próximo restart: {cleanup_system.get_next_restart_time()}")
        
        time_until = cleanup_system.get_time_until_restart()
        print(f"   Tempo até restart: {time_until['hours']}h {time_until['minutes']}m {time_until['seconds']}s")
        
        # Verificar se o sistema está rodando
        if status['is_running'] and status['thread_active']:
            print("\n✅ Sistema está funcionando corretamente!")
            print("🔄 O restart será executado automaticamente às 21:00")
        else:
            print("\n❌ Sistema NÃO está funcionando!")
            print("🚨 Verifique se o sistema foi inicializado corretamente")
            
            # Tentar iniciar o sistema
            print("\n🚀 Tentando iniciar o sistema...")
            cleanup_system.start_scheduler()
            
            # Verificar novamente
            status = cleanup_system.get_system_status()
            if status['is_running'] and status['thread_active']:
                print("✅ Sistema iniciado com sucesso!")
            else:
                print("❌ Falha ao iniciar o sistema")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste local: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_endpoints():
    """Testa os endpoints da API"""
    print("\n🌐 TESTE DOS ENDPOINTS DA API")
    print("="*60)
    
    base_url = "http://localhost:5000"  # Ajuste conforme necessário
    
    # Testar endpoint de status
    try:
        print("📡 Testando endpoint de status...")
        response = requests.get(f"{base_url}/api/scheduler/restart-system-status")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Endpoint de status funcionando!")
            print(f"   Status: {data.get('status')}")
            
            restart_system = data.get('restart_system', {})
            print(f"   Sistema ativo: {restart_system.get('is_running')}")
            print(f"   Thread ativa: {restart_system.get('thread_active')}")
            print(f"   Horário atual: {restart_system.get('current_time_sp')}")
            print(f"   Próximo restart: {restart_system.get('next_restart')}")
        else:
            print(f"❌ Erro no endpoint: {response.status_code}")
            print(f"   Resposta: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Não foi possível conectar à API")
        print("   Verifique se o backend está rodando")
    except Exception as e:
        print(f"❌ Erro ao testar API: {e}")

def main():
    """Função principal"""
    print("🔍 DIAGNÓSTICO COMPLETO DO SISTEMA DE RESTART")
    print("="*80)
    
    # Teste local
    local_success = test_local_system()
    
    # Teste da API
    test_api_endpoints()
    
    print("\n📋 RESUMO DO DIAGNÓSTICO")
    print("="*40)
    
    if local_success:
        print("✅ Sistema local: FUNCIONANDO")
        print("\n🎯 PRÓXIMOS PASSOS:")
        print("1. O sistema executará automaticamente às 21:00")
        print("2. Monitore os logs para confirmar a execução")
        print("3. Use os endpoints da API para monitoramento")
        print("\n📡 Endpoints disponíveis:")
        print("   GET /api/scheduler/restart-system-status")
        print("   POST /api/scheduler/test-restart")
    else:
        print("❌ Sistema local: COM PROBLEMAS")
        print("\n🔧 AÇÕES NECESSÁRIAS:")
        print("1. Verifique se o backend está rodando")
        print("2. Verifique os logs de erro")
        print("3. Reinicie o sistema se necessário")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main()
    input("\nPressione Enter para sair...")