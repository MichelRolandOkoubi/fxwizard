import vectorbt as vbt
import pandas as pd
from src.data.data_manager import MT5DataManager
from src.analysis.technical_engine import TechnicalEngine

def run_backtest(symbol="EURUSD"):
    print(f"Running Backtest for {symbol}...")
    
    # 1. Load Data
    data_manager = MT5DataManager()
    df = data_manager.get_historical_data(symbol, "H1", 2000)
    
    # 2. Add Indicators
    df = TechnicalEngine.add_indicators(df)
    
    # 3. Define Strategy Signals
    # Buy when RSI < 30 and price crosses above SMA (simplified example)
    entries = (df['RSI'] < 30) & (df['close'] > df['BB_LOW'])
    exits = (df['RSI'] > 70) 
    
    # 4. Run VectorBT Portfolio
    pf = vbt.Portfolio.from_signals(df['close'], entries, exits, init_cash=10000, fees=0.0001)
    
    print(pf.stats())
    # pf.plot().show() # Requires GUI or Jupyter

if __name__ == "__main__":
    run_backtest()
