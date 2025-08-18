# -*- coding: utf-8 -*-
"""
BTC Correlation Analyzer - Sistema de Análise de Correlação com Bitcoin
Este módulo analisa a correlação entre altcoins e Bitcoin para melhorar a precisão dos sinais.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Any, Tuple
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange
import time
import traceback
from .binance_client import BinanceClient

class BTCCorrelationAnalyzer:
    """
    Analisador de correlação entre altcoins e Bitcoin
    Fornece insights sobre como o BTC influencia outros pares
    """
    
    def __init__(self, binance_client: BinanceClient):
        """Inicializa o analisador de correlação BTC"""
        print("₿ Inicializando BTCCorrelationAnalyzer...")
        
        self.binance = binance_client
        self.btc_symbol = 'BTCUSDT'
        
        # Cache para análises BTC
        self.btc_cache = {
            'last_update': 0,
            'cache_duration': 300,  # 5 minutos
            'analysis_4h': None,
            'analysis_1h': None,
            'current_analysis': None
        }
        
        # Cache para correlações
        self.correlation_cache = {
            'last_update': 0,
            'cache_duration': 3600,  # 1 hora
            'correlations': {}
        }
        
        # Configurações de correlação
        self.correlation_config = {
            'lookback_periods': 100,  # Períodos para calcular correlação
            'high_correlation_threshold': 0.8,
            'medium_correlation_threshold': 0.5,
            'low_correlation_threshold': 0.2
        }
        
        print("✅ BTCCorrelationAnalyzer inicializado com sucesso!")
    
    def get_btc_price_data(self) -> Dict[str, Any]:
        """Obtém dados básicos de preço do BTC para a API"""
        try:
            # Obter dados recentes do BTC
            btc_df = self._get_btc_klines('1h', 24)  # Últimas 24 horas
            if btc_df is None or len(btc_df) < 2:
                return self._get_default_price_data()
            
            current_price = float(btc_df['close'].iloc[-1])
            previous_price = float(btc_df['close'].iloc[-2])
            high_24h = float(btc_df['high'].max())
            low_24h = float(btc_df['low'].min())
            volume_24h = float(btc_df['volume'].sum())
            
            # Calcular variação
            change_24h = ((current_price - previous_price) / previous_price) * 100
            
            return {
                'symbol': 'BTCUSDT',
                'price': current_price,
                'change_24h': change_24h,
                'high_24h': high_24h,
                'low_24h': low_24h,
                'volume_24h': volume_24h,
                'last_updated': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            }
            
        except Exception as e:
            print(f"❌ Erro ao obter dados de preço BTC: {e}")
            return self._get_default_price_data()
    
    def _get_default_price_data(self) -> Dict[str, Any]:
        """Retorna dados de preço padrão em caso de erro"""
        return {
            'symbol': 'BTCUSDT',
            'price': 50000.0,
            'change_24h': 0.0,
            'high_24h': 50000.0,
            'low_24h': 50000.0,
            'volume_24h': 0.0,
            'last_updated': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        }
    
    def get_btc_analysis(self, timeframe: str = '4h') -> Optional[Dict[str, Any]]:
        """
        Obtém análise técnica completa do Bitcoin
        
        Args:
            timeframe: Timeframe para análise ('1h', '4h', '1d')
            
        Returns:
            Dict com análise técnica do BTC ou None se erro
        """
        try:
            # Verificar cache
            current_time = time.time()
            cache_key = f'analysis_{timeframe}'
            
            if (cache_key in self.btc_cache and 
                self.btc_cache[cache_key] and 
                current_time - self.btc_cache['last_update'] < self.btc_cache['cache_duration']):
                return self.btc_cache[cache_key]
            
            # Obter dados do BTC
            btc_df = self._get_btc_klines(timeframe)
            if btc_df is None or len(btc_df) < 50:
                return None
            
            # Análise técnica completa
            analysis = self._analyze_btc_dataframe(btc_df, timeframe)
            
            # Atualizar cache
            self.btc_cache[cache_key] = analysis
            self.btc_cache['last_update'] = current_time
            
            return analysis
            
        except Exception as e:
            print(f"❌ Erro na análise BTC {timeframe}: {e}")
            return None
    
    def get_current_btc_analysis(self) -> Dict[str, Any]:
        """
        Obtém análise BTC consolidada (4H + 1H)
        
        Returns:
            Dict com análise consolidada do BTC
        """
        try:
            # Verificar cache
            current_time = time.time()
            if (self.btc_cache['current_analysis'] and 
                current_time - self.btc_cache['last_update'] < self.btc_cache['cache_duration']):
                return self.btc_cache['current_analysis']
            
            # Obter análises
            btc_4h = self.get_btc_analysis('4h')
            btc_1h = self.get_btc_analysis('1h')
            
            if not btc_4h or not btc_1h:
                return self._get_default_btc_analysis()
            
            # Consolidar análises
            consolidated = self._consolidate_btc_analysis(btc_4h, btc_1h)
            
            # Atualizar cache
            self.btc_cache['current_analysis'] = consolidated
            
            return consolidated
            
        except Exception as e:
            print(f"❌ Erro na análise BTC consolidada: {e}")
            return self._get_default_btc_analysis()
    
    def calculate_symbol_btc_correlation(self, symbol: str, timeframe: str = '1h', 
                                       periods: int = 100) -> float:
        """
        Calcula correlação entre um símbolo e o BTC
        
        Args:
            symbol: Símbolo para calcular correlação
            timeframe: Timeframe para análise
            periods: Número de períodos para cálculo
            
        Returns:
            Valor de correlação entre -1.0 e 1.0
        """
        try:
            # Verificar cache
            cache_key = f"{symbol}_{timeframe}_{periods}"
            current_time = time.time()
            
            if (cache_key in self.correlation_cache['correlations'] and 
                current_time - self.correlation_cache['last_update'] < self.correlation_cache['cache_duration']):
                return self.correlation_cache['correlations'][cache_key]
            
            # Obter dados
            symbol_df = self._get_symbol_klines(symbol, timeframe, periods)
            btc_df = self._get_btc_klines(timeframe, periods)
            
            if symbol_df is None or btc_df is None:
                return 0.5  # Correlação neutra como fallback
            
            # Calcular correlação
            correlation = self._calculate_price_correlation(symbol_df, btc_df)
            
            # Atualizar cache
            self.correlation_cache['correlations'][cache_key] = correlation
            self.correlation_cache['last_update'] = current_time
            
            return correlation
            
        except Exception as e:
            print(f"❌ Erro ao calcular correlação {symbol}: {e}")
            return 0.5  # Correlação neutra como fallback
    
    def classify_correlation_strength(self, correlation: float) -> str:
        """
        Classifica a força da correlação
        
        Args:
            correlation: Valor de correlação
            
        Returns:
            Classificação da correlação
        """
        abs_corr = abs(correlation)
        
        if abs_corr >= self.correlation_config['high_correlation_threshold']:
            return 'HIGH'
        elif abs_corr >= self.correlation_config['medium_correlation_threshold']:
            return 'MEDIUM'
        elif abs_corr >= self.correlation_config['low_correlation_threshold']:
            return 'LOW'
        else:
            return 'VERY_LOW'
    
    def calculate_btc_correlation_score(self, symbol: str, signal_type: str) -> float:
        """
        Calcula pontuação baseada na correlação com BTC
        
        Args:
            symbol: Símbolo do par
            signal_type: Tipo do sinal ('COMPRA' ou 'VENDA')
            
        Returns:
            Pontuação de correlação (0-30 pontos)
        """
        try:
            # Obter análise BTC e correlação
            btc_analysis = self.get_current_btc_analysis()
            correlation = self.calculate_symbol_btc_correlation(symbol)
            correlation_strength = self.classify_correlation_strength(correlation)
            
            score = 0.0
            
            # 1. ALINHAMENTO COM BTC (20 pontos)
            btc_trend = btc_analysis['trend']
            btc_strength = btc_analysis['strength']
            
            if correlation_strength in ['HIGH', 'MEDIUM']:
                # Para moedas correlacionadas, alinhamento é crucial
                if ((signal_type == 'COMPRA' and btc_trend == 'BULLISH') or 
                    (signal_type == 'VENDA' and btc_trend == 'BEARISH')):
                    score += 20.0 * (abs(correlation) * btc_strength / 100)
                elif btc_trend == 'NEUTRAL':
                    score += 10.0
                else:
                    # Penalizar sinais contra BTC forte
                    score -= 10.0 * (abs(correlation) * btc_strength / 100)
            
            # 2. FORÇA INDEPENDENTE (10 pontos)
            if correlation_strength in ['LOW', 'VERY_LOW']:
                # Bônus para moedas independentes
                score += 10.0 * (1 - abs(correlation))
            
            # 3. DIVERGÊNCIA POSITIVA (5 pontos)
            if self._detect_positive_divergence(symbol, btc_analysis):
                score += 5.0
            
            # 4. MOMENTUM BTC (5 pontos)
            if btc_analysis['momentum_aligned']:
                if correlation_strength in ['HIGH', 'MEDIUM']:
                    score += 5.0 * abs(correlation)
            
            # Garantir que score está entre 0 e 30
            return max(0.0, min(30.0, score))
            
        except Exception as e:
            print(f"❌ Erro ao calcular score de correlação: {e}")
            return 0.0
    
    def should_filter_signal_by_btc(self, symbol: str, signal_type: str) -> bool:
        """
        Determina se um sinal deve ser filtrado baseado na análise BTC
        
        Args:
            symbol: Símbolo do par
            signal_type: Tipo do sinal
            
        Returns:
            True se o sinal deve ser rejeitado
        """
        try:
            btc_analysis = self.get_current_btc_analysis()
            correlation = self.calculate_symbol_btc_correlation(symbol)
            correlation_strength = self.classify_correlation_strength(correlation)
            
            # Filtros para moedas altamente correlacionadas
            if correlation_strength == 'HIGH' and abs(correlation) > 0.8:
                btc_trend = btc_analysis['trend']
                btc_strength = btc_analysis['strength']
                
                # Rejeitar se BTC está em tendência forte oposta
                if btc_strength > 70:
                    if ((signal_type == 'COMPRA' and btc_trend == 'BEARISH') or 
                        (signal_type == 'VENDA' and btc_trend == 'BULLISH')):
                        return True
                
                # Rejeitar se BTC está em zona de indecisão crítica
                if btc_analysis.get('pivot_broken', False) and btc_strength < 30:
                    return True
            
            return False
            
        except Exception as e:
            print(f"❌ Erro no filtro BTC: {e}")
            return False
    
    def _get_btc_klines(self, timeframe: str, limit: int = 100) -> Optional[pd.DataFrame]:
        """Obtém dados de klines do BTC"""
        try:
            klines_data = self.binance.get_klines(self.btc_symbol, timeframe, limit)
            if not klines_data:
                return None
            
            df = pd.DataFrame(klines_data)
            numeric_columns = ['open', 'high', 'low', 'close', 'volume']
            
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            return df[numeric_columns].copy() if all(col in df.columns for col in numeric_columns) else None
            
        except Exception as e:
            print(f"❌ Erro ao obter klines BTC: {e}")
            return None
    
    def _get_symbol_klines(self, symbol: str, timeframe: str, limit: int = 100) -> Optional[pd.DataFrame]:
        """Obtém dados de klines de um símbolo"""
        try:
            klines_data = self.binance.get_klines(symbol, timeframe, limit)
            if not klines_data:
                return None
            
            df = pd.DataFrame(klines_data)
            numeric_columns = ['open', 'high', 'low', 'close', 'volume']
            
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            return df[numeric_columns].copy() if all(col in df.columns for col in numeric_columns) else None
            
        except Exception as e:
            print(f"❌ Erro ao obter klines {symbol}: {e}")
            return None
    
    def _analyze_btc_dataframe(self, df: pd.DataFrame, timeframe: str) -> Dict[str, Any]:
        """Analisa DataFrame do BTC e retorna métricas técnicas"""
        try:
            close_series = pd.Series(df['close'].values, dtype=float)
            
            # Indicadores técnicos
            ema20 = EMAIndicator(close=close_series, window=20).ema_indicator()
            ema50 = EMAIndicator(close=close_series, window=50).ema_indicator()
            rsi = RSIIndicator(close=close_series, window=14).rsi()
            macd = MACD(close=close_series)
            atr = AverageTrueRange(high=df['high'], low=df['low'], close=df['close']).average_true_range()
            
            current_price = df['close'].iloc[-1]
            current_ema20 = ema20.iloc[-1]
            current_ema50 = ema50.iloc[-1]
            current_rsi = rsi.iloc[-1]
            current_atr = atr.iloc[-1]
            
            # Análise de tendência
            trend_analysis = self._analyze_btc_trend(df, ema20, ema50)
            
            # Análise de momentum
            momentum_analysis = self._analyze_btc_momentum(df, rsi, macd)
            
            # Análise de volatilidade
            volatility_analysis = self._analyze_btc_volatility(df, atr)
            
            return {
                'timeframe': timeframe,
                'price': current_price,
                'ema20': current_ema20,
                'ema50': current_ema50,
                'rsi': current_rsi,
                'atr': current_atr,
                **trend_analysis,
                **momentum_analysis,
                **volatility_analysis,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            print(f"❌ Erro na análise BTC DataFrame: {e}")
            return self._get_default_btc_analysis()
    
    def _analyze_btc_trend(self, df: pd.DataFrame, ema20: pd.Series, ema50: pd.Series) -> Dict[str, Any]:
        """Analisa tendência do BTC"""
        try:
            current_price = df['close'].iloc[-1]
            current_ema20 = ema20.iloc[-1]
            current_ema50 = ema50.iloc[-1]
            
            # Determinar tendência
            if current_price > current_ema20 * 1.005 and current_ema20 > current_ema50 * 1.01:
                trend = 'BULLISH'
                strength = min(100, abs(current_price - current_ema20) / current_price * 1000)
            elif current_price < current_ema20 * 0.995 and current_ema20 < current_ema50 * 0.99:
                trend = 'BEARISH'
                strength = min(100, abs(current_price - current_ema20) / current_price * 1000)
            else:
                trend = 'NEUTRAL'
                strength = 50
            
            # Detectar rompimento de pivot
            pivot_broken = self._detect_pivot_break(df)
            
            return {
                'trend': trend,
                'strength': float(strength),
                'pivot_broken': bool(pivot_broken),
                'ema_alignment': bool(current_price > current_ema20 > current_ema50)
            }
            
        except Exception as e:
            print(f"❌ Erro na análise de tendência BTC: {e}")
            return {'trend': 'NEUTRAL', 'strength': 50, 'pivot_broken': False, 'ema_alignment': False}
    
    def _analyze_btc_momentum(self, df: pd.DataFrame, rsi: pd.Series, macd: MACD) -> Dict[str, Any]:
        """Analisa momentum do BTC"""
        try:
            current_rsi = rsi.iloc[-1]
            macd_line = macd.macd().iloc[-1]
            macd_signal = macd.macd_signal().iloc[-1]
            macd_histogram = macd.macd_diff().iloc[-1]
            
            # Análise RSI
            if current_rsi > 70:
                rsi_condition = 'OVERBOUGHT'
            elif current_rsi < 30:
                rsi_condition = 'OVERSOLD'
            else:
                rsi_condition = 'NEUTRAL'
            
            # Análise MACD
            macd_bullish = macd_line > macd_signal and macd_histogram > 0
            macd_bearish = macd_line < macd_signal and macd_histogram < 0
            
            momentum_aligned = (
                (macd_bullish and current_rsi > 50) or 
                (macd_bearish and current_rsi < 50)
            )
            
            return {
                'rsi_condition': rsi_condition,
                'macd_bullish': bool(macd_bullish),
                'macd_bearish': bool(macd_bearish),
                'momentum_aligned': bool(momentum_aligned)
            }
            
        except Exception as e:
            print(f"❌ Erro na análise de momentum BTC: {e}")
            return {
                'rsi_condition': 'NEUTRAL',
                'macd_bullish': False,
                'macd_bearish': False,
                'momentum_aligned': False
            }
    
    def _analyze_btc_volatility(self, df: pd.DataFrame, atr: pd.Series) -> Dict[str, Any]:
        """Analisa volatilidade do BTC"""
        try:
            current_atr = atr.iloc[-1]
            current_price = df['close'].iloc[-1]
            atr_percentage = (current_atr / current_price) * 100
            
            # Classificar volatilidade
            if atr_percentage > 5:
                volatility_level = 'HIGH'
            elif atr_percentage > 2:
                volatility_level = 'MEDIUM'
            else:
                volatility_level = 'LOW'
            
            return {
                'atr_percentage': atr_percentage,
                'volatility_level': volatility_level
            }
            
        except Exception as e:
            print(f"❌ Erro na análise de volatilidade BTC: {e}")
            return {'atr_percentage': 2.0, 'volatility_level': 'MEDIUM'}
    
    def _consolidate_btc_analysis(self, btc_4h: Dict, btc_1h: Dict) -> Dict[str, Any]:
        """Consolida análises de diferentes timeframes"""
        try:
            # Tendência principal (4H tem mais peso)
            main_trend = btc_4h['trend']
            trend_strength = (btc_4h['strength'] * 0.7) + (btc_1h['strength'] * 0.3)
            
            # Momentum (1H tem mais peso para entrada)
            momentum_aligned = btc_1h['momentum_aligned']
            
            # Volatilidade (média dos dois)
            volatility = (btc_4h['atr_percentage'] + btc_1h['atr_percentage']) / 2
            
            return {
                'trend': main_trend,
                'strength': float(trend_strength),
                'momentum_aligned': bool(momentum_aligned),
                'volatility': float(volatility),
                'pivot_broken': bool(btc_4h['pivot_broken'] or btc_1h['pivot_broken']),
                'timeframes': {
                    '4h': btc_4h,
                    '1h': btc_1h
                }
            }
            
        except Exception as e:
            print(f"❌ Erro na consolidação BTC: {e}")
            return self._get_default_btc_analysis()
    
    def _calculate_price_correlation(self, symbol_df: pd.DataFrame, btc_df: pd.DataFrame) -> float:
        """Calcula correlação de preços entre símbolo e BTC"""
        try:
            # Alinhar DataFrames pelo tamanho
            min_length = min(len(symbol_df), len(btc_df))
            
            symbol_returns = symbol_df['close'].tail(min_length).pct_change().dropna()
            btc_returns = btc_df['close'].tail(min_length).pct_change().dropna()
            
            # Alinhar novamente após dropna
            min_length = min(len(symbol_returns), len(btc_returns))
            
            if min_length < 10:
                return 0.5  # Dados insuficientes
            
            correlation = symbol_returns.tail(min_length).corr(btc_returns.tail(min_length))
            
            # Tratar NaN
            if pd.isna(correlation):
                return 0.5
            
            return float(correlation)
            
        except Exception as e:
            print(f"❌ Erro no cálculo de correlação: {e}")
            return 0.5
    
    def _detect_pivot_break(self, df: pd.DataFrame) -> bool:
        """Detecta rompimento de pivot points"""
        try:
            if len(df) < 20:
                return False
            
            # Calcular pivot points simples
            high_pivot = df['high'].rolling(window=5, center=True).max()
            low_pivot = df['low'].rolling(window=5, center=True).min()
            
            current_price = df['close'].iloc[-1]
            recent_high = high_pivot.dropna().iloc[-5:].max()
            recent_low = low_pivot.dropna().iloc[-5:].max()
            
            # Detectar rompimentos
            upward_break = current_price > recent_high * 1.01
            downward_break = current_price < recent_low * 0.99
            
            return upward_break or downward_break
            
        except Exception as e:
            print(f"❌ Erro na detecção de pivot: {e}")
            return False
    
    def _detect_positive_divergence(self, symbol: str, btc_analysis: Dict) -> bool:
        """Detecta divergência positiva entre símbolo e BTC"""
        try:
            # Obter dados do símbolo
            symbol_df = self._get_symbol_klines(symbol, '1h', 50)
            if symbol_df is None:
                return False
            
            # Análise simples de divergência
            symbol_change = (symbol_df['close'].iloc[-1] - symbol_df['close'].iloc[-10]) / symbol_df['close'].iloc[-10]
            
            # Se BTC está fraco mas símbolo está forte
            if btc_analysis['trend'] == 'BEARISH' and symbol_change > 0.02:
                return True
            
            # Se BTC está neutro mas símbolo tem momentum
            if btc_analysis['trend'] == 'NEUTRAL' and abs(symbol_change) > 0.05:
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Erro na detecção de divergência: {e}")
            return False
    
    def _get_default_btc_analysis(self) -> Dict[str, Any]:
        """Retorna análise BTC padrão em caso de erro"""
        return {
            'trend': 'NEUTRAL',
            'strength': 50.0,
            'momentum_aligned': False,
            'volatility': 2.0,
            'pivot_broken': False,
            'rsi_condition': 'NEUTRAL',
            'macd_bullish': False,
            'macd_bearish': False
        }