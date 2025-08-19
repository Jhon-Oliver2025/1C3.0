#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar diretamente o BTCSignalManager e verificar sinais confirmados
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'back'))

from back.core.database import Database
from back.core.btc_signal_manager import BTCSignalManager
from back.app_supabase import KryptonBotSupabase
import json

def test_btc_signals_direct():
    """
    Testa diretamente o BTCSignalManager para verificar sinais confirmados
    """
    print("\n" + "="*80)
    print("🔍 TESTE DIRETO DO BTCSignalManager")
    print("="*80)
    
    try:
        # 1. Inicializar bot
        print("\n📋 1. INICIALIZANDO BOT...")
        bot = KryptonBotSupabase()
        print(f"✅ Bot inicializado: {type(bot)}")
        
        # 2. Verificar BTCSignalManager
        print("\n📊 2. VERIFICANDO BTCSignalManager...")
        if hasattr(bot, 'btc_signal_manager'):
            btc_manager = bot.btc_signal_manager
            print(f"✅ BTCSignalManager encontrado: {btc_manager}")
            
            # 3. Verificar sinais confirmados
            print("\n🎯 3. VERIFICANDO SINAIS CONFIRMADOS...")
            confirmed_signals = btc_manager.get_confirmed_signals(limit=10)
            print(f"   Sinais confirmados encontrados: {len(confirmed_signals)}")
            
            if confirmed_signals:
                print("\n   📊 Sinais confirmados:")
                for i, signal in enumerate(confirmed_signals):
                    print(f"\n   🔸 Sinal {i+1}:")
                    for key, value in signal.items():
                        print(f"     {key}: {value}")
            else:
                print("   ⚠️ Nenhum sinal confirmado encontrado")
            
            # 4. Verificar sinais pendentes
            print("\n⏳ 4. VERIFICANDO SINAIS PENDENTES...")
            pending_signals = btc_manager.pending_signals
            print(f"   Sinais pendentes: {len(pending_signals)}")
            
            if pending_signals:
                print("\n   📊 Sinais pendentes:")
                for i, signal in enumerate(pending_signals[:3]):  # Mostrar apenas 3
                    print(f"\n   🔸 Sinal {i+1}:")
                    for key, value in signal.items():
                        print(f"     {key}: {value}")
            
            # 5. Verificar status do monitoramento
            print("\n🔄 5. VERIFICANDO STATUS DO MONITORAMENTO...")
            print(f"   Monitoramento ativo: {btc_manager.is_monitoring}")
            print(f"   Thread de monitoramento: {btc_manager.monitoring_thread}")
            if btc_manager.monitoring_thread:
                print(f"   Thread está viva: {btc_manager.monitoring_thread.is_alive()}")
            
            # 6. Verificar métricas
            print("\n📈 6. VERIFICANDO MÉTRICAS...")
            try:
                metrics = btc_manager.get_confirmation_metrics()
                print(f"   Métricas: {json.dumps(metrics, indent=2)}")
            except Exception as e:
                print(f"   ❌ Erro ao obter métricas: {e}")
            
            # 7. Testar conversão para formato do dashboard
            print("\n🔄 7. TESTANDO CONVERSÃO PARA DASHBOARD...")
            if confirmed_signals:
                print("   Convertendo sinais para formato do dashboard...")
                
                dashboard_signals = []
                for signal in confirmed_signals:
                    # Converter tipo de COMPRA/VENDA para LONG/SHORT
                    signal_type = "LONG" if signal.get('type') == 'COMPRA' else "SHORT"
                    
                    # Converter sinal para formato dos cards
                    dashboard_signal = {
                        "symbol": signal.get('symbol', ''),
                        "type": signal_type,
                        "entry_price": float(signal.get('entry_price', 0)),
                        "entry_time": signal.get('confirmed_at', signal.get('created_at', '')),
                        "target_price": float(signal.get('target_price', 0)),
                        "projection_percentage": round(float(signal.get('projection_percentage', 0)), 2),
                        "status": "CONFIRMADO",
                        "quality_score": round(float(signal.get('quality_score', 0)), 1),
                        "signal_class": "BTC_CONFIRMED"
                    }
                    
                    dashboard_signals.append(dashboard_signal)
                
                print(f"   ✅ {len(dashboard_signals)} sinais convertidos para o dashboard")
                
                if dashboard_signals:
                    print("\n   📊 Exemplo de sinal convertido:")
                    for key, value in dashboard_signals[0].items():
                        print(f"     {key}: {value}")
            
        else:
            print("❌ BTCSignalManager não encontrado no bot")
        
        # 8. Diagnóstico final
        print("\n🎯 8. DIAGNÓSTICO FINAL...")
        
        issues = []
        
        if not hasattr(bot, 'btc_signal_manager'):
            issues.append("❌ Bot não tem BTCSignalManager")
        elif not bot.btc_signal_manager:
            issues.append("❌ BTCSignalManager é None")
        elif len(confirmed_signals) == 0:
            issues.append("⚠️ Nenhum sinal confirmado encontrado")
        elif not btc_manager.is_monitoring:
            issues.append("⚠️ Monitoramento não está ativo")
        
        if issues:
            print("\n🚨 PROBLEMAS IDENTIFICADOS:")
            for issue in issues:
                print(f"   {issue}")
        else:
            print("\n✅ Sistema está funcionando corretamente")
        
        # Sugestões
        print("\n💡 PRÓXIMOS PASSOS:")
        if len(confirmed_signals) == 0:
            print("   1. Confirmar um sinal manualmente para teste")
            print("   2. Verificar se o sistema de confirmação está funcionando")
        if not btc_manager.is_monitoring:
            print("   3. Ativar o monitoramento via interface")
        print("   4. Verificar logs do backend para erros")
        print("   5. Testar a API /api/signals/ diretamente")
        
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80)
    print("🏁 TESTE CONCLUÍDO")
    print("="*80)

if __name__ == "__main__":
    test_btc_signals_direct()