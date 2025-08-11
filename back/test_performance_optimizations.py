#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste das Otimizações de Performance
Script para validar processamento paralelo e cache de klines
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database import Database
from core.technical_analysis import TechnicalAnalysis
from core.klines_cache import CacheManager
import time

def test_parallel_processing():
    """Testa o processamento paralelo vs sequencial"""
    print("🚀 === TESTE DE PROCESSAMENTO PARALELO ===")
    print()
    
    try:
        # Inicializar sistema
        print("📊 Inicializando sistema...")
        db = Database()
        tech_analysis = TechnicalAnalysis(db)
        
        # Simular lista menor para teste rápido
        original_pairs = tech_analysis.top_pairs.copy() if tech_analysis.top_pairs else []
        test_pairs = [
            'BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'BNBUSDT', 'XRPUSDT',
            'SOLUSDT', 'DOGEUSDT', 'MATICUSDT', 'AVAXUSDT', 'DOTUSDT',
            'LINKUSDT', 'LTCUSDT', 'BCHUSDT', 'XLMUSDT', 'VETUSDT'
        ]
        
        # Forçar lista de teste
        tech_analysis.top_pairs = test_pairs
        
        print(f"🔍 Testando com {len(test_pairs)} pares...")
        
        # Teste com processamento paralelo
        print("\n⚡ Executando varredura PARALELA...")
        start_time = time.time()
        
        signals_parallel = tech_analysis.scan_market(verbose=True)
        
        parallel_time = time.time() - start_time
        
        print(f"\n📊 Resultados do Processamento Paralelo:")
        print(f"   ⏱️ Tempo: {parallel_time:.2f}s")
        print(f"   📈 Sinais: {len(signals_parallel)}")
        print(f"   🚀 Velocidade: {len(test_pairs)/parallel_time:.1f} pares/s")
        
        # Restaurar lista original
        tech_analysis.top_pairs = original_pairs
        
        return {
            'parallel_time': parallel_time,
            'signals_count': len(signals_parallel),
            'pairs_per_second': len(test_pairs)/parallel_time
        }
        
    except Exception as e:
        print(f"❌ Erro no teste paralelo: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_cache_performance():
    """Testa a eficiência do sistema de cache"""
    print("\n🗄️ === TESTE DE CACHE DE KLINES ===")
    print()
    
    try:
        # Inicializar sistema
        db = Database()
        tech_analysis = TechnicalAnalysis(db)
        
        test_symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'BNBUSDT', 'XRPUSDT']
        test_intervals = ['1h', '4h']
        
        print(f"🔍 Testando cache com {len(test_symbols)} símbolos e {len(test_intervals)} intervalos...")
        
        # Primeira execução (cache miss)
        print("\n📥 Primeira execução (cache miss):")
        start_time = time.time()
        
        for symbol in test_symbols:
            for interval in test_intervals:
                data = tech_analysis.get_klines(symbol, interval, 100)
                if data is not None:
                    print(f"✅ {symbol} {interval}: {len(data)} períodos")
                else:
                    print(f"❌ {symbol} {interval}: Falha")
        
        first_run_time = time.time() - start_time
        
        # Segunda execução (cache hit)
        print("\n📤 Segunda execução (cache hit):")
        start_time = time.time()
        
        for symbol in test_symbols:
            for interval in test_intervals:
                data = tech_analysis.get_klines(symbol, interval, 100)
                if data is not None:
                    print(f"⚡ {symbol} {interval}: {len(data)} períodos (cached)")
        
        second_run_time = time.time() - start_time
        
        # Estatísticas de cache
        cache_stats = tech_analysis.cache_manager.get_performance_stats()
        
        print(f"\n📊 Resultados do Cache:")
        print(f"   ⏱️ Primeira execução: {first_run_time:.3f}s")
        print(f"   ⚡ Segunda execução: {second_run_time:.3f}s")
        print(f"   🚀 Speedup: {first_run_time/second_run_time:.1f}x")
        print(f"   📈 Hit Rate: {cache_stats['cache_hit_rate']:.1f}%")
        print(f"   💾 API Calls Saved: {cache_stats['api_calls_saved']}")
        
        return {
            'first_run_time': first_run_time,
            'second_run_time': second_run_time,
            'speedup': first_run_time/second_run_time,
            'cache_hit_rate': cache_stats['cache_hit_rate'],
            'api_calls_saved': cache_stats['api_calls_saved']
        }
        
    except Exception as e:
        print(f"❌ Erro no teste de cache: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_memory_usage():
    """Testa uso de memória do sistema"""
    print("\n💾 === TESTE DE USO DE MEMÓRIA ===")
    print()
    
    try:
        import psutil
        import gc
        
        # Memória inicial
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        print(f"📊 Memória inicial: {initial_memory:.1f} MB")
        
        # Inicializar sistema
        db = Database()
        tech_analysis = TechnicalAnalysis(db)
        
        after_init_memory = process.memory_info().rss / 1024 / 1024
        print(f"📊 Memória após inicialização: {after_init_memory:.1f} MB (+{after_init_memory-initial_memory:.1f} MB)")
        
        # Executar varredura
        test_pairs = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'BNBUSDT', 'XRPUSDT']
        tech_analysis.top_pairs = test_pairs
        
        signals = tech_analysis.scan_market(verbose=False)
        
        after_scan_memory = process.memory_info().rss / 1024 / 1024
        print(f"📊 Memória após varredura: {after_scan_memory:.1f} MB (+{after_scan_memory-after_init_memory:.1f} MB)")
        
        # Estatísticas de cache
        cache_stats = tech_analysis.cache_manager.get_performance_stats()
        
        print(f"\n📈 Estatísticas de Cache:")
        for interval, stats in cache_stats['individual_caches'].items():
            print(f"   {interval}: {stats['total_entries']} entradas, {stats['cache_efficiency']:.1f}% eficiência")
        
        # Limpeza
        gc.collect()
        final_memory = process.memory_info().rss / 1024 / 1024
        print(f"📊 Memória final: {final_memory:.1f} MB")
        
        return {
            'initial_memory': initial_memory,
            'peak_memory': after_scan_memory,
            'memory_increase': after_scan_memory - initial_memory,
            'cache_entries': sum(stats['total_entries'] for stats in cache_stats['individual_caches'].values())
        }
        
    except ImportError:
        print("⚠️ psutil não disponível, pulando teste de memória")
        return None
    except Exception as e:
        print(f"❌ Erro no teste de memória: {e}")
        return None

