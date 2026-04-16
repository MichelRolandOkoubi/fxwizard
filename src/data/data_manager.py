import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime
import time
from config import MT5_LOGIN, MT5_PASSWORD, MT5_SERVER

class MT5DataManager:
    def __init__(self):
        self.connected = False

    def connect(self):
        """Connects to the MetaTrader 5 terminal."""
        if not mt5.initialize(login=MT5_LOGIN, password=MT5_PASSWORD, server=MT5_SERVER):
            print(f"MT5 initialization failed, error code: {mt5.last_error()}")
            return False
        
        # Check if login is successful
        authorized = mt5.login(MT5_LOGIN, password=MT5_PASSWORD, server=MT5_SERVER)
        if not authorized:
            print(f"Failed to connect to account #{MT5_LOGIN}, error code: {mt5.last_error()}")
            return False
            
        print(f"Connected to MT5: {MT5_SERVER}")
        self.connected = True
        return True

    def get_historical_data(self, symbol, timeframe, n_bars=1000):
        """Fetches historical candles for a specific symbol and timeframe."""
        if not self.connected:
            self.connect()

        # Map string timeframe to MT5 constant
        tf_map = {
            "M1": mt5.TIMEFRAME_M1,
            "M5": mt5.TIMEFRAME_M5,
            "M15": mt5.TIMEFRAME_M15,
            "M30": mt5.TIMEFRAME_M30,
            "H1": mt5.TIMEFRAME_H1,
            "H4": mt5.TIMEFRAME_H4,
            "D1": mt5.TIMEFRAME_D1
        }
        
        mt5_tf = tf_map.get(timeframe, mt5.TIMEFRAME_H1)
        
        rates = mt5.copy_rates_from_pos(symbol, mt5_tf, 0, n_bars)
        if rates is None:
            print(f"Failed to get rates for {symbol}, error: {mt5.last_error()}")
            return pd.DataFrame()

        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)
        return df

    def get_realtime_tick(self, symbol):
        """Fetches the latest tick for a symbol."""
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            return None
        return tick._asdict()

    def disconnect(self):
        mt5.shutdown()
        self.connected = False
