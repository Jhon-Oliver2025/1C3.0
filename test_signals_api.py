#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar API de sinais com sinais confirmados
"""

import requests
import json

def test_signals_api():
    """Testa a API de sinais principal"""
    print("🧪 Testando API de sinais principal...")
    
    token = '94fad7b1-094b-4fdb-8a76-e33de20dac01'
    
    try:
        response = requests.get(
            "http://localhost:5000/api/signals",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Total de sinais: {len(data)}")
            
            # Filtrar sinais BTC confirmados
            btc_signals = [s for s in data if s.get('signal_class') == 'BTC_CONFIRMED']
            print(f"Sinais BTC confirmados: {len(btc_signals)}")
            
            if btc_signals:
                print("\nPrimeiro sinal BTC confirmado:")
                print(json.dumps(btc_signals[0], indent=2))
            else:
                print("\nNenhum sinal BTC confirmado encontrado")
                
            # Mostrar alguns sinais do CSV
            csv_signals = [s for s in data if s.get('signal_class') != 'BTC_CONFIRMED']
            print(f"\nSinais do CSV: {len(csv_signals)}")
            if csv_signals:
                print("Primeiro sinal do CSV:")
                print(json.dumps(csv_signals[0], indent=2))
        else:
            print(f"Erro: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

def main():
    test_signals_api()

if __name__ == "__main__":
    main()