def test_thread_safety():
    """Testa thread safety do sistema"""
    print("\n🔒 === TESTE DE THREAD SAFETY ===")
    print()
    
    try:
        import threading
        import concurrent.futures
        
        # Inicializar sistema
        db = Database()
        tech_analysis = TechnicalAnalysis(db)
        
        test_symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT']
        results = []
        errors = []
        
        def analyze_symbol_thread(symbol):
            """Função para executar em thread separada"""
            try:
                for _ in range(3):  # 3 análises por thread
                    signal = tech_analysis.analyze_symbol(symbol)
                    results.append(f"{symbol}: {'✅' if signal else '❌'}")
                    time.sleep(0.1)
                return True
            except Exception as e:
                errors.append(f"{symbol}: {e}")
                return False
        
        print(f"🔍 Executando análises concorrentes com {len(test_symbols)} símbolos...")
        
        # Executar em threads paralelas
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(analyze_symbol_thread, symbol) for symbol in test_symbols]
            
            for future in concurrent.futures.as_completed(futures):
                future.result()
        
        print(f"\n📊 Resultados Thread Safety:")
        print(f"   ✅ Análises completadas: {len(results)}")
        print(f"   ❌ Erros: {len(errors)}")
        
        if errors:
            print("\n❌ Erros encontrados:")
            for error in errors[:5]:  # Mostrar apenas os primeiros 5
                print(f"   {error}")
        
        return {
            'completed_analyses': len(results),
            'errors': len(errors),
            'success_rate': len(results) / (len(results) + len(errors)) * 100 if (len(results) + len(errors)) > 0 else 0
        }
        
    except Exception as e:
        print(f"❌ Erro no teste de thread safety: {e}")
        return None

def run_comprehensive_performance_test():
    """Executa todos os testes de performance"""
    print("🧪 === TESTE ABRANGENTE DE PERFORMANCE ===")
    print("=" * 60)
    
    results = {}
    
    # Teste 1: Processamento Paralelo
    parallel_results = test_parallel_processing()
    if parallel_results:
        results['parallel'] = parallel_results
    
    # Teste 2: Cache Performance
    cache_results = test_cache_performance()
    if cache_results:
        results['cache'] = cache_results
    
    # Teste 3: Uso de Memória
    memory_results = test_memory_usage()
    if memory_results:
        results['memory'] = memory_results
    
    # Teste 4: Thread Safety
    thread_results = test_thread_safety()
    if thread_results:
        results['thread_safety'] = thread_results
    
    # Resumo final
    print("\n🎉 === RESUMO DOS TESTES ===")
    print("=" * 60)
    
    if 'parallel' in results:
        print(f"⚡ Processamento Paralelo: {results['parallel']['pairs_per_second']:.1f} pares/s")
    
    if 'cache' in results:
        print(f"🗄️ Cache Speedup: {results['cache']['speedup']:.1f}x")
        print(f"📈 Cache Hit Rate: {results['cache']['cache_hit_rate']:.1f}%")
    
    if 'memory' in results:
        print(f"💾 Uso de Memória: +{results['memory']['memory_increase']:.1f} MB")
    
    if 'thread_safety' in results:
        print(f"🔒 Thread Safety: {results['thread_safety']['success_rate']:.1f}% sucesso")
    
    print("\n✅ Todos os testes concluídos!")
    print("=" * 60)
    
    return results

if __name__ == "__main__":
    print("🚀 Iniciando testes de otimizações de performance...")
    print("=" * 60)
    
    # Executar todos os testes
    results = run_comprehensive_performance_test()
    
    print("\n🎯 Testes de performance finalizados!")
    print("=" * 60)