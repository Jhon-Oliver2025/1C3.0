import pandas as pd
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands
from config import server

class TechnicalIndicators:
    def __init__(self):
        self.config = server.config['TRADING']['INDICATORS']

    def calculate_all(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcula todos os indicadores técnicos"""
        close_series = pd.Series(df['close'])
        
        # EMAs
        df['ema_9'] = EMAIndicator(close_series, window=self.config['EMA']['fast']).ema_indicator()
        df['ema_21'] = EMAIndicator(close_series, window=self.config['EMA']['slow']).ema_indicator()
        
        # RSI
        df['rsi'] = RSIIndicator(close_series, window=self.config['RSI']['window']).rsi()
        
        # MACD
        macd = MACD(close_series)
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        
        # Bollinger Bands
        bb = BollingerBands(close_series, window=self.config['BB']['window'])
        df['bb_upper'] = bb.bollinger_hband()
        df['bb_lower'] = bb.bollinger_lband()
        
        return df