from src.data.data_manager import MT5DataManager
from src.analysis.technical_engine import TechnicalEngine
from src.analysis.prediction_model import PredictionModel
from config import TRADED_ASSETS

def train_on_historical_data():
    print("Initializing Training Pipeline...")
    data_manager = MT5DataManager()
    technical_engine = TechnicalEngine()
    predictor = PredictionModel()

    if not data_manager.connect():
        print("Failed to connect to MT5 for training data.")
        return

    try:
        # We will train on the primary asset (e.g., EURUSD)
        symbol = "EURUSD"
        print(f"Fetching 5000 bars of H1 data for {symbol}...")
        
        df = data_manager.get_historical_data(symbol, "H1", 5000)
        if df.empty:
            print("No data fetched.")
            return
            
        print("Calculating indicators for training...")
        df = technical_engine.add_indicators(df)
        
        print(f"Training XGBoost model on {len(df)} records...")
        predictor.train(df)
        
        print("Model training completed and saved to config.MODEL_PATH")
        
    finally:
        data_manager.disconnect()

if __name__ == "__main__":
    train_on_historical_data()
