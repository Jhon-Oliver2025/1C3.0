#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para confirmar um sinal pendente
"""

import requests
import json

def confirm_first_signal():
    """Confirma o primeiro sinal pendente"""
    token = '94fad7b1-094b-4fdb-8a76-e33de20dac01'
    
    # Obter sinais pendentes
    response = requests.get(
        "http://localhost:5000/api/btc-signals/pending",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print(f"Status pending: {response.status_code}")
    print(f"Response: {response.text[:500]}")
    
    if response.status_code == 200:
        data = response.json()
        if 'data' in data and 'pending_signals' in data['data']:
            signals = data['data']['pending_signals']
            if signals:
                signal_id = signals[0]['id']
                symbol = signals[0]['symbol']
                print(f"\nConfirmando sinal: {symbol} (ID: {signal_id})")
                
                # Confirmar sinal
                confirm_response = requests.post(
                    f"http://localhost:5000/api/btc-signals/confirm/{signal_id}",
                    headers={"Authorization": f"Bearer {token}"}
                )
                
                print(f"Status confirm: {confirm_response.status_code}")
                print(f"Response: {confirm_response.text}")
            else:
                print("Nenhum sinal pendente encontrado")
        else:
            print("Estrutura de resposta inesperada")
    else:
        print(f"Erro ao obter sinais pendentes: {response.text}")

def main():
    confirm_first_signal()

if __name__ == "__main__":
    main()