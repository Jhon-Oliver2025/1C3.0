#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para analisar dados disponíveis na API BTC
"""

import requests
import json

def analyze_btc_data():
    """Analisa todos os dados disponíveis na API BTC"""
    token = '6b4cd525-58c3-46cf-a0d2-60c447d06a72'
    
    try:
        response = requests.get(
            "http://localhost:5000/api/btc-signals/metrics",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print("=== DADOS DISPONÍVEIS NA API BTC ===")
            
            print("\n1. BTC ANALYSIS:")
            btc_analysis = data['data']['btc_analysis']
            for key, value in btc_analysis.items():
                if key != 'timeframes':
                    print(f"  {key}: {value}")
            
            print("\n2. BTC PRICE DATA:")
            btc_price = data['data']['btc_price_data']
            for key, value in btc_price.items():
                print(f"  {key}: {value}")
            
            print("\n3. TIMEFRAMES (1h):")
            tf_1h = btc_analysis['timeframes']['1h']
            for key, value in tf_1h.items():
                print(f"  {key}: {value}")
            
            print("\n4. TIMEFRAMES (4h):")
            tf_4h = btc_analysis['timeframes']['4h']
            for key, value in tf_4h.items():
                print(f"  {key}: {value}")
                
            print("\n5. CONFIRMATION METRICS:")
            conf_metrics = data['data']['confirmation_metrics']
            for key, value in conf_metrics.items():
                print(f"  {key}: {value}")
                
            print("\n=== SUGESTÕES PARA O PAINEL ===")
            print("\n📊 INDICADORES TÉCNICOS DISPONÍVEIS:")
            print("  • RSI (1h e 4h): Força relativa")
            print("  • MACD: Convergência/Divergência")
            print("  • EMA 20/50: Médias móveis")
            print("  • ATR: Volatilidade")
            print("  • Pivot Points: Suporte/Resistência")
            
            print("\n💰 DADOS DE PREÇO:")
            print("  • Máxima/Mínima 24h")
            print("  • Timestamp da última atualização")
            
            print("\n📈 ANÁLISE MULTI-TIMEFRAME:")
            print("  • Comparação 1h vs 4h")
            print("  • Alinhamento de EMAs")
            print("  • Momentum por timeframe")
            
        else:
            print(f"Erro: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

def main():
    analyze_btc_data()

if __name__ == "__main__":
    main()