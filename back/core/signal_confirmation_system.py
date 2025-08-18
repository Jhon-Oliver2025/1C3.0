# Imports necessários
from typing import Dict, Optional, List, Any, Tuple
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from .binance_client import BinanceClient
from .btc_correlation_analyzer import BTCCorrelationAnalyzer
import traceback

class ConfirmationCriteria:
    """Critérios de confirmação de sinais"""
    
    # Pesos para diferentes tipos de confirmação (total = 100)
    WEIGHTS = {
        'price_breakout': 30,      # Rompimento de preço
        'volume_confirmation': 25,  # Confirmação de volume
        'btc_alignment': 20,       # Alinhamento com BTC
        'momentum_sustainability': 15, # Sustentação do momentum
        'technical_patterns': 10   # Padrões técnicos
    }
    
    # Thresholds para confirmação
    THRESHOLDS = {
        'min_confirmation_score': 70,  # Mínimo 70 pontos para confirmar
        'max_rejection_score': 30,     # Máximo 30 pontos para rejeitar
        'breakout_percentage': 0.5,    # 0.5% mínimo para rompimento
        'volume_increase': 1.3,        # 30% aumento mínimo no volume
        'momentum_candles': 2,         # Mínimo 2 velas confirmando momentum
        'btc_strength_threshold': 0.4  # Threshold para força BTC
    }

