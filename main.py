import time
import pandas as pd
from config import TRADED_ASSETS, TIMEFRAMES
from src.data.data_manager import MT5DataManager
from src.analysis.technical_engine import TechnicalEngine
from src.analysis.sentiment_analyzer import SentimentAnalyzer
from src.analysis.prediction_model import PredictionModel
from src.execution.risk_manager import RiskManager
from src.execution.executor import Executor

def main():
    print("Starting FXWizard Quantitative Trading Bot...")
    
    # Initialize Modules
    data_manager = MT5DataManager()
    technical_engine = TechnicalEngine()
    sentiment_analyzer = SentimentAnalyzer()
    prediction_model = PredictionModel()
    risk_manager = RiskManager()
    executor = Executor()
    
    # Send Startup Notification
    executor.notifier.send_message("🚀 *FXWizard Bot Started!* Monitoring active assets...")

    if not data_manager.connect():
        return

    try:
        while True:
            for symbol in TRADED_ASSETS:
                print(f"\n--- Analyzing {symbol} ---")
                
                # 1. Fetch Data
                df_m15 = data_manager.get_historical_data(symbol, "M15", 500)
                df_h1 = data_manager.get_historical_data(symbol, "H1", 200)
                
                # 2. Add Indicators
                df_m15 = technical_engine.add_indicators(df_m15)
                
                # 3. Sentiment Analysis
                sentiment_score = sentiment_analyzer.get_news_sentiment(symbol)
                print(f"Sentiment Score: {sentiment_score}")
                
                # 4. ML Prediction
                up_prob = prediction_model.predict_probability(df_m15)
                print(f"ML Up-Probability: {up_prob:.2f}")

                # 5. Logic
                latest = df_m15.iloc[-1]
                
                # Signal: ML High Prob + RSI not overbought + Bullish Sentiment
                if up_prob > 0.7 and latest['RSI'] < 70 and sentiment_score > 0.1:
                    print("Signal: STRONG BUY detected.")
                    
                    # Risk Management
                    balance = 10000 # Dummy balance, should fetch from MT5
                    risk_amt = balance * 0.01
                    sl_price = risk_manager.get_atr_stop_loss(latest['close'], latest['ATR'], "long")
                    sl_pips = abs(latest['close'] - sl_price) * 10000
                    
                    vol = risk_manager.calculate_position_size(balance, risk_amt, sl_pips)
                    
                    # Execute
                    executor.place_order(symbol, vol, "long", stop_loss=sl_price)

                elif up_prob < 0.3 and latest['RSI'] > 30 and sentiment_score < -0.1:
                    print("Signal: STRONG SELL detected.")
                    sl_price = risk_manager.get_atr_stop_loss(latest['close'], latest['ATR'], "short")
                    # ... Position sizing and Execution
                    
                else:
                    print("No clear signal. Monitoring...")

            # Wait for next candle or interval
            time.sleep(60)
            
    except KeyboardInterrupt:
        print("Bot stopped.")
    finally:
        data_manager.disconnect()

if __name__ == "__main__":
    main()
