#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar a integração entre sinais confirmados e dashboard
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'back'))

from back.core.database import Database
from back.core.btc_signal_manager import BTCSignalManager
from back.core.technical_analysis import TechnicalAnalysis
from back.app_supabase import KryptonBotSupabase
import requests
import json

def test_dashboard_signals_integration():
    """
    Testa a integração entre sinais confirmados e dashboard
    """
    print("\n" + "="*80)
    print("🔍 TESTE DE INTEGRAÇÃO: SINAIS CONFIRMADOS → DASHBOARD")
    print("="*80)
    
    try:
        # 1. Testar inicialização do bot
        print("\n📋 1. TESTANDO INICIALIZAÇÃO DO BOT...")
        bot = KryptonBotSupabase()
        print(f"✅ Bot inicializado: {type(bot)}")
        print(f"   - Tem btc_signal_manager: {hasattr(bot, 'btc_signal_manager')}")
        
        if hasattr(bot, 'btc_signal_manager'):
            btc_manager = bot.btc_signal_manager
            print(f"   - BTCSignalManager: {btc_manager}")
            print(f"   - Tipo: {type(btc_manager)}")
            
            # 2. Testar sinais confirmados
            print("\n📊 2. TESTANDO SINAIS CONFIRMADOS...")
            confirmed_signals = btc_manager.get_confirmed_signals(limit=10)
            print(f"   - Sinais confirmados encontrados: {len(confirmed_signals)}")
            
            if confirmed_signals:
                print("   - Exemplo de sinal confirmado:")
                for key, value in confirmed_signals[0].items():
                    print(f"     {key}: {value}")
            else:
                print("   - Nenhum sinal confirmado encontrado")
                
                # Criar um sinal de teste
                print("\n🧪 3. CRIANDO SINAL DE TESTE...")
                test_signal = {
                    'id': 'test-signal-123',
                    'symbol': 'BTCUSDT',
                    'type': 'COMPRA',
                    'entry_price': 43250.0,
                    'target_price': 45000.0,
                    'projection_percentage': 4.05,
                    'quality_score': 85.5,
                    'signal_class': 'PREMIUM+',
                    'created_at': '19/08/2025 08:30:00',
                    'expires_at': '19/08/2025 12:30:00',
                    'confirmation_attempts': 1,
                    'btc_correlation': 0.75,
                    'btc_trend': 'BULLISH',
                    'original_data': {
                        'symbol': 'BTCUSDT',
                        'type': 'COMPRA',
                        'entry_price': 43250.0,
                        'target_price': 45000.0,
                        'projection_percentage': 4.05,
                        'quality_score': 85.5,
                        'signal_class': 'PREMIUM+'
                    }
                }
                
                # Adicionar sinal pendente
                btc_manager.pending_signals.append(test_signal)
                print(f"   ✅ Sinal de teste adicionado aos pendentes")
                
                # Confirmar sinal manualmente
                btc_manager._confirm_signal(test_signal, ['TEST_CONFIRMATION'])
                print(f"   ✅ Sinal de teste confirmado")
                
                # Verificar se apareceu nos confirmados
                confirmed_signals = btc_manager.get_confirmed_signals(limit=10)
                print(f"   - Sinais confirmados após teste: {len(confirmed_signals)}")
        
        # 4. Testar API de sinais
        print("\n🌐 4. TESTANDO API DE SINAIS...")
        try:
            # Simular chamada da API
            from back.api_routes.signals import get_btc_confirmed_signals
            
            # Configurar contexto da aplicação
            from back.app_supabase import create_app
            app = create_app()
            
            with app.app_context():
                # Anexar bot_instance ao app
                app.bot_instance = bot
                
                # Testar função
                btc_signals = get_btc_confirmed_signals()
                print(f"   - Sinais retornados pela API: {len(btc_signals)}")
                
                if btc_signals:
                    print("   - Exemplo de sinal da API:")
                    for key, value in btc_signals[0].items():
                        print(f"     {key}: {value}")
                        
        except Exception as api_error:
            print(f"   ❌ Erro na API: {api_error}")
            import traceback
            traceback.print_exc()
        
        # 5. Verificar estrutura do bot
        print("\n🔍 5. ESTRUTURA DO BOT...")
        print(f"   - Atributos do bot: {[attr for attr in dir(bot) if not attr.startswith('_')]}")
        
        if hasattr(bot, 'technical_analysis'):
            ta = bot.technical_analysis
            print(f"   - TechnicalAnalysis: {ta}")
            if hasattr(ta, 'btc_signal_manager'):
                print(f"   - BTCSignalManager via TA: {ta.btc_signal_manager}")
        
        # 6. Diagnóstico final
        print("\n🎯 6. DIAGNÓSTICO FINAL...")
        
        issues = []
        
        if not hasattr(bot, 'btc_signal_manager'):
            issues.append("❌ Bot não tem atributo btc_signal_manager")
        elif not bot.btc_signal_manager:
            issues.append("❌ btc_signal_manager é None")
        
        if not confirmed_signals:
            issues.append("⚠️ Nenhum sinal confirmado encontrado")
        
        if issues:
            print("\n🚨 PROBLEMAS IDENTIFICADOS:")
            for issue in issues:
                print(f"   {issue}")
        else:
            print("\n✅ Sistema aparenta estar funcionando corretamente")
        
        # 7. Sugestões de correção
        print("\n💡 SUGESTÕES DE CORREÇÃO:")
        print("   1. Verificar se o BTCSignalManager está sendo inicializado corretamente")
        print("   2. Verificar se o bot_instance está sendo anexado ao app corretamente")
        print("   3. Verificar se a função get_btc_confirmed_signals está acessando o local correto")
        print("   4. Testar confirmação manual de sinais")
        print("   5. Verificar logs do sistema para erros específicos")
        
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80)
    print("🏁 TESTE CONCLUÍDO")
    print("="*80)

if __name__ == "__main__":
    test_dashboard_signals_integration()