class SignalConfirmationSystem:
    """Sistema avançado de confirmação de sinais"""
    
    def __init__(self, binance_client: BinanceClient):
        """Inicializa o sistema de confirmação"""
        print("🔍 Inicializando SignalConfirmationSystem...")
        
        self.binance = binance_client
        self.btc_analyzer = BTCCorrelationAnalyzer(binance_client)
        
        # Configurações do sistema
        self.config = {
            'analysis_timeframes': ['1h', '4h'],
            'volume_analysis_periods': [5, 10, 20],
            'momentum_analysis_candles': 5,
            'support_resistance_window': 20,
            'btc_correlation_threshold': 0.3
        }
        
        print("✅ SignalConfirmationSystem inicializado!")
    
    def analyze_signal_confirmation(self, signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa se um sinal deve ser confirmado"""
        try:
            symbol = signal_data['symbol']
            signal_type = signal_data['type']
            entry_price = signal_data['entry_price']
            
            print(f"🔍 Analisando confirmação para {symbol} - {signal_type}")
            
            # Obter dados atuais do mercado
            market_data = self._get_comprehensive_market_data(symbol)
            if not market_data:
                return self._create_confirmation_result('insufficient_data', 0, [])
            
            # Calcular scores de confirmação
            confirmation_scores = {
                'price_breakout': self._analyze_price_breakout(signal_data, market_data),
                'volume_confirmation': self._analyze_volume_confirmation(signal_data, market_data),
                'btc_alignment': self._analyze_btc_alignment(signal_data),
                'momentum_sustainability': self._analyze_momentum_sustainability(signal_data, market_data),
                'technical_patterns': self._analyze_technical_patterns(signal_data, market_data)
            }
            
            # Calcular score total ponderado
            total_score = sum(
                score * ConfirmationCriteria.WEIGHTS[criteria] / 100
                for criteria, score in confirmation_scores.items()
            )
            
            # Determinar ação baseada no score
            if total_score >= ConfirmationCriteria.THRESHOLDS['min_confirmation_score']:
                action = 'confirm'
            elif total_score <= ConfirmationCriteria.THRESHOLDS['max_rejection_score']:
                action = 'reject'
            else:
                action = 'wait'
            
            # Gerar razões detalhadas
            reasons = self._generate_confirmation_reasons(confirmation_scores, action)
            
            return self._create_confirmation_result(action, total_score, reasons, confirmation_scores)
            
        except Exception as e:
            print(f"❌ Erro na análise de confirmação: {e}")
            traceback.print_exc()
            return self._create_confirmation_result('error', 0, ['ANALYSIS_ERROR'])
    
    def _get_comprehensive_market_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Obtém dados abrangentes do mercado para análise"""
        try:
            # Obter klines para diferentes timeframes
            klines_1h = self.binance.get_klines(symbol, '1h', 50)
            klines_4h = self.binance.get_klines(symbol, '4h', 20)
            
            if not klines_1h or not klines_4h:
                return None
            
            # Obter dados de ticker 24h
            ticker_data = self.binance.get_24h_ticker_data([symbol])
            if not ticker_data or symbol not in ticker_data:
                return None
            
            # Converter para DataFrames
            df_1h = pd.DataFrame(klines_1h)
            df_4h = pd.DataFrame(klines_4h)
            
            # Converter colunas numéricas
            numeric_columns = ['open', 'high', 'low', 'close', 'volume']
            for col in numeric_columns:
                df_1h[col] = pd.to_numeric(df_1h[col], errors='coerce')
                df_4h[col] = pd.to_numeric(df_4h[col], errors='coerce')
            
            return {
                'klines_1h': df_1h,
                'klines_4h': df_4h,
                'ticker_24h': ticker_data[symbol],
                'current_price': float(df_1h['close'].iloc[-1]),
                'current_volume': float(df_1h['volume'].iloc[-1])
            }
            
        except Exception as e:
            print(f"❌ Erro ao obter dados do mercado: {e}")
            return None
    
    def _analyze_price_breakout(self, signal_data: Dict[str, Any], market_data: Dict[str, Any]) -> float:
        """Analisa rompimento de preço (0-100 pontos)"""
        try:
            current_price = market_data['current_price']
            entry_price = signal_data['entry_price']
            signal_type = signal_data['type']
            
            # Calcular porcentagem de movimento
            price_change_pct = abs(current_price - entry_price) / entry_price * 100
            
            # Verificar direção do movimento
            if signal_type == 'COMPRA':
                movement_correct = current_price > entry_price
                breakout_threshold = ConfirmationCriteria.THRESHOLDS['breakout_percentage']
            else:  # VENDA
                movement_correct = current_price < entry_price
                breakout_threshold = ConfirmationCriteria.THRESHOLDS['breakout_percentage']
            
            # Calcular score baseado no movimento
            if not movement_correct:
                # Movimento na direção errada
                return max(0, 50 - price_change_pct * 10)  # Penalizar movimento contrário
            
            # Movimento na direção correta
            if price_change_pct >= breakout_threshold:
                # Rompimento confirmado
                score = min(100, 70 + price_change_pct * 10)  # Bonus por rompimento maior
            else:
                # Movimento correto mas ainda não rompeu
                score = 50 + (price_change_pct / breakout_threshold) * 20
            
            return score
            
        except Exception as e:
            print(f"❌ Erro na análise de breakout: {e}")
            return 50  # Score neutro em caso de erro
    
    def _analyze_volume_confirmation(self, signal_data: Dict[str, Any], market_data: Dict[str, Any]) -> float:
        """Analisa confirmação de volume (0-100 pontos)"""
        try:
            df_1h = market_data['klines_1h']
            
            if len(df_1h) < 20:
                return 50  # Score neutro se dados insuficientes
            
            # Volume das últimas 3 velas vs média das 10 anteriores
            recent_volume = df_1h['volume'].tail(3).mean()
            avg_volume = df_1h['volume'].tail(13).head(10).mean()
            
            volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1
            
            # Calcular score baseado no ratio de volume
            if volume_ratio >= ConfirmationCriteria.THRESHOLDS['volume_increase']:
                # Volume confirmado
                score = min(100, 70 + (volume_ratio - 1.3) * 30)
            elif volume_ratio >= 1.0:
                # Volume normal
                score = 50 + (volume_ratio - 1.0) * 66.7  # 0.3 * 66.7 = 20
            else:
                # Volume baixo
                score = max(0, 50 * volume_ratio)
            
            return score
            
        except Exception as e:
            print(f"❌ Erro na análise de volume: {e}")
            return 50
    
    def _analyze_btc_alignment(self, signal_data: Dict[str, Any]) -> float:
        """Analisa alinhamento com BTC (0-100 pontos)"""
        try:
            signal_type = signal_data['type']
            symbol = signal_data['symbol']
            
            # Obter análise atual do BTC
            btc_analysis = self.btc_analyzer.get_current_btc_analysis()
            
            # Calcular correlação do símbolo com BTC
            btc_correlation = self.btc_analyzer.calculate_symbol_btc_correlation(symbol)
            
            # Score base baseado na correlação
            correlation_score = 50  # Neutro por padrão
            
            if abs(btc_correlation) > self.config['btc_correlation_threshold']:
                # Alta correlação - verificar alinhamento
                btc_trend = btc_analysis['trend']
                btc_strength = btc_analysis['strength']
                
                if signal_type == 'COMPRA':
                    if btc_trend == 'BULLISH':
                        correlation_score = 70 + btc_strength * 30
                    elif btc_trend == 'BEARISH':
                        correlation_score = max(0, 30 - btc_strength * 30)
                    else:  # NEUTRAL
                        correlation_score = 50
                
                else:  # VENDA
                    if btc_trend == 'BEARISH':
                        correlation_score = 70 + btc_strength * 30
                    elif btc_trend == 'BULLISH':
                        correlation_score = max(0, 30 - btc_strength * 30)
                    else:  # NEUTRAL
                        correlation_score = 50
            
            else:
                # Baixa correlação - movimento independente pode ser bom
                correlation_score = 60  # Ligeiramente positivo
            
            return correlation_score
            
        except Exception as e:
            print(f"❌ Erro na análise de alinhamento BTC: {e}")
            return 50
    
    def _analyze_momentum_sustainability(self, signal_data: Dict[str, Any], market_data: Dict[str, Any]) -> float:
        """Analisa sustentação do momentum (0-100 pontos)"""
        try:
            df_1h = market_data['klines_1h']
            signal_type = signal_data['type']
            
            if len(df_1h) < 5:
                return 50
            
            # Analisar últimas 5 velas
            last_5_closes = df_1h['close'].tail(5).values
            
            # Contar velas na direção correta
            correct_direction_count = 0
            
            for i in range(1, len(last_5_closes)):
                if signal_type == 'COMPRA':
                    if last_5_closes[i] > last_5_closes[i-1]:
                        correct_direction_count += 1
                else:  # VENDA
                    if last_5_closes[i] < last_5_closes[i-1]:
                        correct_direction_count += 1
            
            # Calcular score baseado na consistência
            consistency_ratio = correct_direction_count / 4  # 4 comparações possíveis
            
            if consistency_ratio >= 0.75:  # 3+ velas na direção correta
                score = 80 + consistency_ratio * 20
            elif consistency_ratio >= 0.5:  # 2+ velas na direção correta
                score = 50 + consistency_ratio * 40
            else:
                score = consistency_ratio * 50
            
            return score
            
        except Exception as e:
            print(f"❌ Erro na análise de momentum: {e}")
            return 50
    
    def _analyze_technical_patterns(self, signal_data: Dict[str, Any], market_data: Dict[str, Any]) -> float:
        """Analisa padrões técnicos (0-100 pontos)"""
        try:
            df_1h = market_data['klines_1h']
            current_price = market_data['current_price']
            signal_type = signal_data['type']
            
            if len(df_1h) < 20:
                return 50
            
            score = 50  # Score base
            
            # 1. Análise de suporte/resistência
            support_resistance_score = self._analyze_support_resistance(
                df_1h, current_price, signal_type
            )
            
            # 2. Análise de padrões de candlestick
            candlestick_score = self._analyze_candlestick_patterns(
                df_1h, signal_type
            )
            
            # 3. Análise de médias móveis
            ma_score = self._analyze_moving_averages(
                df_1h, current_price, signal_type
            )
            
            # Combinar scores (pesos iguais)
            score = (support_resistance_score + candlestick_score + ma_score) / 3
            
            return score
            
        except Exception as e:
            print(f"❌ Erro na análise de padrões técnicos: {e}")
            return 50
    
    def _analyze_support_resistance(self, df: pd.DataFrame, current_price: float, signal_type: str) -> float:
        """Analisa níveis de suporte e resistência"""
        try:
            # Encontrar máximas e mínimas locais
            highs = df['high'].rolling(window=5, center=True).max()
            lows = df['low'].rolling(window=5, center=True).min()
            
            resistance_levels = []
            support_levels = []
            
            for i in range(2, len(df) - 2):
                if df['high'].iloc[i] == highs.iloc[i]:
                    resistance_levels.append(df['high'].iloc[i])
                if df['low'].iloc[i] == lows.iloc[i]:
                    support_levels.append(df['low'].iloc[i])
            
            # Encontrar nível mais próximo
            if signal_type == 'COMPRA':
                # Para compra, verificar distância do suporte
                if support_levels:
                    nearest_support = max([s for s in support_levels if s < current_price], 
                                        default=current_price * 0.98)
                    distance_pct = abs(current_price - nearest_support) / current_price * 100
                    
                    if 1 <= distance_pct <= 3:  # Próximo do suporte
                        return 80
                    elif distance_pct <= 5:
                        return 60
                    else:
                        return 40
            
            else:  # VENDA
                # Para venda, verificar distância da resistência
                if resistance_levels:
                    nearest_resistance = min([r for r in resistance_levels if r > current_price], 
                                           default=current_price * 1.02)
                    distance_pct = abs(nearest_resistance - current_price) / current_price * 100
                    
                    if 1 <= distance_pct <= 3:  # Próximo da resistência
                        return 80
                    elif distance_pct <= 5:
                        return 60
                    else:
                        return 40
            
            return 50
            
        except Exception as e:
            print(f"❌ Erro na análise de suporte/resistência: {e}")
            return 50
    
    def _analyze_candlestick_patterns(self, df: pd.DataFrame, signal_type: str) -> float:
        """Analisa padrões de candlestick"""
        try:
            if len(df) < 3:
                return 50
            
            last_candle = df.iloc[-1]
            prev_candle = df.iloc[-2]
            
            open_price = float(last_candle['open'])
            close_price = float(last_candle['close'])
            high_price = float(last_candle['high'])
            low_price = float(last_candle['low'])
            
            body_size = abs(close_price - open_price)
            candle_range = high_price - low_price
            
            if candle_range == 0:
                return 50
            
            score = 50
            
            if signal_type == 'COMPRA':
                # Padrões de alta
                lower_shadow = min(close_price, open_price) - low_price
                
                if close_price > open_price:  # Candle verde
                    score += 10
                
                if lower_shadow > body_size * 1.5:  # Martelo
                    score += 20
                
                if body_size > candle_range * 0.6:  # Corpo forte
                    score += 10
            
            else:  # VENDA
                # Padrões de baixa
                upper_shadow = high_price - max(close_price, open_price)
                
                if close_price < open_price:  # Candle vermelho
                    score += 10
                
                if upper_shadow > body_size * 1.5:  # Estrela cadente
                    score += 20
                
                if body_size > candle_range * 0.6:  # Corpo forte
                    score += 10
            
            return min(100, score)
            
        except Exception as e:
            print(f"❌ Erro na análise de candlestick: {e}")
            return 50
    
    def _analyze_moving_averages(self, df: pd.DataFrame, current_price: float, signal_type: str) -> float:
        """Analisa médias móveis"""
        try:
            if len(df) < 20:
                return 50
            
            # Calcular médias móveis
            ma_10 = df['close'].rolling(window=10).mean().iloc[-1]
            ma_20 = df['close'].rolling(window=20).mean().iloc[-1]
            
            score = 50
            
            if signal_type == 'COMPRA':
                # Para compra, preço deve estar acima das MAs
                if current_price > ma_10:
                    score += 15
                if current_price > ma_20:
                    score += 15
                if ma_10 > ma_20:  # MA10 acima da MA20
                    score += 20
            
            else:  # VENDA
                # Para venda, preço deve estar abaixo das MAs
                if current_price < ma_10:
                    score += 15
                if current_price < ma_20:
                    score += 15
                if ma_10 < ma_20:  # MA10 abaixo da MA20
                    score += 20
            
            return score
            
        except Exception as e:
            print(f"❌ Erro na análise de médias móveis: {e}")
            return 50
    
    def _generate_confirmation_reasons(self, scores: Dict[str, float], action: str) -> List[str]:
        """Gera razões detalhadas para a decisão"""
        reasons = []
        
        # Mapear scores para razões
        if scores['price_breakout'] >= 70:
            reasons.append('PRICE_BREAKOUT_CONFIRMED')
        elif scores['price_breakout'] <= 30:
            reasons.append('PRICE_REVERSAL_DETECTED')
        
        if scores['volume_confirmation'] >= 70:
            reasons.append('VOLUME_INCREASE_CONFIRMED')
        elif scores['volume_confirmation'] <= 30:
            reasons.append('VOLUME_INSUFFICIENT')
        
        if scores['btc_alignment'] >= 70:
            reasons.append('BTC_ALIGNMENT_POSITIVE')
        elif scores['btc_alignment'] <= 30:
            reasons.append('BTC_ALIGNMENT_NEGATIVE')
        
        if scores['momentum_sustainability'] >= 70:
            reasons.append('MOMENTUM_SUSTAINED')
        elif scores['momentum_sustainability'] <= 30:
            reasons.append('MOMENTUM_WEAKENING')
        
        if scores['technical_patterns'] >= 70:
            reasons.append('TECHNICAL_PATTERNS_BULLISH')
        elif scores['technical_patterns'] <= 30:
            reasons.append('TECHNICAL_PATTERNS_BEARISH')
        
        # Se não há razões específicas, adicionar razão geral
        if not reasons:
            if action == 'confirm':
                reasons.append('OVERALL_CONFIRMATION_STRONG')
            elif action == 'reject':
                reasons.append('OVERALL_CONFIRMATION_WEAK')
            else:
                reasons.append('AWAITING_STRONGER_SIGNALS')
        
        return reasons
    
    def _create_confirmation_result(self, action: str, score: float, reasons: List[str], 
                                  detailed_scores: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """Cria resultado estruturado da análise de confirmação"""
        return {
            'action': action,  # 'confirm', 'reject', 'wait', 'error', 'insufficient_data'
            'confidence_score': round(score, 1),
            'reasons': reasons,
            'detailed_scores': detailed_scores or {},
            'timestamp': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'analysis_version': '1.0'
        }
    
    def get_confirmation_thresholds(self) -> Dict[str, Any]:
        """Retorna os thresholds atuais do sistema"""
        return {
            'criteria_weights': ConfirmationCriteria.WEIGHTS,
            'confirmation_thresholds': ConfirmationCriteria.THRESHOLDS,
            'system_config': self.config
        }
    
    def update_confirmation_thresholds(self, new_thresholds: Dict[str, float]) -> bool:
        """Atualiza os thresholds do sistema (para interface admin)"""
        try:
            for key, value in new_thresholds.items():
                if key in ConfirmationCriteria.THRESHOLDS:
                    ConfirmationCriteria.THRESHOLDS[key] = value
            
            print(f"✅ Thresholds atualizados: {new_thresholds}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao atualizar thresholds: {e}")
            return False