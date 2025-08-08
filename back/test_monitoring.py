#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste para verificar o funcionamento do monitoramento
"""

import os
import sys
import time
from datetime import datetime

# Adicionar o diretório back ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from core.database import Database
from core.technical_analysis import TechnicalAnalysis
from core.binance_client import BinanceClient

def test_binance_connection():
    """Testa a conexão com a Binance"""
    print("\n" + "="*50)
    print("🔍 TESTANDO CONEXÃO COM BINANCE")
    print("="*50)
    
    try:
        binance = BinanceClient()
        
        # Verificar se a API está habilitada
        if not hasattr(binance, 'use_binance_api') or not binance.use_binance_api:
            print("❌ API da Binance está DESABILITADA")
            print(f"🔍 USE_BINANCE_API: {os.getenv('USE_BINANCE_API', 'NOT_SET')}")
            print(f"🔍 BINANCE_API_KEY: {'SET' if os.getenv('BINANCE_API_KEY') else 'NOT_SET'}")
            print(f"🔍 BINANCE_SECRET_KEY: {'SET' if os.getenv('BINANCE_SECRET_KEY') else 'NOT_SET'}")
            return False
        
        print("✅ API da Binance está HABILITADA")
        
        # Testar exchange info
        print("🔄 Testando get_exchange_info...")
        exchange_info = binance.get_exchange_info()
        if exchange_info:
            print(f"✅ Exchange info obtida: {len(exchange_info.get('symbols', []))} símbolos")
        else:
            print("❌ Falha ao obter exchange info")
            return False
        
        # Testar leverage brackets
        print("🔄 Testando get_leverage_brackets...")
        leverage_info = binance.get_leverage_brackets()
        if leverage_info:
            print(f"✅ Leverage brackets obtidos: {len(leverage_info)} símbolos")
        else:
            print("❌ Falha ao obter leverage brackets")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar Binance: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_monitoring():
    """Testa o sistema de monitoramento"""
    print("\n" + "="*50)
    print("🔍 TESTANDO SISTEMA DE MONITORAMENTO")
    print("="*50)
    
    try:
        # Inicializar componentes
        db = Database()
        analyzer = TechnicalAnalysis(db)
        
        print(f"✅ TechnicalAnalysis inicializado")
        print(f"🔍 Configuração: {analyzer.config}")
        print(f"🔍 Estado inicial: monitoring={analyzer.is_monitoring}, pairs={len(analyzer.top_pairs)}")
        
        # Testar inicialização de pares
        print("\n🔄 Testando inicialização de pares...")
        if analyzer._initialize_pairs():
            print(f"✅ Pares inicializados: {len(analyzer.top_pairs)} pares")
            print(f"🔍 Primeiros 5 pares: {analyzer.top_pairs[:5]}")
        else:
            print("❌ Falha na inicialização de pares")
            return False
        
        # Testar varredura do mercado
        print("\n🔄 Testando varredura do mercado...")
        signals = analyzer.scan_market(verbose=True)
        print(f"✅ Varredura concluída: {len(signals)} sinais encontrados")
        
        if signals:
            print("\n📊 SINAIS ENCONTRADOS:")
            for signal in signals[:3]:  # Mostrar apenas os primeiros 3
                print(f"  • {signal['symbol']} - {signal['type']} - Score: {signal.get('quality_score', 0):.1f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar monitoramento: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_csv_signals():
    """Testa a leitura de sinais do CSV"""
    print("\n" + "="*50)
    print("🔍 TESTANDO LEITURA DE SINAIS CSV")
    print("="*50)
    
    try:
        from api_routes.signals import get_signals_from_csv
        
        signals = get_signals_from_csv()
        print(f"✅ Sinais lidos do CSV: {len(signals)}")
        
        if signals:
            print("\n📊 PRIMEIROS 3 SINAIS:")
            for signal in signals[:3]:
                print(f"  • {signal['symbol']} - {signal['type']} - Class: {signal['signal_class']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar CSV: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Função principal de teste"""
    print("🚀 INICIANDO TESTES DE DIAGNÓSTICO")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Mostrar variáveis de ambiente importantes
    print("\n🔍 VARIÁVEIS DE AMBIENTE:")
    env_vars = ['USE_BINANCE_API', 'BINANCE_API_KEY', 'BINANCE_SECRET_KEY', 'FLASK_ENV', 'DATABASE_URL']
    for var in env_vars:
        value = os.getenv(var, 'NOT_SET')
        if 'KEY' in var or 'URL' in var:
            display_value = 'SET' if value != 'NOT_SET' else 'NOT_SET'
        else:
            display_value = value
        print(f"  • {var}: {display_value}")
    
    # Executar testes
    tests = [
        ("Conexão Binance", test_binance_connection),
        ("Sistema de Monitoramento", test_monitoring),
        ("Leitura CSV", test_csv_signals)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ Erro crítico no teste '{test_name}': {e}")
            results[test_name] = False
    
    # Resumo final
    print("\n" + "="*50)
    print("📋 RESUMO DOS TESTES")
    print("="*50)
    
    for test_name, result in results.items():
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"  • {test_name}: {status}")
    
    all_passed = all(results.values())
    print(f"\n🎯 RESULTADO GERAL: {'✅ TODOS OS TESTES PASSARAM' if all_passed else '❌ ALGUNS TESTES FALHARAM'}")
    
    return all_passed

if __name__ == '__main__':
    main()