#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para diagnosticar problemas do BTCSignalManager em produção
Verifica por que os sinais confirmados não estão aparecendo na aba
"""

import requests
import json
from datetime import datetime
import sys
import os

def diagnose_production_btc():
    """
    Diagnostica problemas do sistema BTC em produção
    """
    print("\n" + "="*80)
    print("🔍 DIAGNÓSTICO DO SISTEMA BTC EM PRODUÇÃO")
    print("="*80)
    
    # URLs para testar (ajustar conforme necessário)
    base_urls = [
        "http://localhost:5000",  # Desenvolvimento
        # Adicionar URL de produção aqui se necessário
    ]
    
    for base_url in base_urls:
        print(f"\n🌐 Testando: {base_url}")
        print("-" * 50)
        
        try:
            # 1. Testar status da API
            print("\n1. TESTANDO STATUS DA API...")
            response = requests.get(f"{base_url}/api/status", timeout=10)
            if response.status_code == 200:
                print("✅ API Status: OK")
            else:
                print(f"❌ API Status: {response.status_code}")
                continue
            
            # 2. Testar endpoint de sinais confirmados (público)
            print("\n2. TESTANDO SINAIS CONFIRMADOS (PÚBLICO)...")
            response = requests.get(f"{base_url}/api/btc-signals/confirmed", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Sinais confirmados: {len(data)} encontrados")
                
                if data:
                    print("\n📊 Exemplo de sinal confirmado:")
                    signal = data[0]
                    for key, value in signal.items():
                        print(f"   {key}: {value}")
                else:
                    print("⚠️ Nenhum sinal confirmado encontrado")
            else:
                print(f"❌ Erro ao obter sinais confirmados: {response.status_code}")
                print(f"   Resposta: {response.text[:200]}...")
            
            # 3. Testar métricas BTC (requer autenticação)
            print("\n3. TESTANDO MÉTRICAS BTC...")
            # Tentar sem token primeiro
            response = requests.get(f"{base_url}/api/btc-signals/metrics", timeout=10)
            if response.status_code == 403:
                print("⚠️ Métricas BTC requerem autenticação (esperado)")
            elif response.status_code == 200:
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
            
            # 4. Verificar se há sinais pendentes
            print("\n4. VERIFICANDO SINAIS PENDENTES...")
            response = requests.get(f"{base_url}/api/btc-signals/pending", timeout=10)
            if response.status_code == 403:
                print("⚠️ Sinais pendentes requerem autenticação (esperado)")
            elif response.status_code == 200:
                data = response.json()
                if 'data' in data and 'pending_signals' in data['data']:
                    pending_count = len(data['data']['pending_signals'])
                    print(f"✅ Sinais pendentes: {pending_count}")
                else:
                    print("⚠️ Formato de resposta inesperado para sinais pendentes")
            else:
                print(f"❌ Erro ao obter sinais pendentes: {response.status_code}")
            
            # 5. Verificar status do sistema BTC
            print("\n5. VERIFICANDO STATUS DO SISTEMA BTC...")
            response = requests.get(f"{base_url}/api/btc-signals/status", timeout=10)
            if response.status_code == 403:
                print("⚠️ Status do sistema requer autenticação (esperado)")
            elif response.status_code == 200:
                data = response.json()
                print("✅ Status do sistema obtido")
                if 'data' in data:
                    status = data['data']
                    print(f"   Sistema ativo: {status.get('is_monitoring', 'N/A')}")
                    print(f"   Thread ativa: {status.get('monitoring_thread_active', 'N/A')}")
            else:
                print(f"❌ Erro ao obter status: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ Não foi possível conectar a {base_url}")
        except requests.exceptions.Timeout:
            print(f"❌ Timeout ao conectar a {base_url}")
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
    
    # 6. Diagnóstico de possíveis problemas
    print("\n" + "="*80)
    print("🔧 DIAGNÓSTICO DE POSSÍVEIS PROBLEMAS")
    print("="*80)
    
    print("\n📋 POSSÍVEIS CAUSAS:")
    print("1. BTCSignalManager não inicializado corretamente")
    print("2. Monitoramento não está ativo")
    print("3. Nenhum sinal foi confirmado ainda")
    print("4. Problema na API de sinais confirmados")
    print("5. Diferença entre ambiente de desenvolvimento e produção")
    
    print("\n🔧 SOLUÇÕES RECOMENDADAS:")
    print("1. Verificar logs do backend para erros de inicialização")
    print("2. Reiniciar o sistema BTC via API admin")
    print("3. Verificar se há sinais pendentes aguardando confirmação")
    print("4. Confirmar que o monitoramento está ativo")
    print("5. Verificar configurações específicas de produção")
    
    print("\n✅ Diagnóstico concluído!")

if __name__ == '__main__':
    diagnose_production_btc()