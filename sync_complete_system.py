#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Sincronização Completa do Sistema
Força a sincronização entre dados locais, sistema de monitoramento e APIs
"""

import sys
import os
import requests
import time
sys.path.append(os.path.join(os.path.dirname(__file__), 'back'))

from core.database import Database
from core.signal_monitoring_system import SignalMonitoringSystem
from core.binance_client import BinanceClient
from core.gerenciar_sinais import GerenciadorSinais
import pandas as pd
from datetime import datetime
import traceback
import json

def sync_complete_system():
    """
    Sincroniza completamente o sistema: dados locais → monitoramento → APIs
    """
    try:
        print("🔄 === SINCRONIZAÇÃO COMPLETA DO SISTEMA ===")
        print(f"⏰ Início: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        
        # Fase 1: Verificar dados locais
        print("\n📊 FASE 1: VERIFICANDO DADOS LOCAIS")
        db = Database()
        gerenciador = GerenciadorSinais(db)
        
        saved_signals = gerenciador.load_signals_from_csv()
        print(f"   ✅ {len(saved_signals)} sinais encontrados no CSV")
        
        if len(saved_signals) == 0:
            print("❌ Nenhum sinal encontrado para sincronizar")
            return False
        
        # Fase 2: Reinicializar sistema de monitoramento
        print("\n🔧 FASE 2: REINICIALIZANDO SISTEMA DE MONITORAMENTO")
        binance_client = BinanceClient()
        
        # Obter nova instância do sistema de monitoramento
        monitoring_system = SignalMonitoringSystem.get_instance(db, binance_client)
        
        # Parar e limpar sistema atual
        if monitoring_system.is_monitoring:
            monitoring_system.stop_monitoring()
            print("   ✅ Monitoramento parado")
        
        # Limpar completamente
        monitoring_system.monitored_signals.clear()
        print("   ✅ Cache limpo")
        
        # Fase 3: Recarregar todos os sinais
        print("\n🔄 FASE 3: RECARREGANDO SINAIS")
        added_count = 0
        
        for i, signal in enumerate(saved_signals, 1):
            try:
                print(f"   [{i}/{len(saved_signals)}] Processando {signal.get('symbol')}...")
                
                # Preparar dados completos do sinal
                signal_data = {
                    'id': signal.get('id', f"sync_{signal.get('symbol')}_{int(datetime.now().timestamp())}"),
                    'symbol': signal.get('symbol'),
                    'type': signal.get('type'),
                    'entry_price': float(signal.get('entry_price', 0)),
                    'target_price': float(signal.get('target_price', 0)),
                    'quality_score': float(signal.get('quality_score', 75)),
                    'signal_class': signal.get('signal_class', 'PREMIUM'),
                    'confirmation_reasons': ['system_sync'],
                    'btc_correlation': 0.0,
                    'btc_trend': 'NEUTRAL',
                    'confirmed_at': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                }
                
                # Adicionar ao monitoramento
                success = monitoring_system.add_signal_to_monitoring(signal_data=signal_data)
                
                if success:
                    added_count += 1
                    print(f"     ✅ {signal['symbol']} adicionado")
                else:
                    print(f"     ❌ Falha: {signal['symbol']}")
                    
            except Exception as e:
                print(f"     ❌ Erro em {signal.get('symbol', 'UNKNOWN')}: {e}")
                continue
        
        # Fase 4: Reiniciar monitoramento
        print("\n🚀 FASE 4: REINICIANDO MONITORAMENTO")
        if not monitoring_system.is_monitoring:
            monitoring_system.start_monitoring()
            print("   ✅ Monitoramento reiniciado")
        
        # Aguardar estabilização
        print("   ⏳ Aguardando estabilização (5 segundos)...")
        time.sleep(5)
        
        # Fase 5: Verificar APIs
        print("\n🔍 FASE 5: VERIFICANDO APIS")
        
        # Testar API de monitoramento
        try:
            response = requests.get('http://localhost:5000/api/signal-monitoring/signals/active', timeout=10)
            if response.status_code == 200:
                data = response.json()
                api_signals = data.get('data', {}).get('signals', [])
                print(f"   ✅ API de monitoramento: {len(api_signals)} sinais")
            else:
                print(f"   ❌ API de monitoramento: Status {response.status_code}")
        except Exception as e:
            print(f"   ❌ Erro na API de monitoramento: {e}")
        
        # Testar API de simulação
        try:
            response = requests.get('http://localhost:5000/api/signal-monitoring/signals/simulation', timeout=10)
            if response.status_code == 200:
                data = response.json()
                sim_data = data.get('data', {})
                total_signals = sim_data.get('total_signals', 0)
                total_investment = sim_data.get('total_investment', 0)
                print(f"   ✅ API de simulação: {total_signals} sinais, ${total_investment} investimento")
            else:
                print(f"   ❌ API de simulação: Status {response.status_code}")
        except Exception as e:
            print(f"   ❌ Erro na API de simulação: {e}")
        
        # Fase 6: Verificar sistema local
        print("\n📊 FASE 6: VERIFICAÇÃO FINAL")
        monitored_signals = monitoring_system.get_monitored_signals()
        print(f"   📊 Sistema local: {len(monitored_signals)} sinais monitorados")
        
        if len(monitored_signals) > 0:
            print("\n   📋 Sinais ativos no sistema:")
            for signal in monitored_signals[:5]:
                symbol = signal.get('symbol', 'UNKNOWN')
                signal_type = signal.get('signal_type', 'UNKNOWN')
                investment = signal.get('simulation_investment', 1000)
                print(f"     • {symbol} - {signal_type} - ${investment}")
        
        # Resultado final
        print("\n🎉 === SINCRONIZAÇÃO CONCLUÍDA ===")
        print(f"⏰ Fim: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"📊 Sinais sincronizados: {added_count}")
        print(f"💰 Investimento total: ${added_count * 1000} USD")
        print(f"🔄 Sistema local: {len(monitored_signals)} sinais ativos")
        
        if added_count > 0:
            print("\n✅ SISTEMA SINCRONIZADO COM SUCESSO!")
            print("📱 Atualize a página para ver os dados")
            print("🔄 As APIs devem mostrar os sinais agora")
            return True
        else:
            print("\n⚠️ Nenhum sinal foi sincronizado")
            return False
        
    except Exception as e:
        print(f"❌ Erro crítico na sincronização: {e}")
        traceback.print_exc()
        return False

def test_apis_after_sync():
    """
    Testa as APIs após a sincronização
    """
    print("\n🧪 === TESTANDO APIS APÓS SINCRONIZAÇÃO ===")
    
    # Aguardar um pouco mais
    print("   ⏳ Aguardando estabilização adicional (3 segundos)...")
    time.sleep(3)
    
    # Testar múltiplas vezes
    for attempt in range(3):
        print(f"\n   🔄 Tentativa {attempt + 1}/3:")
        
        try:
            # API de monitoramento
            response = requests.get('http://localhost:5000/api/signal-monitoring/signals/active', timeout=5)
            if response.status_code == 200:
                data = response.json()
                signals_count = len(data.get('data', {}).get('signals', []))
                print(f"     ✅ Monitoramento: {signals_count} sinais")
                
                if signals_count > 0:
                    print("     🎉 SUCESSO! APIs estão retornando dados")
                    return True
            else:
                print(f"     ❌ Monitoramento: Status {response.status_code}")
                
        except Exception as e:
            print(f"     ❌ Erro: {e}")
        
        if attempt < 2:
            time.sleep(2)
    
    print("   ⚠️ APIs ainda não estão retornando dados")
    return False

def main():
    """
    Função principal
    """
    try:
        # Executar sincronização
        sync_success = sync_complete_system()
        
        if sync_success:
            # Testar APIs
            api_success = test_apis_after_sync()
            
            if api_success:
                print("\n🏆 SINCRONIZAÇÃO COMPLETA E APIS FUNCIONANDO!")
                print("💰 Sistema de simulação de $1.000 USD ativo!")
                print("📱 Atualize a página para ver os investimentos simulados!")
                sys.exit(0)
            else:
                print("\n⚠️ Sistema sincronizado, mas APIs podem precisar de mais tempo")
                print("🔄 Tente atualizar a página em alguns minutos")
                sys.exit(0)
        else:
            print("\n❌ FALHA NA SINCRONIZAÇÃO!")
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