#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para analisar regras de confirmação de sinais BTC
"""

import requests
import json
from datetime import datetime

def debug_confirmation_rules():
    """Analisa as regras de confirmação e por que sinais não estão sendo confirmados"""
    print("🔍 ANALISANDO REGRAS DE CONFIRMAÇÃO BTC")
    print("="*60)
    
    # Token válido (obtido dos logs recentes)
    token = 'cdbefac2-ce4a-4eb2-b011-c7a5cd0258ae'
    
    try:
        # 1. Obter sinais pendentes
        print("\n1. SINAIS PENDENTES:")
        response = requests.get(
            "http://localhost:5000/api/btc-signals/pending",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            pending_signals = data['data']['pending_signals']
            print(f"   📊 Total: {len(pending_signals)} sinais pendentes")
            
            if pending_signals:
                # Analisar primeiro sinal como exemplo
                signal = pending_signals[0]
                print(f"\n   📋 EXEMPLO - {signal['symbol']} ({signal['type']}):")
                print(f"      💰 Preço entrada: ${signal['entry_price']}")
                print(f"      🎯 Preço alvo: ${signal['target_price']}")
                print(f"      📅 Criado: {signal['created_at']}")
                print(f"      ⏰ Expira: {signal['expires_at']}")
                print(f"      🔄 Tentativas: {signal['confirmation_attempts']}")
                print(f"      ₿ Correlação BTC: {signal['btc_correlation']:.3f}")
                print(f"      📈 Tendência BTC: {signal['btc_trend']}")
                print(f"      ⭐ Qualidade: {signal['quality_score']:.1f} ({signal['signal_class']})")
        else:
            print(f"   ❌ Erro ao obter sinais pendentes: {response.status_code}")
            print(f"   📝 Resposta: {response.text}")
        
        # 2. Obter métricas BTC
        print("\n2. ANÁLISE BTC ATUAL:")
        response = requests.get(
            "http://localhost:5000/api/btc-signals/metrics",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            btc_analysis = data['data']['btc_analysis']
            btc_price = data['data']['btc_price_data']
            
            print(f"   💰 Preço BTC: ${btc_price['price']:,.2f}")
            print(f"   📊 Variação 24h: {btc_price['change_24h']:+.2f}%")
            print(f"   📈 Tendência: {btc_analysis['trend']}")
            print(f"   💪 Força: {btc_analysis['strength']:.1f}%")
            print(f"   📊 Volatilidade: {btc_analysis['volatility']:.2f}%")
            
            # Analisar timeframes
            print(f"\n   🕐 TIMEFRAME 1H:")
            tf_1h = btc_analysis['timeframes']['1h']
            print(f"      RSI: {tf_1h['rsi']:.1f} ({tf_1h['rsi_condition']})")
            print(f"      MACD: Bullish={tf_1h['macd_bullish']}, Bearish={tf_1h['macd_bearish']}")
            print(f"      EMA Alignment: {tf_1h['ema_alignment']}")
            print(f"      Tendência: {tf_1h['trend']} (Força: {tf_1h['strength']:.1f}%)")
            
            print(f"\n   🕐 TIMEFRAME 4H:")
            tf_4h = btc_analysis['timeframes']['4h']
            print(f"      RSI: {tf_4h['rsi']:.1f} ({tf_4h['rsi_condition']})")
            print(f"      MACD: Bullish={tf_4h['macd_bullish']}, Bearish={tf_4h['macd_bearish']}")
            print(f"      EMA Alignment: {tf_4h['ema_alignment']}")
            print(f"      Tendência: {tf_4h['trend']} (Força: {tf_4h['strength']:.1f}%)")
        
        # 3. Analisar regras de confirmação
        print("\n3. REGRAS DE CONFIRMAÇÃO:")
        print("   📋 Para um sinal ser CONFIRMADO, precisa de 3+ critérios:")
        print("      1️⃣ BREAKOUT_CONFIRMED - Rompimento de 0.5%+ na direção do sinal")
        print("      2️⃣ VOLUME_CONFIRMED - Aumento de 20%+ no volume")
        print("      3️⃣ BTC_ALIGNED - BTC alinhado com a direção do sinal")
        print("      4️⃣ MOMENTUM_SUSTAINED - 2+ velas confirmando direção")
        
        print("\n   📋 Para um sinal ser REJEITADO, precisa de 2+ critérios:")
        print("      1️⃣ REVERSAL_DETECTED - Movimento contrário de 1%+")
        print("      2️⃣ VOLUME_INSUFFICIENT - Volume muito baixo (<80% da média)")
        print("      3️⃣ BTC_OPPOSITE - BTC forte na direção oposta")
        print("      4️⃣ TIMEOUT_EXPIRED - Mais de 12 tentativas ou 4h expirado")
        
        # 4. Verificar métricas de confirmação
        print("\n4. MÉTRICAS DO SISTEMA:")
        if response.status_code == 200:
            metrics = data['data']['confirmation_metrics']
            print(f"   📊 Total processados: {metrics['total_signals_processed']}")
            print(f"   ✅ Confirmados: {metrics['confirmed_signals']}")
            print(f"   ❌ Rejeitados: {metrics['rejected_signals']}")
            print(f"   ⏳ Pendentes: {metrics['pending_signals']}")
            print(f"   📈 Taxa confirmação: {metrics['confirmation_rate']:.1f}%")
            print(f"   ⏱️ Tempo médio: {metrics['average_confirmation_time_minutes']:.1f} min")
            print(f"   🔄 Status sistema: {metrics['system_status']}")
        
        # 5. Diagnóstico
        print("\n5. DIAGNÓSTICO:")
        if pending_signals and len(pending_signals) > 0:
            print("   🔍 POSSÍVEIS CAUSAS DOS SINAIS NÃO CONFIRMADOS:")
            
            # Verificar se BTC está neutro
            if btc_analysis['trend'] == 'NEUTRAL':
                print("   ⚠️ BTC em tendência NEUTRAL - dificulta alinhamento")
            
            # Verificar força do BTC
            if btc_analysis['strength'] < 50:
                print(f"   ⚠️ BTC com força baixa ({btc_analysis['strength']:.1f}%) - dificulta confirmações")
            
            # Verificar volatilidade
            if btc_analysis['volatility'] < 1.0:
                print(f"   ⚠️ Volatilidade baixa ({btc_analysis['volatility']:.2f}%) - poucos rompimentos")
            
            # Verificar idade dos sinais
            now = datetime.now()
            for signal in pending_signals[:3]:  # Verificar primeiros 3
                created = datetime.strptime(signal['created_at'], '%d/%m/%Y %H:%M:%S')
                age_minutes = (now - created).total_seconds() / 60
                if age_minutes > 60:  # Mais de 1 hora
                    print(f"   ⚠️ Sinal {signal['symbol']} muito antigo ({age_minutes:.0f} min)")
        
        print("\n" + "="*60)
        print("✅ Análise concluída!")
        
    except Exception as e:
        print(f"❌ Erro na análise: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_confirmation_rules()