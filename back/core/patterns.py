import pandas as pd

class PricePatterns:
    @staticmethod
    def check_engulfing(df: pd.DataFrame, signal_type: str) -> bool:
        if signal_type == "LONG":
            return (df['close'].iloc[-1] > df['open'].iloc[-2] and 
                    df['open'].iloc[-1] < df['open'].iloc[-2] and 
                    df['close'].iloc[-1] > df['close'].iloc[-2])
        return (df['close'].iloc[-1] < df['open'].iloc[-2] and 
                df['open'].iloc[-1] > df['open'].iloc[-2] and 
                df['close'].iloc[-1] < df['close'].iloc[-2])

    @staticmethod
    def check_candlestick_pattern(df: pd.DataFrame, signal_type: str) -> float:
        score = 0
        body = abs(df['close'].iloc[-1] - df['open'].iloc[-1])
        upper_shadow = df['high'].iloc[-1] - max(df['open'].iloc[-1], df['close'].iloc[-1])
        lower_shadow = min(df['open'].iloc[-1], df['close'].iloc[-1]) - df['low'].iloc[-1]
        
        # Implementar padrões específicos aqui
        return score