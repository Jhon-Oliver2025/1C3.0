#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para forçar o recarregamento dos dados no sistema de monitoramento
Resolve o problema onde os sinais estão salvos mas não aparecem nas APIs
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'back'))

from core.database import Database
from core.signal_monitoring_system import SignalMonitoringSystem
from core.binance_client import BinanceClient
from core.gerenciar_sinais import GerenciadorSinais
import pandas as pd
from datetime import datetime
import traceback

def force_reload_monitoring():
    """
    Força o recarregamento de todos os sinais no sistema de monitoramento
    """
    try:
        print("🔄 === FORÇANDO RECARREGAMENTO DO MONITORAMENTO ===")
        print(f"⏰ Início: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        
        # Inicializar componentes
        print("\n🔧 Inicializando componentes...")
        db = Database()
        binance_client = BinanceClient()
        monitoring_system = SignalMonitoringSystem.get_instance(db, binance_client)
        gerenciador = GerenciadorSinais(db)
        
        # Verificar sinais salvos
        print("\n📊 Verificando sinais salvos...")
        saved_signals = gerenciador.load_signals_from_csv()
        print(f"   ✅ {len(saved_signals)} sinais encontrados no CSV")
        
        if len(saved_signals) == 0:
            print("❌ Nenhum sinal encontrado para recarregar")
            return False
        
        # Parar monitoramento atual
        print("\n⏹️ Parando monitoramento atual...")
        if monitoring_system.is_monitoring:
            monitoring_system.stop_monitoring()
            print("   ✅ Monitoramento parado")
        
        # Limpar sinais monitorados
        print("\n🧹 Limpando sinais monitorados...")
        monitoring_system.monitored_signals.clear()
        print("   ✅ Cache limpo")
        
        # Recarregar sinais
        print("\n🔄 Recarregando sinais no monitoramento...")
        added_count = 0
        
        for signal in saved_signals:
            try:
                # Preparar dados do sinal para monitoramento
                signal_data = {
                    'id': signal.get('id', f"reload_{signal.get('symbol')}_{int(datetime.now().timestamp())}"),
                    'symbol': signal.get('symbol'),
                    'type': signal.get('type'),
                    'entry_price': float(signal.get('entry_price', 0)),
                    'target_price': float(signal.get('target_price', 0)),
                    'quality_score': float(signal.get('quality_score', 75)),
                    'signal_class': signal.get('signal_class', 'PREMIUM'),
                    'confirmation_reasons': ['reload_system'],
                    'btc_correlation': 0.0,
                    'btc_trend': 'NEUTRAL'
                }
                
                # Adicionar ao monitoramento
                success = monitoring_system.add_signal_to_monitoring(signal_data=signal_data)
                
                if success:
                    added_count += 1
                    print(f"   ✅ {signal['symbol']} - ${signal_data.get('simulation_investment', 1000)}")
                else:
                    print(f"   ❌ Falha: {signal['symbol']}")
                    
            except Exception as e:
                print(f"   ❌ Erro em {signal.get('symbol', 'UNKNOWN')}: {e}")
                continue
        
        # Reiniciar monitoramento
        print("\n🚀 Reiniciando monitoramento...")
        if not monitoring_system.is_monitoring:
            monitoring_system.start_monitoring()
            print("   ✅ Monitoramento reiniciado")
        
        # Verificar resultado
        print("\n🔍 Verificando resultado...")
        monitored_signals = monitoring_system.get_monitored_signals()
        print(f"   📊 Sinais monitorados: {len(monitored_signals)}")
        
        if len(monitored_signals) > 0:
            print("\n   📋 Exemplos de sinais monitorados:")
            for signal in monitored_signals[:3]:
                print(f"     • {signal.get('symbol')} - {signal.get('signal_type')} - ${signal.get('simulation_investment', 1000)}")
        
        print("\n🎉 === RECARREGAMENTO CONCLUÍDO ===")
        print(f"⏰ Fim: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"📊 Sinais recarregados: {added_count}")
        print(f"💰 Simulação total: ${added_count * 1000} USD")
        
        return added_count > 0
        
    except Exception as e:
        print(f"❌ Erro crítico: {e}")
        traceback.print_exc()
        return False

def main():
    """
    Função principal
    """
    try:
        success = force_reload_monitoring()
        
        if success:
            print("\n🎯 RECARREGAMENTO REALIZADO COM SUCESSO!")
            print("💰 Sistema de monitoramento reativado!")
            print("📊 APIs devem mostrar dados corretos agora!")
            sys.exit(0)
        else:
            print("\n❌ FALHA NO RECARREGAMENTO!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Processo cancelado pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()