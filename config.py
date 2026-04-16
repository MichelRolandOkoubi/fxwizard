import os
from dotenv import load_dotenv

load_dotenv()

# --- Connectivity ---
try:
    MT5_LOGIN = int(os.getenv("MT5_LOGIN", "0"))
except ValueError:
    MT5_LOGIN = 0
    print("Warning: MT5_LOGIN should be an integer. Defaulting to 0.")
MT5_PASSWORD = os.getenv("MT5_PASSWORD", "")
MT5_SERVER = os.getenv("MT5_SERVER", "")

# --- Assets ---
TRADED_ASSETS = ["EURUSD", "GBPJPY", "XAUUSD", "USOIL"]
TIMEFRAMES = {
    "entry": "M15",
    "trend_h1": "H1",
    "trend_d1": "D1"
}

# --- Risk Management ---
RISK_PER_TRADE = 0.01  # 1%
MAX_DRAWDOWN = 0.10   # 10%
ATR_PERIOD = 14
ATR_MULTIPLIER = 2.0  # For trailing stop

# --- Sentiment & News ---
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "")
ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY", "")
SENTIMENT_THRESHOLD = 0.2  # Signal if sentiment score > 0.2 or < -0.2

# --- Telegram Alerts ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# --- Model Paths ---
MODEL_PATH = "models/price_prediction.xgb"
