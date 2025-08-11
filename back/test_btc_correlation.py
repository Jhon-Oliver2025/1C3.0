#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste do Sistema de Correlação BTC
Script para validar o funcionamento do BTCCorrelationAnalyzer
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database import Database
from core.binance_client import BinanceClient
from core.btc_correlation_analyzer import BTCCorrelationAnalyzer
from core.technical_analysis import TechnicalAnalysis
import time

def test_btc_correlation_analyzer():
    """Testa o analisador de correlação BTC"""
    print("🧪 === TESTE DO SISTEMA DE CORRELAÇÃO BTC ===")
    print()
    
    try:
        # Inicializar componentes
        print("📊 Inicializando componentes...")
        db = Database()
        binance = BinanceClient()
        btc_analyzer = BTCCorrelationAnalyzer(binance)
        
        # Teste 1: Análise BTC
        print("\n🔍 Teste 1: Análise BTC")
        print("-" * 40)
        
        btc_4h = btc_analyzer.get_btc_analysis('4h')
        btc_1h = btc_analyzer.get_btc_analysis('1h')
        btc_consolidated = btc_analyzer.get_current_btc_analysis()
        
        if btc_4h:
            print(f"✅ BTC 4H: {btc_4h['trend']} | Força: {btc_4h['strength']:.1f}")
        else:
            print("❌ Falha na análise BTC 4H")
            
        if btc_1h:
            print(f"✅ BTC 1H: {btc_1h['trend']} | Força: {btc_1h['strength']:.1f}")
        else:
            print("❌ Falha na análise BTC 1H")
            
        if btc_consolidated:
            print(f"✅ BTC Consolidado: {btc_consolidated['trend']} | Força: {btc_consolidated['strength']:.1f}")
            print(f"   Momentum Alinhado: {btc_consolidated['momentum_aligned']}")
            print(f"   Volatilidade: {btc_consolidated['volatility']:.2f}%")
        else:
            print("❌ Falha na análise BTC consolidada")
        
        # Teste 2: Correlações
        print("\n🔗 Teste 2: Cálculo de Correlações")
        print("-" * 40)
        
        test_symbols = ['ETHUSDT', 'ADAUSDT', 'DOGEUSDT', 'SOLUSDT', 'MATICUSDT']
        
        for symbol in test_symbols:
            try:
                correlation = btc_analyzer.calculate_symbol_btc_correlation(symbol)
                correlation_strength = btc_analyzer.classify_correlation_strength(correlation)
                
                print(f"📈 {symbol}: {correlation:.3f} ({correlation_strength})")
                
            except Exception as e:
                print(f"❌ Erro em {symbol}: {e}")
        
        # Teste 3: Pontuação BTC
        print("\n⭐ Teste 3: Sistema de Pontuação BTC")
        print("-" * 40)
        
        for symbol in test_symbols[:3]:  # Testar apenas 3 para economizar tempo
            try:
                # Testar ambos os tipos de sinal
                for signal_type in ['COMPRA', 'VENDA']:
                    score = btc_analyzer.calculate_btc_correlation_score(symbol, signal_type)
                    should_filter = btc_analyzer.should_filter_signal_by_btc(symbol, signal_type)
                    
                    status = "🚫 FILTRADO" if should_filter else "✅ APROVADO"
                    print(f"📊 {symbol} {signal_type}: {score:.1f}pts | {status}")
                    
            except Exception as e:
                print(f"❌ Erro na pontuação {symbol}: {e}")
        
        # Teste 4: Integração com TechnicalAnalysis
        print("\n🔧 Teste 4: Integração com Sistema Principal")
        print("-" * 40)
        
        try:
            tech_analysis = TechnicalAnalysis(db)
            
            # Testar análise de um símbolo
            test_symbol = 'ETHUSDT'
            print(f"🔍 Testando análise completa: {test_symbol}")
            
            signal = tech_analysis.analyze_symbol(test_symbol)
            
            if signal:
                print(f"✅ Sinal gerado para {test_symbol}:")
                print(f"   Tipo: {signal['type']}")
                print(f"   Qualidade: {signal['quality_score']:.1f} ({signal['signal_class']})")
                print(f"   BTC Correlação: {signal.get('btc_correlation', 'N/A')}")
                print(f"   BTC Tendência: {signal.get('btc_trend', 'N/A')}")
                print(f"   Score BTC: {signal.get('btc_correlation_score', 0):.1f}pts")
            else:
                print(f"ℹ️ Nenhum sinal qualificado para {test_symbol}")
                
        except Exception as e:
            print(f"❌ Erro na integração: {e}")
        
        print("\n🎉 === TESTE CONCLUÍDO ===")
        
    except Exception as e:
        print(f"❌ Erro geral no teste: {e}")
        import traceback
        traceback.print_exc()

def test_correlation_performance():
    """Testa performance do sistema de correlação"""
    print("\n⚡ === TESTE DE PERFORMANCE ===")
    print()
    
    try:
        # Inicializar
        db = Database()
        binance = BinanceClient()
        btc_analyzer = BTCCorrelationAnalyzer(binance)
        
        # Símbolos para teste
        test_symbols = [
            'ETHUSDT', 'ADAUSDT', 'BNBUSDT', 'XRPUSDT', 'SOLUSDT',
            'DOGEUSDT', 'MATICUSDT', 'AVAXUSDT', 'DOTUSDT', 'LINKUSDT'
        ]
        
        print(f"🔍 Testando performance com {len(test_symbols)} símbolos...")
        
        start_time = time.time()
        
        results = []
        for symbol in test_symbols:
            try:
                symbol_start = time.time()
                
                # Calcular correlação
                correlation = btc_analyzer.calculate_symbol_btc_correlation(symbol)
                
                # Calcular scores
                buy_score = btc_analyzer.calculate_btc_correlation_score(symbol, 'COMPRA')
                sell_score = btc_analyzer.calculate_btc_correlation_score(symbol, 'VENDA')
                
                symbol_time = time.time() - symbol_start
                
                results.append({
                    'symbol': symbol,
                    'correlation': correlation,
                    'buy_score': buy_score,
                    'sell_score': sell_score,
                    'time': symbol_time
                })
                
                print(f"✅ {symbol}: {correlation:.3f} | {symbol_time:.2f}s")
                
            except Exception as e:
                print(f"❌ {symbol}: {e}")
        
        total_time = time.time() - start_time
        avg_time = total_time / len(test_symbols) if test_symbols else 0
        
        print(f"\n📊 Resultados de Performance:")
        print(f"   Total: {total_time:.2f}s")
        print(f"   Média por símbolo: {avg_time:.2f}s")
        print(f"   Símbolos processados: {len(results)}/{len(test_symbols)}")
        
        # Teste de cache
        print(f"\n🗄️ Testando cache...")
        cache_start = time.time()
        
        # Segunda execução (deve usar cache)
        for symbol in test_symbols[:3]:
            correlation = btc_analyzer.calculate_symbol_btc_correlation(symbol)
        
        cache_time = time.time() - cache_start
        print(f"✅ Cache test: {cache_time:.2f}s (deve ser mais rápido)")
        
    except Exception as e:
        print(f"❌ Erro no teste de performance: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Iniciando testes do sistema de correlação BTC...")
    print("=" * 60)
    
    # Executar testes
    test_btc_correlation_analyzer()
    test_correlation_performance()
    
    print("\n✅ Todos os testes concluídos!")
    print("=" * 60)