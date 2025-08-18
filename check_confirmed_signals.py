#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar sinais confirmados e investigar discrepância nos números
"""

import requests
import json

def check_confirmed_signals():
    """Verifica sinais confirmados e analisa discrepância"""
    token = '2c6c6d34-1dba-4b30-86e1-a2cb3af69622'
    
    try:
        # Verificar sinais confirmados
        response = requests.get(
            "http://localhost:5000/api/btc-signals/confirmed?limit=50",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print("=== ANÁLISE DE SINAIS CONFIRMADOS ===")
            print(f"Status: {response.status_code}")
            print(f"Total confirmados (count): {data['data']['count']}")
            print(f"Sinais retornados: {len(data['data']['confirmed_signals'])}")
            print(f"Última atualização: {data['data']['last_updated']}")
            
            if data['data']['confirmed_signals']:
                print("\n=== PRIMEIRO SINAL CONFIRMADO ===")
                first_signal = data['data']['confirmed_signals'][0]
                for key, value in first_signal.items():
                    print(f"{key}: {value}")
                    
                print("\n=== ÚLTIMOS 5 SINAIS CONFIRMADOS ===")
                for i, signal in enumerate(data['data']['confirmed_signals'][:5]):
                    print(f"\n{i+1}. {signal['symbol']} - {signal['type']}")
                    print(f"   Criado: {signal.get('created_at', 'N/A')}")
                    print(f"   Confirmado: {signal.get('confirmed_at', 'N/A')}")
                    print(f"   Entrada: {signal.get('entry_price', 'N/A')}")
                    print(f"   Alvo: {signal.get('target_price', 'N/A')}")
            else:
                print("\n❌ Nenhum sinal confirmado encontrado")
                
        else:
            print(f"❌ Erro: {response.status_code} - {response.text}")
            
        # Verificar também a API principal de sinais (dashboard)
        print("\n=== VERIFICANDO API PRINCIPAL (DASHBOARD) ===")
        response_main = requests.get(
            "http://localhost:5000/api/signals",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response_main.status_code == 200:
            main_data = response_main.json()
            print(f"Status API principal: {response_main.status_code}")
            
            # Verificar se é uma lista ou objeto
            if isinstance(main_data, list):
                signals_list = main_data
                print(f"Sinais na API principal: {len(signals_list)}")
            elif isinstance(main_data, dict) and 'signals' in main_data:
                signals_list = main_data['signals']
                print(f"Sinais na API principal: {len(signals_list)}")
            else:
                print(f"Formato inesperado da API: {type(main_data)}")
                print(f"Chaves disponíveis: {list(main_data.keys()) if isinstance(main_data, dict) else 'N/A'}")
                signals_list = []
            
            if signals_list:
                print("\n=== PRIMEIRO SINAL DA API PRINCIPAL ===")
                first_main = signals_list[0]
                print(f"Symbol: {first_main.get('symbol')}")
                print(f"Type: {first_main.get('type')}")
                print(f"Entry: {first_main.get('entry_price')}")
                print(f"Target: {first_main.get('target_price')}")
                print(f"Created: {first_main.get('created_at')}")
                print(f"Confirmed: {first_main.get('confirmed_at')}")
                print(f"Projection: {first_main.get('projection_percentage')}")
                
                print("\n=== VERIFICANDO DATAS/HORÁRIOS ===")
                signals_without_dates = 0
                for i, signal in enumerate(signals_list[:10]):
                    if not signal.get('created_at') or not signal.get('confirmed_at'):
                        signals_without_dates += 1
                        print(f"Sinal {i+1} ({signal.get('symbol')}) sem datas completas:")
                        print(f"  Created: {signal.get('created_at')}")
                        print(f"  Confirmed: {signal.get('confirmed_at')}")
                        
                print(f"\nSinais sem datas completas: {signals_without_dates}/10")
            else:
                print("\n❌ Nenhum sinal encontrado na API principal")
        else:
            print(f"❌ Erro API principal: {response_main.status_code}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

def main():
    check_confirmed_signals()

if __name__ == "__main__":
    main()