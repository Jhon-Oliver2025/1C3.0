import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Any
from binance.client import Client # Alterado de binance.um_futures para binance.client
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange
# Importar 'server' do config para acessar as chaves da API
from config import server
import requests
import time
import traceback
from .database import Database
from colorama import Fore, Style, init # Adicionar 'init' aqui
from .gerenciar_sinais import GerenciadorSinais # Importar GerenciadorSinais

# Initialize colorama
init()

class TechnicalAnalysis:
    def __init__(self, db_instance: Database):
        print("📊 Inicializando TechnicalAnalysis...")
        self.db = db_instance
        # --- Início da Edição ---
        # Obter API Key e Secret do config
        api_key = server.config.get('API_KEY')
        api_secret = server.config.get('API_SECRET')

        # Inicializar o cliente Binance com as chaves
        if not api_key or not api_secret:
            print(f"{Fore.RED}❌ ERRO: Chaves da API da Binance não encontradas no config.py!{Style.RESET_ALL}")
            # Inicializa o cliente sem chaves, mas endpoints privados falharão
            self.client = Client() # Alterado de UMFutures() para Client()
        else:
            self.client = Client(api_key, api_secret) # Alterado de UMFutures(api_key, api_secret) para Client(api_key, api_secret)
            print(f"{Fore.GREEN}✅ Cliente Binance inicializado com chaves.{Style.RESET_ALL}")
        # --- Fim da Edição ---

        # Inicializar GerenciadorSinais aqui, passando a instância do banco de dados
        self.gerenciador_sinais = GerenciadorSinais(self.db)
        # Inicializar variáveis para controle de atualização de pares
        self.pairs_last_update = 0 # Inicializa para 0 para forçar a primeira atualização
        self.update_interval = 4 * 3600 # Intervalo de atualização em segundos (ex: 4 horas)
        # Inicializar timeframes e mínimos
        self.trend_timeframe = '4h' # Timeframe para análise de tendência
        self.entry_timeframe = '1h' # Timeframe para análise de entrada
        # --- Início da Edição ---
        self.quality_score_minimum = 90 # Score mínimo para gerar um sinal (Alterado para 90)
        # --- Fim da Edição ---
        self.min_volume = 100000 # Volume mínimo em USDT para considerar um par
        # Inicializar a lista de pares futuros
        self.futures_pairs = [] # <-- Adicione esta linha
        print("✅ TechnicalAnalysis inicializado.")

    def load_active_signals(self):
        """Carrega sinais ativos do arquivo"""
        try:
            import os
            import json
            
            file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'active_signals.json')
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    self.active_signals = data
                print(f"✅ {len(self.active_signals)} sinais ativos carregados")
            else:
                self.active_signals = {}
                print("📝 Nenhum arquivo de sinais ativos encontrado. Iniciando com lista vazia.")
        except Exception as e:
            print(f"❌ Erro ao carregar sinais ativos: {e}")
            self.active_signals = {}

    def save_active_signals(self):
        """Salva sinais ativos em arquivo"""
        try:
            import os
            import json
            
            # Garantir que o diretório existe
            data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
            os.makedirs(data_dir, exist_ok=True)
            
            file_path = os.path.join(data_dir, 'active_signals.json')
            with open(file_path, 'w') as f:
                json.dump(self.active_signals, f, indent=4)
            return True
        except Exception as e:
            print(f"❌ Erro ao salvar sinais ativos: {e}")
            return False

    def get_klines(self, symbol: str, interval: str, limit: int = 500) -> Optional[pd.DataFrame]:
        try:
            # Adicionar um pequeno delay para evitar atingir limites de API
            time.sleep(0.1)
            
            # Adicionar timeout para evitar que a requisição fique presa
            # Alterado de self.client.klines para self.client.futures_klines para compatibilidade com python-binance para futuros
            klines = self.client.futures_klines(symbol=symbol, interval=interval, limit=limit) 
            colunas = ['timestamp', 'open', 'high', 'low', 'close', 'volume',
                       'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                       'taker_buy_quote', 'ignore']
            
            df = pd.DataFrame(data=klines)
            df.columns = colunas
            
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = df[col].astype(float)
            return df
            
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}⚠️ Operação interrompida pelo usuário{Style.RESET_ALL}")
            raise
        except Exception as e:
            print(f"❌ Erro ao obter klines para {symbol}: {e}")
            return None

    def analyze_trend(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analisa tendência no timeframe maior (4h)"""
        try:
            close = pd.Series(df['close'].values)
            ema20 = EMAIndicator(close=close, window=20).ema_indicator()
            ema50 = EMAIndicator(close=close, window=50).ema_indicator()
            ema200 = EMAIndicator(close=close, window=200).ema_indicator()
            
            current_price = float(df['close'].iloc[-1])
            ema20_val = float(ema20.iloc[-1])
            ema50_val = float(ema50.iloc[-1])
            ema200_val = float(ema200.iloc[-1])
            
            # Verificar inclinação das EMAs
            ema20_slope = (ema20.iloc[-1] - ema20.iloc[-5]) / ema20.iloc[-5] * 100
            ema50_slope = (ema50.iloc[-1] - ema50.iloc[-5]) / ema50.iloc[-5] * 100
            
            trend_strength = 0
            
            # Relaxar condições de tendência
            if current_price > ema20_val and ema20_slope > 0:
                trend_strength = 2
            elif current_price < ema20_val and ema20_slope < 0:
                trend_strength = -2
            else:
                trend_strength = 0
                
            return {
                'trend_strength': trend_strength,
                'is_uptrend': trend_strength > 0,
                'description': 'Alta' if trend_strength > 0 else 'Baixa',
                'ema_alignment': trend_strength != 0,
                'ema20_slope': ema20_slope,
                'ema50_slope': ema50_slope
            }
            
        except Exception as e:
            print(f"❌ Erro ao analisar tendência: {e}")
            return {'trend_strength': 0, 'is_uptrend': False, 'description': 'Erro'}

    def check_pullback(self, df: pd.DataFrame, is_uptrend: bool) -> Dict[str, Any]:
        """Verifica pullback no timeframe menor (1h)"""
        try:
            close = pd.Series(df['close'].values)
            ema8 = EMAIndicator(close=close, window=8).ema_indicator()
            ema21 = EMAIndicator(close=close, window=21).ema_indicator()
            rsi = RSIIndicator(close=close, window=14).rsi()
            
            current_price = float(df['close'].iloc[-1])
            ema8_val = float(ema8.iloc[-1])
            ema21_val = float(ema21.iloc[-1])
            rsi_val = float(rsi.iloc[-1])
            
            # Verificar direção do preço recente
            price_direction = df['close'].iloc[-3:].pct_change().mean()
            
            if is_uptrend:
                pullback_valid = (
                    current_price > ema21_val and      
                    current_price < ema8_val and       
                    35 < rsi_val < 65 and             
                    price_direction < 0                
                )
            else:
                pullback_valid = (
                    current_price < ema21_val and      
                    current_price > ema8_val and       
                    35 < rsi_val < 65 and             
                    price_direction > 0                
                )
                
            return {
                'valid': pullback_valid,
                'description': f"Pullback em tendência de {'alta' if is_uptrend else 'baixa'}",
                'strength': 2 if (is_uptrend and rsi_val > 45) or (not is_uptrend and rsi_val < 55) else 1,
                'rsi': rsi_val,
                'price_action': price_direction
            }
            
        except Exception as e:
            print(f"❌ Erro ao verificar pullback: {e}")
            return {'valid': False, 'description': 'Erro', 'strength': 0}

    def check_breakout(self, df: pd.DataFrame, is_uptrend: bool) -> Dict[str, Any]:
        """Verifica breakout de consolidação no timeframe de entrada"""
        try:
            # Pegar últimas 20 velas para análise de consolidação
            recent_df = df.iloc[-20:]
            
            # Calcular bandas de Bollinger para identificar consolidação
            from ta.volatility import BollingerBands
            bollinger = BollingerBands(close=pd.Series(recent_df['close']), window=20, window_dev=2)
            
            # Largura das bandas (indicador de consolidação)
            bb_width = (bollinger.bollinger_hband() - bollinger.bollinger_lband()) / bollinger.bollinger_mavg()
            
            # Verificar se houve consolidação recente (bandas estreitas) seguida de expansão
            was_consolidating = bb_width.iloc[-5:-2].mean() < 0.05
            is_expanding = bb_width.iloc[-1] > bb_width.iloc[-3] * 1.3
            
            # Verificar volume crescente (confirmação de breakout)
            volume_increasing = df['volume'].iloc[-1] > df['volume'].iloc[-5:-1].mean() * 1.5
            
            # Verificar direção do breakout
            price_direction = df['close'].iloc[-3:].pct_change().mean()
            
            if is_uptrend:
                # Breakout de alta
                breakout_valid = (
                    was_consolidating and
                    is_expanding and
                    price_direction > 0.005 and
                    volume_increasing and
                    df['close'].iloc[-1] > df['high'].iloc[-5:-1].max()
                )
            else:
                # Breakout de baixa
                breakout_valid = (
                    was_consolidating and
                    is_expanding and
                    price_direction < -0.005 and
                    volume_increasing and
                    df['close'].iloc[-1] < df['low'].iloc[-5:-1].min()
                )
                
            return {
                'valid': breakout_valid,
                'description': f"Breakout de {'alta' if is_uptrend else 'baixa'} após consolidação",
                'strength': 2 if volume_increasing else 1,
                'price_action': price_direction
            }
            
        except Exception as e:
            print(f"❌ Erro ao verificar breakout: {e}")
            return {'valid': False, 'description': 'Erro', 'strength': 0}

    def analyze_symbol(self, symbol: str) -> Optional[Dict]:
        try:
            print(f"\nIniciando análise de {symbol}")

            # Análise de tendência em 4h
            trend_df = self.get_klines(symbol, self.trend_timeframe)
            if trend_df is None or len(trend_df) < 50:
                return None

            # Obter dados do timeframe de entrada
            entry_df = self.get_klines(symbol, self.entry_timeframe)
            if entry_df is None or len(entry_df) < 50:
                return None

            print(f"\nAnalisando {symbol}:")

            # Análise de tendência
            trend = self.analyze_trend(trend_df)
            if trend['trend_strength'] == 0:
                print(f"❌ {symbol}: Sem tendência definida")
                return None

            # Calcular scores
            trend_score = abs(trend['trend_strength']) * 10
            alignment_score = self.check_timeframe_alignment(trend_df, entry_df)
            market_score = self.calculate_market_conditions(entry_df)
            quality_score = trend_score + alignment_score + market_score

            # Verificar se o quality_score atinge o mínimo configurado
            if quality_score < self.quality_score_minimum:
                print(f"❌ {symbol}: Score baixo ({quality_score:.1f}) - Mínimo: {self.quality_score_minimum}") # Adicionado .1f para formatar
                return None
            # --- Fim da Edição ---

            # Calcular preços e tempos
            entry_price = float(entry_df['close'].iloc[-1])
            entry_time = datetime.now()

            # Calcular ATR para definir o alvo
            atr_value = AverageTrueRange(
                high=pd.Series(entry_df['high'].values),
                low=pd.Series(entry_df['low'].values),
                close=pd.Series(entry_df['close'].values),
                window=14 # Usar a mesma janela que em calculate_volatility
            ).average_true_range().iloc[-1]

            # Definir multiplicador do ATR para o alvo (ex: 2 * ATR)
            atr_multiplier = 2.0
            target_distance = atr_value * atr_multiplier

            # Calcular preço alvo baseado no tipo de sinal e ATR
            if trend['is_uptrend']: # Sinal LONG
                target_price = entry_price + target_distance
            else: # Sinal SHORT
                target_price = entry_price - target_distance

            # --- Início da Edição ---
            # Calcular a variação percentual do alvo
            if entry_price != 0: # Evitar divisão por zero
                target_variation = ((target_price - entry_price) / entry_price) * 100
                # Para sinais SHORT, a variação é negativa, queremos o valor absoluto
                if not trend['is_uptrend']:
                    target_variation = abs(target_variation)
            else:
                target_variation = 0 # Se entry_price for zero, variação é zero

            # Definir o mínimo de variação percentual desejado
            min_target_percentage = 6.0 # Alterado de 4.0 para 6.0

            # Verificar se a variação do alvo atinge o mínimo
            if target_variation < min_target_percentage:
                print(f"❌ {symbol}: Variação do alvo ({target_variation:.2f}%) abaixo do mínimo ({min_target_percentage}%)")
                return None
            # --- Fim da Edição ---

            # Gerar sinal com todos os campos necessários
            signal = {
                'symbol': symbol,
                'type': 'LONG' if trend['is_uptrend'] else 'SHORT',
                'entry_price': round(entry_price, 8),
                'entry_time': entry_time.strftime('%Y-%m-%d %H:%M:%S'),
                'target_price': round(target_price, 8),
                'target_exit_time': (entry_time + timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S'),
                'status': 'OPEN',
                'exit_price': '',
                'variation': '',
                'result': '',
                'quality_score': int(quality_score),
                'signal_class': self._get_signal_class(quality_score),
                'trend_score': int(trend_score),
                'alignment_score': int(alignment_score),
                'market_score': int(market_score),
                'strategy_info': trend['description'],
                'trend_timeframe': self.trend_timeframe,
                'entry_timeframe': self.entry_timeframe
            }

            print(f"Sinal gerado: {signal}")
            return signal

        except Exception as e:
            print(f"❌ Erro detalhado na análise de {symbol}: {str(e)}")
            traceback.print_exc()
            return None

    def _get_signal_class(self, quality_score: float) -> str:
        """Retorna a classificação do sinal baseado no quality_score"""
        # --- Início da Edição ---
        # Simplificado para Sinais Premium se o score for >= 90
        if quality_score >= 90:
            return "Sinais Premium"
        else:
            # Esta parte não deve ser alcançada se o filtro quality_score_minimum estiver ativo
            return "❌ Score Insuficiente"
        # --- Fim da Edição ---

    def check_timeframe_alignment(self, trend_df: pd.DataFrame, entry_df: pd.DataFrame) -> int:
        """Verifica alinhamento entre TF4h e TF1h"""
        try:
            trend_direction = trend_df['close'].iloc[-1] > trend_df['close'].iloc[-5]
            entry_direction = entry_df['close'].iloc[-1] > entry_df['close'].iloc[-5]
            
            if trend_direction == entry_direction:
                return 30  # Timeframes alinhados
            return 0
        except Exception as e:
            print(f"❌ Erro ao verificar alinhamento: {e}")
            return 0

    def calculate_market_conditions(self, df: pd.DataFrame) -> int:
        """Calcula score baseado em volume e volatilidade"""
        try:
            # Volume score (0-25 pontos)
            volume = df['volume'].iloc[-1] * df['close'].iloc[-1]
            volume_score = min(25, (volume / self.min_volume) * 25)
            
            # Volatilidade score (0-25 pontos)
            volatility = self.calculate_volatility(df)
            volatility_score = 25 if 3.0 <= volatility <= 6.0 else (
                15 if 2.0 <= volatility <= 7.0 else (
                5 if 1.0 <= volatility <= 8.0 else 0
                ))
            
            return int(volume_score + volatility_score)
        except Exception as e:
            print(f"❌ Erro ao calcular condições de mercado: {e}")
            return 0

    def calculate_volatility(self, df: pd.DataFrame) -> float:
        try:
            atr = AverageTrueRange(
                high=pd.Series(df['high'].values),
                low=pd.Series(df['low'].values),
                close=pd.Series(df['close'].values),
                window=14
            ).average_true_range().iloc[-1]
            
            return (atr / df['close'].iloc[-1]) * 100
        except Exception as e:
            print(f"❌ Erro ao calcular volatilidade: {e}")
            return 0.0

    def calculate_quality_score(self, trend: Dict, strategy_data: Dict, volatility: float) -> int:
        try:
            score = 50
            
            # Pontuação por força da tendência (0-30 pontos)
            trend_points = abs(trend['trend_strength']) * 12
            score += min(30, trend_points)
            
            # Pontuação pela estratégia (0-30 pontos)
            if 'strength' in strategy_data:
                score += strategy_data['strength'] * 12
            
            # Pontuação por volatilidade (0-30 pontos)
            if 3.0 <= volatility <= 6.0:
                score += 30
            elif 2.0 <= volatility <= 7.0:
                score += 20
            elif 1.0 <= volatility <= 8.0:
                score += 10
            
            return min(100, max(0, score))
        except Exception as e:
            print(f"❌ Erro ao calcular pontuação: {e}")
            return 0

    def scan_market(self, verbose: bool = True) -> List[Dict[str, Any]]:
        signals = []
        try:
            if verbose:
                print("\n📡 Iniciando scan de mercado...")
            
            # Verificar atualização dos pares
            current_time = time.time()
            if current_time - self.pairs_last_update > self.update_interval:
                self.select_top_pairs()
                self.pairs_last_update = current_time
            
            # Obter gerenciador de sinais
            gerenciador = self.gerenciador_sinais

            # Analisar pares
            for idx, symbol in enumerate(self.top_pairs):
                try:
                    signal = self.analyze_symbol(symbol)
                    if signal:
                        if gerenciador.save_signal(signal):
                            signals.append(signal)
                            print(f"✅ Sinal encontrado: {symbol}")
                        else:
                            print(f"❌ Erro ao salvar sinal: {symbol}")
                except Exception as e:
                    print(f"❌ Erro ao analisar {symbol}: {e}")
                    continue

            if verbose:        
                print(f"\n✨ {len(signals)} sinais encontrados")
            return signals
            
        except Exception as e:
            if verbose:
                print(f"❌ Erro no scan: {e}")
                traceback.print_exc()
            return signals

    def update_futures_pairs(self):
        """Atualiza a lista de pares futuros"""
        try:
            print("\n🔄 Atualizando lista de pares...")
            # Alterado de self.client.exchange_info() para self.client.futures_exchange_info()
            exchange_info = self.client.futures_exchange_info() 
            
            # Obter informações de alavancagem
            # Alterado de self.client.leverage_bracket() para self.client.futures_leverage_bracket()
            leverage_info = self.client.futures_leverage_bracket() 
            leverage_map = {item['symbol']: item['brackets'][0]['initialLeverage'] for item in leverage_info}

            # Filtrar pares com base no status, tipo de contrato, quoteAsset e alavancagem mínima
            self.futures_pairs = [
                s['symbol'] for s in exchange_info['symbols']
                if s['status'] == 'TRADING' and
                s['contractType'] == 'PERPETUAL' and
                s['quoteAsset'] == 'USDT' and
                leverage_map.get(s['symbol'], 0) >= 50 # Verificar alavancagem mínima de 50x
            ]
            print(f"✅ {len(self.futures_pairs)} pares atualizados (>= 50x alavancagem)")
            return True
        except Exception as e:
            print(f"❌ Erro ao atualizar pares: {e}")
            self.futures_pairs = []
            return False

    def get_24h_volume(self, symbol: str) -> float:
        """Retorna o volume em USDT das últimas 24h"""
        try:
            # Alterado de self.client.futures_ticker_24hr para self.client.futures_symbol_ticker
            ticker = self.client.futures_symbol_ticker(symbol=symbol) 
            return float(ticker['quoteVolume'])
        except Exception as e:
            print(f"❌ Erro ao obter volume de {symbol}: {e}")
            return 0

    def check_divergence(self, df: pd.DataFrame, trend: Dict) -> Dict[str, Any]:
        """Check for RSI divergence"""
        try:
            if len(df) < 14:
                return {'valid': False, 'description': 'Insufficient data'}
            
            # Convert df['close'] to Series explicitly to satisfy type checker
            close_series = pd.Series(df['close'].values)
            rsi = RSIIndicator(close=close_series).rsi()
            is_valid = False
            description = ''
            
            if trend['is_uptrend']:
                is_valid = rsi.iloc[-1] < 30
                description = 'Bullish RSI divergence'
            else:
                is_valid = rsi.iloc[-1] > 70
                description = 'Bearish RSI divergence'
                
            return {
                'valid': is_valid,
                'description': description,
                'strength': 2 if is_valid else 0
            }
        except Exception as e:
            print(f"❌ Erro ao verificar divergência: {e}")
            return {'valid': False, 'description': 'Error', 'strength': 0}

    def check_fibonacci_levels(self, df: pd.DataFrame, trend: Dict) -> Dict[str, Any]:
        """Check Fibonacci retracement levels"""
        try:
            if len(df) < 20:
                return {'valid': False, 'description': 'Insufficient data'}
            
            high = df['high'].max()
            low = df['low'].min()
            current = df['close'].iloc[-1]
            
            fib_levels = [0.236, 0.382, 0.5, 0.618, 0.786]
            is_valid = False
            
            if trend['is_uptrend']:
                retracement = high - (high - low) * np.array(fib_levels)
                is_valid = any(abs(current - level) / current < 0.01 for level in retracement)
                description = 'Bullish Fibonacci support'
            else:
                retracement = low + (high - low) * np.array(fib_levels)
                is_valid = any(abs(current - level) / current < 0.01 for level in retracement)
                description = 'Bearish Fibonacci resistance'
                
            return {
                'valid': is_valid,
                'description': description,
                'strength': 2 if is_valid else 0
            }
        except Exception as e:
            print(f"❌ Erro ao verificar níveis de Fibonacci: {e}")
            return {'valid': False, 'description': 'Error', 'strength': 0}

    def analyze_market(self) -> List[Dict[str, Any]]:
        """Analyze market and return signals"""
        signals = []
        try:
            for symbol in self.top_pairs:
                signal = self.analyze_symbol(symbol)
                if signal:
                    signals.append(signal)
            return signals
        except Exception as e:
            print(f"❌ Erro na análise de mercado: {e}")
            return signals

    def select_top_pairs(self):
        """Seleciona os melhores pares com base em volume e volatilidade"""
        try:
            print("\n🔍 Selecionando os melhores pares...")
            
            # Verificar se já temos pares carregados
            if not self.futures_pairs:
                self.update_futures_pairs()
            
            pairs_data = []
            total_pairs = len(self.futures_pairs)
            
            for i, symbol in enumerate(self.futures_pairs):
                try:
                    print(f"\r🔄 Analisando {symbol}... ({i+1}/{total_pairs})", end="")
                    
                    # Adicionar um pequeno delay para evitar atingir limites de API
                    time.sleep(0.1)
                    
                    df = self.get_klines(symbol, self.entry_timeframe, limit=100)
                    if df is None or len(df) < 20:
                        continue
                        
                    # Calcular volume médio diário (em USD)
                    avg_volume = df['volume'].mean() * df['close'].mean()
                    
                    # Calcular volatilidade (ATR como % do preço)
                    atr = AverageTrueRange(
                        high=pd.Series(df['high'].values),
                        low=pd.Series(df['low'].values),
                        close=pd.Series(df['close'].values),
                        window=14
                    ).average_true_range()
                    
                    volatility = (atr.iloc[-1] / df['close'].iloc[-1]) * 100
                    
                    # Calcular score (combinação de volume e volatilidade)
                    volume_score = min(avg_volume / 1000000, 10)
                    volatility_score = min(volatility, 10)
                    
                    # Score final (50% volume, 50% volatilidade)
                    final_score = (volume_score * 0.5 + volatility_score * 0.5) * 10
                    
                    pairs_data.append({
                        'symbol': symbol,
                        'volume': avg_volume,
                        'volatility': volatility,
                        'score': final_score
                    })
                    
                except KeyboardInterrupt:
                    print(f"\n{Fore.YELLOW}⚠️ Seleção de pares interrompida pelo usuário{Style.RESET_ALL}")
                    raise
                except Exception as e:
                    continue
            
            # Ordenar por score e selecionar os melhores
            pairs_df = pd.DataFrame(pairs_data)
            if len(pairs_df) > 0:
                # --- Início da Edição ---
                # Selecionar os 100 melhores pares
                pairs_df = pairs_df.sort_values('score', ascending=False).head(100)
                # --- Fim da Edição ---
                self.top_pairs = pairs_df['symbol'].tolist()
                
                # Exibir os pares selecionados
                print("\n\n✅ Top pares selecionados:")
                for i, row in enumerate(pairs_df.iterrows()):
                    idx, data = row
                    print(f"{i+1}. {data['symbol']} - Volume: ${data['volume']:,.0f} - Volatilidade: {data['volatility']:.2f}% - Score: {data['score']:.1f}")
            else:
                print("\n⚠️ Não foi possível selecionar pares. Usando lista padrão.")
                self.top_pairs = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT']
                
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}⚠️ Seleção de pares interrompida pelo usuário{Style.RESET_ALL}")
            self.top_pairs = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT']
        except Exception as e:
            print(f"\n❌ Erro ao selecionar pares: {e}")
            self.top_pairs = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT']