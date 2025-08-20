#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar diretamente a API BTC e verificar se está acessando a instância correta
"""

import requests
import json

def test_api_btc_direct():
    print("🔍 Testando API BTC diretamente...")
    
    try:
        # 1. Testar métricas BTC (requer token admin)
        print("\n📊 1. TESTANDO MÉTRICAS BTC...")
        # Usar um token admin válido (você pode precisar ajustar)
        admin_token = "cdbefac2-ce4a-4eb2-b011-c7a5cd0258ae"  # Token de exemplo
        
        response = requests.get(
            "http://localhost:5000/api/btc-signals/metrics",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Métricas BTC obtidas com sucesso")
            if 'data' in data:
                metrics = data['data']
                print(f"   Sinais processados: {metrics.get('total_signals_processed', 'N/A')}")
                print(f"   Sinais confirmados: {metrics.get('confirmed_signals', 'N/A')}")
                print(f"   Sinais pendentes: {metrics.get('pending_signals', 'N/A')}")
                print(f"   Taxa de confirmação: {metrics.get('confirmation_rate', 'N/A')}%")
        else:
            print(f"❌ Erro ao obter métricas: {response.status_code}")
            print(f"   Resposta: {response.text[:200]}")
        
        # 2. Testar sinais confirmados (público)
        print("\n📋 2. TESTANDO SINAIS CONFIRMADOS (PÚBLICO)...")
        response = requests.get("http://localhost:5000/api/btc-signals/confirmed")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sinais confirmados: {len(data)} encontrados")
            
            if data:
                print("\n📊 Primeiro sinal confirmado:")
                signal = data[0]
                for key, value in signal.items():
                    print(f"   {key}: {value}")
            else:
                print("⚠️ Nenhum sinal confirmado retornado")
        else:
            print(f"❌ Erro ao obter sinais confirmados: {response.status_code}")
        
        # 3. Testar status do sistema BTC (requer token admin)
        print("\n🔧 3. TESTANDO STATUS DO SISTEMA BTC...")
        response = requests.get(
            "http://localhost:5000/api/btc-signals/status",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Status do sistema obtido")
            if 'data' in data:
                status = data['data']
                print(f"   Sistema ativo: {status.get('is_monitoring', 'N/A')}")
                print(f"   Thread ativa: {status.get('monitoring_thread_active', 'N/A')}")
                print(f"   Sinais pendentes: {status.get('pending_signals', 'N/A')}")
                print(f"   Sinais confirmados: {status.get('confirmed_signals', 'N/A')}")
                print(f"   Sinais rejeitados: {status.get('rejected_signals', 'N/A')}")
        else:
            print(f"❌ Erro ao obter status: {response.status_code}")
            print(f"   Resposta: {response.text[:200]}")
        
        # 4. Testar sinais pendentes (requer token admin)
        print("\n⏳ 4. TESTANDO SINAIS PENDENTES...")
        response = requests.get(
            "http://localhost:5000/api/btc-signals/pending",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Sinais pendentes obtidos")
            if 'data' in data and 'pending_signals' in data['data']:
                pending_count = len(data['data']['pending_signals'])
                print(f"   Sinais pendentes: {pending_count}")
                
                if pending_count > 0:
                    print("\n📋 Primeiro sinal pendente:")
                    signal = data['data']['pending_signals'][0]
                    print(f"   Symbol: {signal.get('symbol')}")
                    print(f"   Type: {signal.get('type')}")
                    print(f"   Created: {signal.get('created_at')}")
                    print(f"   Attempts: {signal.get('confirmation_attempts')}")
        else:
            print(f"❌ Erro ao obter sinais pendentes: {response.status_code}")
            print(f"   Resposta: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_api_btc_direct()