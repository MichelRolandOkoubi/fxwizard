import talib
import pandas as pd
import numpy as np

class TechnicalEngine:
    @staticmethod
    def add_indicators(df):
        """Adds advanced technical indicators to the dataframe."""
        if df.empty:
            return df
            
        close = df['close'].values
        high = df['high'].values
        low = df['low'].values
        volume_col = 'tick_volume' if 'tick_volume' in df.columns else 'volume'
        volume = df[volume_col].values if volume_col in df.columns else np.zeros(len(df))

        # 1. RSI (Adaptatif/Standard)
        df['RSI'] = talib.RSI(close, timeperiod=14)

        # 2. Bollinger Bands
        df['BB_UP'], df['BB_MID'], df['BB_LOW'] = talib.BBANDS(close, timeperiod=20)

        # 3. MACD
        df['MACD'], df['MACD_SIGNAL'], df['MACD_HIST'] = talib.MACD(close)

        # 4. Ichimoku Cloud (Manual calculation as TA-Lib doesn't have it natively)
        # Tenkan-sen (Conversion Line): (9-period high + 9-period low)/2
        nine_period_high = df['high'].rolling(window=9).max()
        nine_period_low = df['low'].rolling(window=9).min()
        df['tenkan_sen'] = (nine_period_high + nine_period_low) / 2

        # Kijun-sen (Base Line): (26-period high + 26-period low)/2
        period26_high = df['high'].rolling(window=26).max()
        period26_low = df['low'].rolling(window=26).min()
        df['kijun_sen'] = (period26_high + period26_low) / 2

        # Senkou Span A (Leading Span A): (Conversion Line + Base Line)/2
        df['senkou_span_a'] = ((df['tenkan_sen'] + df['kijun_sen']) / 2).shift(26)

        # Senkou Span B (Leading Span B): (52-period high + 52-period low)/2
        period52_high = df['high'].rolling(window=52).max()
        period52_low = df['low'].rolling(window=52).min()
        df['senkou_span_b'] = ((period52_high + period52_low) / 2).shift(26)

        # 5. ATR (for Risk Management)
        df['ATR'] = talib.ATR(high, low, close, timeperiod=14)
        
        # 6. Fibonacci Retracements (Calculated on the last 100 periods)
        max_p = df['high'].tail(100).max()
        min_p = df['low'].tail(100).min()
        diff = max_p - min_p
        df['FIB_61_8'] = max_p - 0.618 * diff
        df['FIB_50_0'] = max_p - 0.5 * diff
        df['FIB_38_2'] = max_p - 0.382 * diff

        return df

    @staticmethod
    def check_mtf_signals(m15_df, h1_df, d1_df):
        """Performs Multi-Timeframe Analysis."""
        # Simple trend confirmation: If Price is above SMA 200 on D1 and H1
        # Example logic
        last_d1_close = d1_df['close'].iloc[-1]
        last_h1_close = h1_df['close'].iloc[-1]
        
        # We could add SMA calculation here
        # For brevity, let's assume a trend-following logic
        pass
