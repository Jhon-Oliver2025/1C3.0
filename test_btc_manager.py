#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'back'))

from back.core.database import Database
from back.core.btc_signal_manager import BTCSignalManager

def test_btc_manager():
    print("🔍 Testando BTCSignalManager...")
    
    try:
        # Inicializar
        db = Database()
        btc_manager = BTCSignalManager(db)
        
        # Verificar sinais confirmados
        signals = btc_manager.get_confirmed_signals(limit=3)
        print(f"📊 Sinais do BTCSignalManager: {len(signals)}")
        
        if signals:
            print("\n📋 Exemplo de sinal:")
            signal = signals[0]
            for key, value in signal.items():
                print(f"   {key}: {value}")
        else:
            print("⚠️ Nenhum sinal confirmado no BTCSignalManager")
            
        # Verificar estado do sistema
        print(f"\n🔧 Estado do sistema:")
        print(f"   Monitoramento ativo: {btc_manager.is_monitoring}")
        print(f"   Sinais pendentes: {len(btc_manager.pending_signals)}")
        print(f"   Sinais confirmados: {len(btc_manager.confirmed_signals)}")
        print(f"   Sinais rejeitados: {len(btc_manager.rejected_signals)}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_btc_manager()