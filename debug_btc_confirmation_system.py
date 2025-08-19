#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para diagnosticar o sistema de confirmação BTC
Verifica por que os sinais não estão sendo confirmados automaticamente
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'back'))

from back.core.btc_signal_manager import BTCSignalManager
from back.core.signal_confirmation_system import SignalConfirmationSystem
from back.core.database import Database
from back.core.binance_client import BinanceClient
from back.core.btc_correlation_analyzer import BTCCorrelationAnalyzer
import time
from datetime import datetime

def debug_btc_confirmation_system():
    """
    Função principal para diagnosticar o sistema de confirmação BTC
    """
    print("\n" + "="*80)
    print("🔍 DIAGNÓSTICO DO SISTEMA DE CONFIRMAÇÃO BTC")
    print("="*80)
    
    try:
        # 1. Verificar instâncias dos sistemas
        print("\n📋 1. VERIFICANDO INSTÂNCIAS DOS SISTEMAS...")
        
        # Inicializar componentes
        db = Database()
        binance_client = BinanceClient()
        btc_analyzer = BTCCorrelationAnalyzer(binance_client)
        
        # Verificar BTCSignalManager (apenas precisa do db_instance)
        btc_manager = BTCSignalManager(db)
        print(f"✅ BTCSignalManager inicializado")
        print(f"   - Monitoramento ativo: {btc_manager.is_monitoring}")
        print(f"   - Sinais pendentes: {len(btc_manager.pending_signals)}")
        print(f"   - Sinais confirmados: {len(btc_manager.confirmed_signals)}")
        print(f"   - Sinais rejeitados: {len(btc_manager.rejected_signals)}")
        
        # Verificar SignalConfirmationSystem
        confirmation_system = SignalConfirmationSystem(binance_client, btc_analyzer)
        print(f"✅ SignalConfirmationSystem inicializado")
        
        # 2. Verificar configurações
        print("\n⚙️ 2. VERIFICANDO CONFIGURAÇÕES...")
        config = btc_manager.config
        print(f"   - Intervalo de verificação: {config.get('check_interval', 'N/A')}s")
        print(f"   - Máximo tentativas: {config.get('max_confirmation_attempts', 'N/A')}")
        print(f"   - Timeout expiração: {config.get('expiration_hours', 'N/A')}h")
        
        thresholds = confirmation_system.get_confirmation_thresholds()
        print(f"   - Score mínimo confirmação: {thresholds['confirmation_thresholds']['min_confirmation_score']}")
        print(f"   - Score máximo rejeição: {thresholds['confirmation_thresholds']['max_rejection_score']}")
        print(f"   - Breakout mínimo: {thresholds['confirmation_thresholds']['breakout_percentage']}%")
        
        # 3. Verificar sinais pendentes em detalhes
        print("\n📊 3. ANALISANDO SINAIS PENDENTES...")
        if btc_manager.pending_signals:
            for i, signal in enumerate(btc_manager.pending_signals[:5]):  # Mostrar apenas 5
                print(f"\n   📈 Sinal {i+1}:")
                print(f"      - Símbolo: {signal['symbol']}")
                print(f"      - Tipo: {signal['type']}")
                print(f"      - Preço entrada: {signal['entry_price']}")
                print(f"      - Score qualidade: {signal['quality_score']}")
                print(f"      - Criado em: {signal['created_at']}")
                print(f"      - Expira em: {signal['expires_at']}")
                print(f"      - Tentativas: {signal['confirmation_attempts']}")
                
                # Verificar se expirou
                now = datetime.now()
                if now > signal['expires_at']:
                    print(f"      ⚠️ EXPIRADO! ({now - signal['expires_at']} atrás)")
                else:
                    print(f"      ✅ Válido (expira em {signal['expires_at'] - now})")
        else:
            print("   📭 Nenhum sinal pendente encontrado")
        
        # 4. Testar confirmação de um sinal
        print("\n🧪 4. TESTANDO SISTEMA DE CONFIRMAÇÃO...")
        if btc_manager.pending_signals:
            test_signal = btc_manager.pending_signals[0]
            print(f"   🔬 Testando confirmação do sinal: {test_signal['symbol']}")
            
            # Simular verificação de confirmação
            try:
                result = btc_manager._check_signal_confirmation(test_signal)
                print(f"   📊 Resultado da verificação:")
                print(f"      - Ação: {result['action']}")
                print(f"      - Razões: {result['reasons']}")
            except Exception as e:
                print(f"   ❌ Erro na verificação: {e}")
        
        # 5. Verificar status do loop de monitoramento
        print("\n🔄 5. VERIFICANDO LOOP DE MONITORAMENTO...")
        print(f"   - Thread ativa: {btc_manager.monitoring_thread is not None}")
        if btc_manager.monitoring_thread:
            print(f"   - Thread viva: {btc_manager.monitoring_thread.is_alive()}")
        print(f"   - Flag monitoramento: {btc_manager.is_monitoring}")
        
        # 6. Verificar métricas
        print("\n📈 6. MÉTRICAS DO SISTEMA...")
        try:
            metrics = btc_manager.get_confirmation_metrics()
            print(f"   - Total processados: {metrics['total_signals_processed']}")
            print(f"   - Taxa confirmação: {metrics['confirmation_rate']}%")
            print(f"   - Tempo médio: {metrics['average_confirmation_time_minutes']}min")
            print(f"   - Status sistema: {metrics['system_status']}")
        except Exception as e:
            print(f"   ❌ Erro ao obter métricas: {e}")
        
        # 7. Diagnóstico final
        print("\n🎯 7. DIAGNÓSTICO FINAL...")
        
        issues = []
        
        if not btc_manager.is_monitoring:
            issues.append("❌ Sistema de monitoramento está DESABILITADO")
        
        if not btc_manager.monitoring_thread or not btc_manager.monitoring_thread.is_alive():
            issues.append("❌ Thread de monitoramento não está rodando")
        
        if len(btc_manager.pending_signals) == 0:
            issues.append("⚠️ Nenhum sinal pendente para processar")
        
        expired_signals = sum(1 for s in btc_manager.pending_signals 
                            if datetime.now() > s['expires_at'])
        if expired_signals > 0:
            issues.append(f"⚠️ {expired_signals} sinais expirados não removidos")
        
        if issues:
            print("\n🚨 PROBLEMAS IDENTIFICADOS:")
            for issue in issues:
                print(f"   {issue}")
        else:
            print("\n✅ Sistema aparenta estar funcionando corretamente")
        
        # 8. Sugestões de correção
        print("\n💡 SUGESTÕES DE CORREÇÃO:")
        if not btc_manager.is_monitoring:
            print("   1. Ativar monitoramento: btc_manager.start_monitoring()")
        
        if expired_signals > 0:
            print("   2. Limpar sinais expirados")
        
        if len(btc_manager.pending_signals) == 0:
            print("   3. Verificar se novos sinais estão sendo gerados")
        
        print("   4. Verificar logs do sistema para erros específicos")
        print("   5. Reiniciar o sistema de monitoramento se necessário")
        
    except Exception as e:
        print(f"❌ Erro durante diagnóstico: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80)
    print("🏁 DIAGNÓSTICO CONCLUÍDO")
    print("="*80)

if __name__ == "__main__":
    debug_btc_confirmation_system()