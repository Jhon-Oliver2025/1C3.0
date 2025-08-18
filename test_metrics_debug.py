#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para debugar API metrics
"""

import requests
import json

def test_metrics_debug():
    """Debug da API metrics"""
    print("🔍 Debugando API metrics...")
    
    # Fazer login
    login_data = {
        "username": "jonatasprojetos2013@gmail.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(
            "http://localhost:5000/api/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            
            print(f"✅ Login bem-sucedido! Token: {token[:20]}...")
            
            # Testar API metrics
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            metrics_response = requests.get(
                "http://localhost:5000/api/btc-signals/metrics",
                headers=headers
            )
            
            print(f"\nStatus API metrics: {metrics_response.status_code}")
            print(f"Response: {metrics_response.text}")
            
        else:
            print(f"❌ Login falhou: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

def main():
    test_metrics_debug()

if __name__ == "__main__":
    main()