#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnóstico para verificar a saúde do backend Flask
"""

import requests
import json
import sys
import time
from urllib.parse import urljoin

def test_endpoint(base_url, endpoint, method='GET', data=None):
    """
    Testa um endpoint específico
    """
    url = urljoin(base_url, endpoint)
    print(f"\n🔍 Testando {method} {url}")
    
    try:
        if method == 'GET':
            response = requests.get(url, timeout=30)
        elif method == 'POST':
            response = requests.post(url, json=data, timeout=30)
        
        print(f"✅ Status: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")
        
        try:
            content = response.json()
            print(f"📄 Conteúdo: {json.dumps(content, indent=2)}")
        except:
            print(f"📄 Conteúdo (texto): {response.text[:200]}...")
            
        return response.status_code == 200
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro: {e}")
        return False

def main():
    """
    Função principal de diagnóstico
    """
    print("🏥 DIAGNÓSTICO DO BACKEND FLASK")
    print("=" * 50)
    
    # URLs para testar
    urls = [
        "https://1crypten.space",
        "http://localhost:5000"
    ]
    
    # Endpoints para testar
    endpoints = [
        "/api/health",
        "/api/status",
        "/"
    ]
    
    for base_url in urls:
        print(f"\n🌐 Testando servidor: {base_url}")
        print("-" * 40)
        
        for endpoint in endpoints:
            test_endpoint(base_url, endpoint)
            time.sleep(1)  # Pequena pausa entre requests
    
    # Teste de login
    print("\n🔐 Testando endpoint de login")
    print("-" * 40)
    
    login_data = {
        "username": "test@example.com",
        "password": "testpassword"
    }
    
    for base_url in urls:
        test_endpoint(base_url, "/api/auth/login", method='POST', data=login_data)
        time.sleep(1)

if __name__ == "__main__":
    main()