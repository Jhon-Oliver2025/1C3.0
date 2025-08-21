#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para forçar a adição de todos os sinais confirmados ao sistema de monitoramento
Resolve o problema onde os 65 sinais do dashboard não estão sendo monitorados
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

def force_add_all_signals_to_monitoring():
    """
    Força a adição de todos os sinais confirmados ao sistema de monitoramento
    """
    try:
        print("🚀 === FORÇANDO ADIÇÃO DE SINAIS AO MONITORAMENTO ===")
        print(f"⏰ Iniciado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        
        # Inicializar componentes
        print("\n🔧 Inicializando componentes...")
        db = Database()
        binance_client = BinanceClient()
        monitoring_system = SignalMonitoringSystem.get_instance(db, binance_client)
        gerenciador = GerenciadorSinais(db)
        
        # Verificar status atual do monitoramento
        print("\n📊 Status atual do monitoramento:")
        current_monitored = monitoring_system.get_monitored_signals()
        print(f"   Sinais sendo monitorados: {len(current_monitored)}")
        
        # Carregar sinais confirmados do CSV
        print("\n📂 Carregando sinais confirmados do dashboard...")
        signals_file = gerenciador.signals_file
        
        if not os.path.exists(signals_file):
            print(f"❌ Arquivo de sinais não encontrado: {signals_file}")
            return
        
        df = pd.read_csv(signals_file)
        confirmed_signals = df[df['status'] == 'CONFIRMED'].to_dict('records')
        
        print(f"✅ Encontrados {len(confirmed_signals)} sinais confirmados no dashboard")
        
        if len(confirmed_signals) == 0:
            print("⚠️ Nenhum sinal confirmado encontrado para adicionar")
            return
        
        # Adicionar cada sinal ao monitoramento
        print("\n🔄 Adicionando sinais ao monitoramento...")
        added_count = 0
        skipped_count = 0
        error_count = 0
        
        for i, signal in enumerate(confirmed_signals, 1):
            try:
                symbol = signal['symbol']
                signal_id = signal.get('confirmation_id', signal.get('id', f"manual_{symbol}_{i}"))
                
                print(f"\n📊 [{i}/{len(confirmed_signals)}] Processando {symbol}...")
                
                # Verificar se já está sendo monitorado
                if signal_id in [s.get('id') for s in current_monitored]:
                    print(f"   ⚠️ {symbol} já está sendo monitorado - pulando")
                    skipped_count += 1
                    continue
                
                # Preparar dados do sinal
                signal_data = {
                    'id': signal_id,
                    'confirmation_id': signal_id,
                    'symbol': symbol,
                    'type': signal['type'],
                    'entry_price': float(signal['entry_price']),
                    'target_price': float(signal.get('target_price', 0)),
                    'quality_score': float(signal.get('quality_score', 70)),
                    'signal_class': signal.get('signal_class', 'PREMIUM'),
                    'confirmation_reasons': signal.get('confirmation_reasons', 'manual_addition'),
                    'btc_correlation': float(signal.get('btc_correlation', 0)),
                    'btc_trend': signal.get('btc_trend', 'NEUTRAL'),
                    'confirmed_at': signal.get('confirmed_at', datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
                }
                
                # Adicionar ao monitoramento
                success = monitoring_system.add_signal_to_monitoring(signal_data=signal_data)
                
                if success:
                    print(f"   ✅ {symbol} adicionado com sucesso")
                    added_count += 1
                else:
                    print(f"   ❌ Falha ao adicionar {symbol}")
                    error_count += 1
                    
            except Exception as e:
                print(f"   ❌ Erro ao processar {signal.get('symbol', 'UNKNOWN')}: {e}")
                error_count += 1
                continue
        
        # Iniciar monitoramento se não estiver rodando
        print("\n🚀 Verificando sistema de monitoramento...")
        if not monitoring_system.is_monitoring:
            print("   🔄 Iniciando sistema de monitoramento...")
            monitoring_system.start_monitoring()
            print("   ✅ Sistema de monitoramento iniciado")
        else:
            print("   ✅ Sistema de monitoramento já está rodando")
        
        # Verificar status final
        print("\n📊 Status final do monitoramento:")
        final_monitored = monitoring_system.get_monitored_signals()
        print(f"   Sinais sendo monitorados: {len(final_monitored)}")
        
        # Resumo
        print("\n" + "="*60)
        print("📋 RESUMO DA OPERAÇÃO")
        print("="*60)
        print(f"✅ Sinais adicionados: {added_count}")
        print(f"⚠️ Sinais já monitorados: {skipped_count}")
        print(f"❌ Erros: {error_count}")
        print(f"📊 Total no dashboard: {len(confirmed_signals)}")
        print(f"🔍 Total sendo monitorado: {len(final_monitored)}")
        
        if added_count > 0:
            print("\n🎉 SUCESSO! Sinais adicionados ao monitoramento com simulação de $1.000 USD")
            print("💰 Agora você pode acompanhar o P&L em tempo real na página 'Investimentos Simulados'")
        else:
            print("\n⚠️ Nenhum sinal novo foi adicionado")
        
        print(f"\n⏰ Concluído em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        
    except Exception as e:
        print(f"❌ Erro crítico: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    force_add_all_signals_to_monitoring()