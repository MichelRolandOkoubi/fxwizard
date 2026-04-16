import pandas as pd
import numpy as np
import vectorbt as vbt
import talib

def generate_synthetic_data(n_bars=1000):
    """Generates synthetic OHLCV data with some trends and cycles."""
    np.random.seed(42)
    time = pd.date_range(start="2023-01-01", periods=n_bars, freq="H")
    
    # Random walk with some trend
    price = 1.05 + np.cumsum(np.random.normal(0, 0.001, n_bars))
    # Add a cycle
    price += 0.01 * np.sin(np.linspace(0, 10 * np.pi, n_bars))
    
    df = pd.DataFrame({
        'open': price,
        'high': price + 0.002,
        'low': price - 0.002,
        'close': price,
        'tick_volume': np.random.randint(100, 1000, n_bars)
    }, index=time)
    return df

def run_simulated_backtest():
    print("Generating synthetic market data...")
    df = generate_synthetic_data(2000)
    
    print("Calculating indicators...")
    close = df['close'].values
    df['RSI'] = talib.RSI(close, timeperiod=14)
    df['SMA_50'] = talib.SMA(close, timeperiod=50)
    df['SMA_200'] = talib.SMA(close, timeperiod=200)
    
    # Strategy Logic:
    # Buy if RSI < 40 and Price > SMA_50
    # Exit if RSI > 70
    entries = (df['RSI'] < 40) & (df['close'] > df['SMA_50'])
    exits = (df['RSI'] > 70)
    
    print("Executing VectorBT simulation...")
    pf = vbt.Portfolio.from_signals(
        df['close'], 
        entries, 
        exits, 
        init_cash=10000, 
        fees=0.0001,
        freq="H"
    )
    
    print("\n--- Backtest Results ---")
    print(pf.stats())
    
    # Save results to a CSV
    result_file = "backtest_results.csv"
    pf.stats().to_csv(result_file)
    print(f"\nResults saved to {result_file}")

if __name__ == "__main__":
    try:
        run_simulated_backtest()
    except Exception as e:
        print(f"Error during simulation: {e}")
        print("Note: Ensure TA-Lib and VectorBT are correctly installed.")
