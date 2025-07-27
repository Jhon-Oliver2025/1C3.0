# Imports necessários
from binance.client import Client
from binance.exceptions import BinanceAPIException
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Any, TypedDict, cast
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange
from config import server
import requests
import time
import traceback
import os
import csv
from .database import Database
from colorama import Fore, Style, init
from .binance_client import BinanceClient
from .gerenciar_sinais import GerenciadorSinais

# Initialize colorama
init()

class TechnicalAnalysisConfig(TypedDict):
    trend_timeframe: str
    entry_timeframe: str
    quality_score_minimum: float
    update_interval: int

class TechnicalAnalysis:
    def __init__(self, db_instance: Database):
        print("📊 Inicializando TechnicalAnalysis...")
        self.db = db_instance
        self.binance = BinanceClient()
        self.gerenciador = GerenciadorSinais(db_instance)
        
        # Configurações de análise
        self.trend_timeframe: str = '4h'
        self.entry_timeframe: str = '1h'
        self.quality_score_minimum: float = 80.0
        self.update_interval: int = 1200  # 20 minutos
        
        # Controle de pares e varreduras
        self.pairs_last_update: float = 0
        self.top_pairs: List[str] = []
        self.complete_scan_interval: int = 1200  # 20 minutos
        self.quick_scan_interval: int = 60
        self.last_complete_scan: float = 0
        self.target_percentage: float = 6.0
        
        # Inicialização forçada dos pares
        print("🔄 Carregando pares iniciais...")
        if not self.update_futures_pairs():
            print("⚠️ Falha ao carregar pares iniciais, tentando método alternativo...")
            self.select_top_pairs()
        print(f"✅ {len(self.top_pairs)} pares carregados para análise")

    def calculate_target_price(self, entry_price: float, signal_type: str, trend_data: Optional[Dict] = None, market_conditions: Optional[Dict] = None, quality_score: float = 0) -> float:
        """Calcula o preço alvo com garantia mínima de 6% de ganho"""
        # ALVO MÍNIMO GARANTIDO: 6%
        min_percentage = 6.0
        
        # Calcular percentual dinâmico baseado na qualidade
        if quality_score >= 80:  # Sinais PREMIUM e ELITE
            # Adicionar até 14% extra baseado em análise técnica
            extra_percentage = 0.0
            
            if trend_data and market_conditions:
                # Volatilidade: até +8%
                volatility = market_conditions.get('volatility', 2.0)
                volatility_bonus = min(volatility * 2.0, 8.0)
                
                # Força da tendência: até +3%
                trend_strength = abs(trend_data.get('trend_strength', 0.01))
                trend_bonus = min(trend_strength * 300, 3.0)
                
                # Qualidade do sinal: até +3%
                if quality_score >= 90:  # ELITE
                    quality_bonus = 3.0
                elif quality_score >= 85:  # PREMIUM Alto
                    quality_bonus = 2.0
                else:  # PREMIUM Baixo
                    quality_bonus = 1.0
                
                extra_percentage = volatility_bonus + trend_bonus + quality_bonus
            
            # Limitar o extra entre 0% e 14%
            extra_percentage = min(max(extra_percentage, 0.0), 14.0)
            final_percentage = min_percentage + extra_percentage
        else:
            # Para sinais com qualidade < 80, usar apenas o mínimo
            final_percentage = min_percentage
        
        # Calcular preço alvo
        if signal_type == 'COMPRA':
            target_price = entry_price * (1 + final_percentage / 100)
        else:  # VENDA
            target_price = entry_price * (1 - final_percentage / 100)
        
        return target_price

    def calculate_support_resistance_levels(self, df: pd.DataFrame, current_price: float) -> Dict[str, float]:
        """Calcula níveis de suporte e resistência baseados em máximas e mínimas"""
        try:
            # Últimas 50 velas para análise
            recent_df = df.tail(50)
            
            # Encontrar máximas e mínimas locais
            highs = recent_df['high'].values
            lows = recent_df['low'].values
            
            # Resistência: média das 3 maiores máximas recentes
            top_highs = sorted(highs, reverse=True)[:3]
            resistance = sum(top_highs) / len(top_highs)
            
            # Suporte: média das 3 menores mínimas recentes
            bottom_lows = sorted(lows)[:3]
            support = sum(bottom_lows) / len(bottom_lows)
            
            return {
                'resistance': resistance,
                'support': support,
                'resistance_distance': ((resistance - current_price) / current_price) * 100,
                'support_distance': ((current_price - support) / current_price) * 100
            }
            
        except Exception as e:
            print(f"❌ Erro ao calcular suporte/resistência: {e}")
            return {
                'resistance': current_price * 1.1, 
                'support': current_price * 0.9, 
                'resistance_distance': 10.0, 
                'support_distance': 10.0
            }

    def select_top_pairs(self) -> bool:
        """Seleciona os melhores pares para análise"""
        try:
            print("\n🔄 Selecionando melhores pares...")
            pairs_data = []
            
            # Get all USDT perpetual futures using our custom client
            exchange_info = self.binance.get_exchange_info()
            if not exchange_info:
                return False
                
            valid_pairs = [s['symbol'] for s in exchange_info['symbols'] 
                         if s['symbol'].endswith('USDT') and 
                         s['status'] == 'TRADING' and 
                         s['contractType'] == 'PERPETUAL']
            
            total_pairs = len(valid_pairs)
            remaining_pairs = total_pairs
            
            for i, symbol in enumerate(valid_pairs):
                try:
                    print(f"\r🔄 Analisando {symbol}... ({remaining_pairs}/{total_pairs})", end="")
                    remaining_pairs -= 1
                    # Na função select_top_pairs, linha ~160:
                    # ANTES:
                    df = self.get_klines(symbol, self.entry_timeframe, limit=100)
                    
                    # DEPOIS:
                    df = self.get_klines(symbol, '4h', limit=100)  # ← MUDANÇA: usar 4h em vez de entry_timeframe
                    if df is None or len(df) < 20:
                        continue
                        
                    # Calculate metrics
                    avg_volume = df['volume'].mean() * df['close'].mean()
                    atr = AverageTrueRange(
                        high=pd.Series(df['high'].values, dtype=float),
                        low=pd.Series(df['low'].values, dtype=float),
                        close=pd.Series(df['close'].values, dtype=float),
                        window=14
                    ).average_true_range()
                    
                    volatility = (atr.iloc[-1] / df['close'].iloc[-1]) * 100
                    volume_score = min(avg_volume / 1000000, 10)
                    volatility_score = min(volatility, 10)
                    final_score = (volume_score * 0.5 + volatility_score * 0.5) * 10
                    
                    pairs_data.append({
                        'symbol': symbol,
                        'volume': avg_volume,
                        'volatility': volatility,
                        'score': final_score
                    })
                    
                except Exception as e:
                    continue
            
            # Sort and select top pairs
            pairs_df = pd.DataFrame(pairs_data)
            if len(pairs_df) > 0:
                pairs_df = pairs_df.sort_values('score', ascending=False).head(100)
                self.top_pairs = list(pairs_df['symbol'].values)
                
                # Converte o DataFrame para lista de tuplas (symbol, data)
                pairs_list = [(row['symbol'], {
                    'volume': row['volume'],
                    'priceChangePercent': 0.0
                }) for _, row in pairs_df.iterrows()]
                
                # Exibe os top 100 pares
                print(f"\n✅ Top {len(self.top_pairs)} pares USDT perpétuos selecionados:")
                for i, (symbol, data) in enumerate(pairs_list, 1):
                    remaining = 100 - i + 1
                    print(f"({remaining:03d}) {symbol:<12} - Volume: ${data['volume']:,.0f}")
                
                return True
            
            return False
            
        except Exception as e:
            print(f"\n❌ Erro ao selecionar pares: {e}")
            return False

    def get_klines(self, symbol: str, interval: str, limit: int = 100) -> Optional[pd.DataFrame]:
        """Obtém dados de klines da Binance"""
        try:
            klines = self.binance.make_request(
                '/fapi/v1/klines',
                params={
                    'symbol': symbol,
                    'interval': interval,
                    'limit': limit
                }
            )
            
            if not klines:
                return None
                
            # Create DataFrame
            df = pd.DataFrame(data=klines)
            
            # Assign columns
            df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume',
                         'close_time', 'quote_volume', 'trades', 'taker_buy_volume',
                         'taker_buy_quote_volume', 'ignore']
            
            # Convert numeric columns
            df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
            
            return df
            
        except Exception as e:
            print(f"❌ Erro ao obter klines para {symbol}: {e}")
            return None

    def analyze_market(self) -> List[Dict[str, Any]]:
        """Analisa todos os pares selecionados"""
        signals = []
        for symbol in self.top_pairs:
            signal = self.analyze_symbol(symbol)
            if signal:
                signals.append(signal)
        return signals

    def scan_market(self, verbose: bool = False) -> List[Dict[str, Any]]:
        """Executa varredura do mercado"""
        try:
            current_time = time.time()
            current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            if verbose:
                print("\n" + "="*50)
                print(f"🔍 Iniciando varredura do mercado em {current_datetime}")
                print(f"📊 Pares monitorados: {len(self.top_pairs)}")
                print("="*50)
            
            # Verifica se é hora de fazer varredura completa
            time_since_last_update = current_time - self.pairs_last_update
            if time_since_last_update >= self.complete_scan_interval:
                print("\n🔄 Iniciando varredura completa...")
                self.update_futures_pairs()
                self.pairs_last_update = current_time
                print("✅ Varredura completa finalizada")
            else:
                print("\n🔍 Analisando top 100 pares...")
                time_to_next_complete = self.complete_scan_interval - time_since_last_update
                hours = int(time_to_next_complete // 3600)
                minutes = int((time_to_next_complete % 3600) // 60)
                print(f"⏳ Próxima varredura completa em: {hours}h {minutes}m")
            
            # Analisa o mercado
            signals = []
            sinais_encontrados = 0
            
            for symbol in self.top_pairs:
                try:
                    print(f"\r📊 Analisando {symbol}...", end="")
                    signal = self.analyze_symbol(symbol)
                    if signal:
                        print(f"\n✅ Sinal encontrado para {symbol}:")
                        print(f"   Tipo: {signal['type']}")
                        print(f"   Preço Entrada: {signal['entry_price']:.8f}")
                        print(f"   Preço Alvo: {signal['target_price']:.8f}")
                        print(f"   RSI: {signal.get('rsi', 0):.2f}")
                        print(f"   Pontuação: {signal['quality_score']:.2f} ({signal['signal_class']})")
                        print(f"   - Tendência 4H: {signal['trend_score']:.2f}/35")
                        print(f"   - Confirmação 1H: {signal['entry_score']:.2f}/25")
                        print(f"   - RSI: {signal['rsi_score']:.2f}/20")
                        print(f"   - Padrões Técnicos: {signal['pattern_score']:.2f}/20")
                        
                        # Usar apenas o gerenciador para salvar o sinal
                        if self.gerenciador.save_signal(signal):
                            signals.append(signal)
                            sinais_encontrados += 1
                            print(f"✅ Sinal salvo com sucesso: {symbol}")
                        else:
                            print(f"❌ Falha ao salvar sinal: {signal['symbol']}")
                            
                except Exception as e:
                    print(f"\n❌ Erro ao analisar {symbol}: {e}")
                    continue
            
            # Exibir resumo final
            print("\n" + "="*50)
            print(f"✅ Varredura concluída em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"📈 Total de sinais encontrados: {sinais_encontrados}")
            print("="*50)
            print("\n⏳ Aguardando próxima varredura...")
            
            # Temporizador regressivo de 60 segundos
            for i in range(60, 0, -1):
                print(f"\r⏱️  Próxima varredura em {i} segundos...", end="")
                time.sleep(1)
            print("\n")
            
            return signals
            
        except Exception as e:
            print(f"❌ Erro na varredura do mercado: {e}")
            traceback.print_exc()
            return []

    def update_futures_pairs(self):
        """Atualiza a lista de pares futuros"""
        try:
            print("\n🔄 Atualizando lista de pares futuros...")
            
            # Get exchange information using our custom client
            exchange_info = self.binance.get_exchange_info()
            if not exchange_info:
                return False
            
            # Filter USDT perpetual futures and check leverage
            valid_pairs = []
            total_symbols = len([s for s in exchange_info['symbols'] 
                           if s['symbol'].endswith('USDT') and 
                           s['status'] == 'TRADING' and 
                           s['contractType'] == 'PERPETUAL'])
            remaining = total_symbols
            
            for symbol in exchange_info['symbols']:
                if (symbol['symbol'].endswith('USDT') and 
                    symbol['status'] == 'TRADING' and 
                    symbol['contractType'] == 'PERPETUAL'):
                    
                    try:
                        print(f"\r🔄 Verificando {symbol['symbol']} ({remaining}/{total_symbols})", end="")
                        leverage_info = self.binance.get_leverage_brackets()
                        if not leverage_info or symbol['symbol'] not in leverage_info:
                            remaining -= 1
                            continue
                            
                        max_leverage = float(leverage_info[symbol['symbol']][0]['initialLeverage'])
                        if max_leverage >= 50:
                            valid_pairs.append(symbol['symbol'])
                            print(f"\n✅ {symbol['symbol']} verificado (alavancagem: {max_leverage}x)")
                        remaining -= 1
                    except Exception as e:
                        print(f"\n❌ Erro ao verificar {symbol['symbol']}: {e}")
                        remaining -= 1
                        continue
            
            # Get 24h ticker for valid pairs
            ticker_data = self.binance.get_24h_ticker_data(valid_pairs)
            if not ticker_data:
                return False
                
            # Sort by volume and get top 100
            sorted_pairs = sorted(
                [(symbol, data) for symbol, data in ticker_data.items()],
                key=lambda x: x[1]['volume'],
                reverse=True
            )[:100]
            
            self.top_pairs = [pair[0] for pair in sorted_pairs]
            
            print(f"\n✅ Top {len(self.top_pairs)} pares USDT perpétuos com alavancagem 50x selecionados:")
            for i, (symbol, data) in enumerate(sorted_pairs, 1):
                print(f"{i}. {symbol:<12} - Volume: ${data['volume']:,.0f} - Variação 24h: {data['priceChangePercent']:+.2f}%")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao atualizar pares futuros: {e}")
            traceback.print_exc()
            return False

    def analyze_symbol(self, symbol: str) -> Optional[Dict[str, Any]]:
        try:
            # Get trend timeframe data (4H)
            trend_df = self.get_klines(symbol, self.trend_timeframe)
            if trend_df is None or len(trend_df) < 50:
                return None
                
            # Analisar tendência do timeframe maior primeiro
            trend = self.analyze_trend_df(trend_df)
            if trend is None:
                return None
                
            # Get entry timeframe data (1H)
            entry_df = self.get_klines(symbol, self.entry_timeframe)
            if entry_df is None or len(entry_df) < 50:
                return None

            # Determinar o tipo de sinal baseado na tendência
            signal_type = 'COMPRA' if trend['is_uptrend'] else 'VENDA'
            
            # Definir preço de entrada como o último preço de fechamento
            entry_price = float(entry_df['close'].iloc[-1])
            
            # Calcular condições de mercado
            market_conditions = self.calculate_market_conditions(entry_df)
            
            # Calcular níveis de suporte e resistência
            support_resistance = self.calculate_support_resistance_levels(entry_df, entry_price)
            
            # 1. Análise de Tendência em 4H (35 pontos)
            trend_score = 0
            trend_strength = abs(trend.get('trend_strength', 0))
            trend_score += min(trend_strength * 50, 15)
            
            # Alinhamento de EMAs (10 pontos)
            if trend['is_uptrend'] and trend['close'] >= trend['ema20'] * 0.98:
                trend_score += 10
            elif trend['is_downtrend'] and trend['close'] <= trend['ema20'] * 1.02:
                trend_score += 10
            
            # Volume e momentum (10 pontos)
            if trend.get('volume_trend', 0) > 0:
                trend_score += 5
            if abs(trend.get('macd_signal', 0)) > 0.001:
                trend_score += 5
            
            # 2. Análise de Entrada em 1H (25 pontos) - NOVA LÓGICA
            entry_analysis = self.analyze_entry_df(entry_df)
            entry_score = 0
            
            # NOVA LÓGICA: Detectar retomada da tendência
            if signal_type == 'COMPRA':
                # Tendência principal é ALTA no 4H
                if entry_analysis.get('is_uptrend', False):
                    # 1H já está alinhado com 4H
                    entry_score += 25  # Pontuação máxima
                elif (
                    entry_analysis.get('rsi', 50) < 55 and  # RSI não está sobrecomprado
                    entry_analysis.get('momentum_positive', False) and  # Momentum voltando positivo
                    entry_analysis.get('price_change', 0) > 0.005  # Movimento de pelo menos 0.5% para cima
                ):
                    # 1H está retomando a direção do 4H
                    entry_score += 20  # Boa pontuação para retomada
                elif (
                    entry_analysis.get('rsi', 50) < 45 and  # RSI em zona de sobrevenda
                    not entry_analysis.get('is_downtrend', True)  # Não está em downtrend forte
                ):
                    # 1H em correção, mas pode estar formando fundo
                    entry_score += 10  # Pontuação moderada
            elif signal_type == 'VENDA':  # CORRIGIDO: Agora está no mesmo nível do primeiro if
                # Tendência principal é BAIXA no 4H
                if entry_analysis.get('is_downtrend', False):
                    # 1H já está alinhado com 4H
                    entry_score += 25  # Pontuação máxima
                elif (
                    entry_analysis.get('rsi', 50) > 45 and  # RSI não está sobrevenda
                    not entry_analysis.get('momentum_positive', True) and  # Momentum voltando negativo
                    entry_analysis.get('price_change', 0) < -0.005  # Movimento de pelo menos 0.5% para baixo
                ):
                    # 1H está retomando a direção do 4H
                    entry_score += 20  # Boa pontuação para retomada
                elif (
                    entry_analysis.get('rsi', 50) > 55 and  # RSI em zona de sobrecompra
                    not entry_analysis.get('is_uptrend', True)  # Não está em uptrend forte
                ):
                    # 1H em correção, mas pode estar formando topo
                    entry_score += 10  # Pontuação moderada
            
            # 3. Análise de RSI (20 pontos)
            rsi_score = 0
            rsi_value = entry_analysis.get('rsi', 50)
            
            if signal_type == 'COMPRA':
                if 30 <= rsi_value <= 50:  # RSI em zona boa para compra
                    rsi_score += 20
                elif 20 <= rsi_value < 30:  # RSI sobrevenda
                    rsi_score += 15
                elif 50 < rsi_value <= 60:  # RSI neutro alto
                    rsi_score += 10
            else:  # VENDA
                if 50 <= rsi_value <= 70:  # RSI em zona boa para venda
                    rsi_score += 20
                elif 70 < rsi_value <= 80:  # RSI sobrecompra
                    rsi_score += 15
                elif 40 <= rsi_value < 50:  # RSI neutro baixo
                    rsi_score += 10
            
            # 4. Padrões Técnicos (20 pontos)
            pattern_score = 0
            
            # Verificar padrões de candlestick
            if len(entry_df) >= 3:
                last_candles = entry_df.tail(3)
                
                # Padrão de reversão
                if signal_type == 'COMPRA':
                    # Martelo ou doji em baixa
                    last_close = last_candles['close'].iloc[-1]
                    last_open = last_candles['open'].iloc[-1]
                    last_low = last_candles['low'].iloc[-1]
                    last_high = last_candles['high'].iloc[-1]
                    
                    body_size = abs(last_close - last_open)
                    lower_shadow = min(last_close, last_open) - last_low
                    
                    if lower_shadow > body_size * 2:  # Martelo
                        pattern_score += 15
                    elif body_size < (last_high - last_low) * 0.3:  # Doji
                        pattern_score += 10
                else:  # VENDA
                    # Estrela cadente ou doji em alta
                    last_close = last_candles['close'].iloc[-1]
                    last_open = last_candles['open'].iloc[-1]
                    last_low = last_candles['low'].iloc[-1]
                    last_high = last_candles['high'].iloc[-1]
                    
                    body_size = abs(last_close - last_open)
                    upper_shadow = last_high - max(last_close, last_open)
                    
                    if upper_shadow > body_size * 2:  # Estrela cadente
                        pattern_score += 15
                    elif body_size < (last_high - last_low) * 0.3:  # Doji
                        pattern_score += 10
            
            # Calcular pontuação total de qualidade
            quality_score = trend_score + entry_score + rsi_score + pattern_score
            
            # Classificar sinal baseado na pontuação
            if quality_score >= 90:
                signal_class = 'ELITE'
            elif quality_score >= 80:
                signal_class = 'PREMIUM'
            elif quality_score >= 60:  # Reduzido para capturar mais sinais
                signal_class = 'PADRÃO'
            else:
                signal_class = 'Descartado'
                return None  # Não salvar sinais com qualidade baixa
            
            # Calcular preço alvo APÓS ter todos os dados
            target_price = self.calculate_target_price(
                entry_price, 
                signal_type, 
                trend, 
                market_conditions, 
                quality_score
            )
            
            # Criar sinal
            # Simplificar o retorno para apenas as informações necessárias
            signal = {
                'symbol': symbol,
                'type': signal_type,  # 'COMPRA' ou 'VENDA'
                'entry_price': entry_price,
                'target_price': target_price,
                'quality_score': quality_score,
                'signal_class': signal_class,
                'entry_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                # Adicionar os campos necessários para o display
                'trend_score': trend_score,
                'entry_score': entry_score,
                'rsi_score': rsi_score,
                'pattern_score': pattern_score,
                'rsi': entry_analysis.get('rsi', 50)
            }
            
            return signal
            
        except Exception as e:
            print(f"❌ Erro na análise de {symbol}: {e}")
            return None

    def analyze_trend_df(self, df: pd.DataFrame) -> Optional[Dict]:
        """Analisa tendência do DataFrame"""
        try:
            # Calcular indicadores - conversão explícita para Series
            close_series = pd.Series(df['close'].values, dtype=float)
            ema20 = EMAIndicator(close=close_series, window=20).ema_indicator()
            ema50 = EMAIndicator(close=close_series, window=50).ema_indicator()
            macd_line = MACD(close=close_series).macd()
            macd_signal = MACD(close=close_series).macd_signal()
            
            current_price = df['close'].iloc[-1]
            current_ema20 = ema20.iloc[-1]
            current_ema50 = ema50.iloc[-1]
            
            # CONDIÇÕES MAIS CLARAS para detectar tendências
            # Uptrend: Preço acima da EMA20 E EMA20 > EMA50
            is_uptrend = (
                current_price > current_ema20 * 0.995 and  # Preço pelo menos 0.5% próximo ou acima da EMA20
                current_ema20 > current_ema50 * 1.005      # EMA20 claramente acima da EMA50 (0.5%)
            )
            
            # Downtrend: Preço abaixo da EMA20 E EMA20 < EMA50
            is_downtrend = (
                current_price < current_ema20 * 1.005 and  # Preço pelo menos 0.5% próximo ou abaixo da EMA20
                current_ema20 < current_ema50 * 0.995      # EMA20 claramente abaixo da EMA50 (0.5%)
            )
            
            # Verificação secundária para casos onde nenhuma tendência é detectada
            if not is_uptrend and not is_downtrend:
                # Se o preço está acima da EMA50, considerar tendência de alta
                if current_price > current_ema50 * 1.01:  # Preço 1% acima da EMA50
                    is_uptrend = True
                # Se o preço está abaixo da EMA50, considerar tendência de baixa
                elif current_price < current_ema50 * 0.99:  # Preço 1% abaixo da EMA50
                    is_downtrend = True
                # Caso contrário, usar a inclinação da EMA20 para determinar a tendência
                else:
                    ema20_slope = (current_ema20 - ema20.iloc[-6]) / ema20.iloc[-6]  # Inclinação das últimas 5 velas
                    if ema20_slope > 0.002:  # Inclinação positiva de 0.2%
                        is_uptrend = True
                    elif ema20_slope < -0.002:  # Inclinação negativa de 0.2%
                        is_downtrend = True
                    # Se ainda não tiver tendência clara, usar o MACD como último recurso
                    elif macd_line.iloc[-1] > macd_signal.iloc[-1]:
                        is_uptrend = True
                    else:
                        is_downtrend = True
            
            # Garantir que não tenhamos tendências conflitantes
            if is_uptrend and is_downtrend:
                # Decidir com base na força relativa da EMA20 vs EMA50
                ema_ratio = current_ema20 / current_ema50
                if ema_ratio > 1:
                    is_downtrend = False  # Priorizar tendência de alta
                else:
                    is_uptrend = False    # Priorizar tendência de baixa
            
            # Calcular força da tendência
            trend_strength = abs(current_price - current_ema20) / current_price
            
            # Volume trend
            volume_trend = 1 if df['volume'].tail(5).mean() > df['volume'].tail(10).mean() else 0
            
            return {
                'is_uptrend': is_uptrend,
                'is_downtrend': is_downtrend,
                'trend_strength': trend_strength,
                'close': current_price,
                'ema20': current_ema20,
                'ema50': current_ema50,
                'macd_signal': macd_line.iloc[-1] - macd_signal.iloc[-1],
                'volume_trend': volume_trend
            }
            
        except Exception as e:
            print(f"❌ Erro na análise de tendência: {e}")
            return None

    def calculate_market_conditions(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calcula condições de mercado como volatilidade e momentum"""
        try:
            # Calcular ATR para volatilidade
            atr = AverageTrueRange(
                high=pd.Series(df['high'].values, dtype=float),
                low=pd.Series(df['low'].values, dtype=float),
                close=pd.Series(df['close'].values, dtype=float),
                window=14
            ).average_true_range()
            
            current_price = df['close'].iloc[-1]
            volatility = (atr.iloc[-1] / current_price) * 100
            
            # Calcular momentum
            price_change_24h = (current_price - df['close'].iloc[-24]) / df['close'].iloc[-24] * 100 if len(df) >= 24 else 0
            price_change_12h = (current_price - df['close'].iloc[-12]) / df['close'].iloc[-12] * 100 if len(df) >= 12 else 0
            
            # Volume relativo
            volume_ratio = df['volume'].tail(5).mean() / df['volume'].tail(20).mean() if len(df) >= 20 else 1.0
            
            return {
                'volatility': volatility,
                'price_change_24h': price_change_24h,
                'price_change_12h': price_change_12h,
                'volume_ratio': volume_ratio
            }
            
        except Exception as e:
            print(f"❌ Erro ao calcular condições de mercado: {e}")
            return {
                'volatility': 2.0,
                'price_change_24h': 0.0,
                'price_change_12h': 0.0,
                'volume_ratio': 1.0
            }

    def analyze_entry_df(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analisa condições de entrada no timeframe menor"""
        try:
            # Calcular indicadores - conversão explícita para Series
            close_series = pd.Series(df['close'].values, dtype=float)
            ema20 = EMAIndicator(close=close_series, window=20).ema_indicator()
            ema50 = EMAIndicator(close=close_series, window=50).ema_indicator()
            rsi = RSIIndicator(close=close_series, window=14).rsi()
            
            current_price = df['close'].iloc[-1]
            current_ema20 = ema20.iloc[-1]
            current_ema50 = ema50.iloc[-1]
            current_rsi = rsi.iloc[-1]
            
            # Condições de tendência (mais tolerantes que na análise de tendência)
            is_uptrend = current_price > current_ema20 * 0.99 and current_ema20 > current_ema50 * 1.002
            is_downtrend = current_price < current_ema20 * 1.01 and current_ema20 < current_ema50 * 0.998
            
            # Momentum
            price_change = (current_price - df['close'].iloc[-3]) / df['close'].iloc[-3] if len(df) >= 3 else 0
            momentum_positive = price_change > 0
            
            # Verificar se o preço está se aproximando da EMA20 (possível entrada)
            price_to_ema20_ratio = current_price / current_ema20
            approaching_ema20 = 0.995 < price_to_ema20_ratio < 1.005
            
            return {
                'is_uptrend': is_uptrend,
                'is_downtrend': is_downtrend,
                'rsi': current_rsi,
                'price_change': price_change,
                'momentum_positive': momentum_positive,
                'approaching_ema20': approaching_ema20
            }
            
        except Exception as e:
            print(f"❌ Erro na análise de entrada: {e}")
            return {
                'is_uptrend': False,
                'is_downtrend': False,
                'rsi': 50.0,
                'price_change': 0.0,
                'momentum_positive': False,
                'approaching_ema20': False
            }