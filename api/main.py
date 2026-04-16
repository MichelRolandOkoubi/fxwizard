import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import asyncio
from fastapi import FastAPI, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from src.analysis.sentiment_analyzer import SentimentAnalyzer
from src.analysis.technical_engine import TechnicalEngine
from src.analysis.prediction_model import PredictionModel

app = FastAPI(title="FXWizard API")

# Enable CORS for Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sentiment_engine = SentimentAnalyzer()
tech_engine = TechnicalEngine()
prediction_model = PredictionModel()

class MarketFetcher:
    def _map_symbol(self, symbol):
        mapping = {
            "EURUSD": "EURUSD=X",
            "GBPJPY": "GBPJPY=X",
            "XAUUSD": "GC=F",
            "USOIL": "CL=F",
            "US500": "^GSPC",
            "USTECH": "^IXIC",
        }
        return mapping.get(symbol, symbol)

    def get_candles(self, symbol, resolution="15", days=7):
        mapped_symbol = self._map_symbol(symbol)
        interval_map = {
            "1": "1m",
            "5": "5m",
            "15": "15m",
            "30": "30m",
            "60": "1h",
            "240": "4h",
            "D": "1d",
            "W": "1wk"
        }
        interval = interval_map.get(resolution, "15m")
        period = f"{days}d"
        try:
            ticker = yf.Ticker(mapped_symbol)
            df = ticker.history(period=period, interval=interval)
            if not df.empty:
                df = df.rename(columns={
                    "Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"
                })
                df['time'] = df.index.view(int) // 10**9 # Convert to unix timestamp
                
                # Add technical indicators
                df = tech_engine.add_indicators(df)
                
                # Replace Inf/NaN with None for JSON serialization
                df = df.replace([float('inf'), float('-inf')], 0).fillna(0)
                
                return df.to_dict(orient='records')
            return []
        except Exception as e:
            print(f"Candle error: {e}")
            return []

    def get_quote(self, symbol):
        mapped_symbol = self._map_symbol(symbol)
        try:
            ticker = yf.Ticker(mapped_symbol)
            info = ticker.fast_info
            # Get latest close and previous close for change
            data = ticker.history(period="2d", interval="1d")
            change = 0
            change_pct = 0
            if len(data) >= 2:
                prev_close = data.iloc[-2]['Close']
                current_price = info.last_price
                change = current_price - prev_close
                change_pct = (change / prev_close) * 100
                
            return {
                'symbol': symbol,
                'price': float(info.last_price),
                'change': float(change),
                'change_pct': float(change_pct)
            }
        except Exception as e:
            return {"error": str(e)}

fetcher = MarketFetcher()

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get("/api/candles")
def get_candles(symbol: str = "EURUSD", resolution: str = "15", days: int = 7):
    return fetcher.get_candles(symbol, resolution, days)

@app.get("/api/quote")
def get_quote(symbol: str = "EURUSD"):
    return fetcher.get_quote(symbol)

@app.get("/api/bulk-quotes")
def get_bulk_quotes(symbols: str = "EURUSD,GBPJPY,XAUUSD,USOIL"):
    sym_list = symbols.split(",")
    return {s: fetcher.get_quote(s) for s in sym_list}

@app.get("/api/sentiment")
def get_sentiment(symbol: str = "EURUSD"):
    score = sentiment_engine.get_news_sentiment(symbol)
    trend = "Bullish" if score > 0 else ("Bearish" if score < 0 else "Neutral")
    return {
        "symbol": symbol,
        "score": score,
        "trend": trend
    }

@app.get("/api/backtest")
def get_backtest():
    if os.path.exists("backtest_results.csv"):
        df = pd.read_csv("backtest_results.csv")
        return df.to_dict(orient='records')
    return []

@app.get("/api/technical-signals")
def get_technical_signals(symbol: str = "EURUSD"):
    candles = fetcher.get_candles(symbol, resolution="15", days=1)
    if not candles:
        return {"error": "No data"}
    
    last = candles[-1]
    
    # RSI Status
    rsi = last.get('RSI', 50)
    rsi_status = "Overbought" if rsi > 70 else ("Oversold" if rsi < 30 else "Neutral")
    
    # MACD Status
    macd = last.get('MACD', 0)
    macd_signal = last.get('MACD_SIGNAL', 0)
    macd_trend = "Bullish" if macd > macd_signal else "Bearish"
    
    return {
        "symbol": symbol,
        "rsi": {
            "value": round(float(rsi), 2),
            "status": rsi_status
        },
        "macd": {
            "value": round(float(macd), 4),
            "trend": macd_trend
        },
        "atr": round(float(last.get('ATR', 0)), 5)
    }

@app.get("/api/prediction")
def get_prediction(symbol: str = "EURUSD"):
    # Fetch data to predict on
    data = fetcher.get_candles(symbol, resolution="15", days=5)
    if not data:
        return {"probability": 0.5, "confidence": "Low"}
    
    df = pd.DataFrame(data)
    prob = prediction_model.predict_probability(df)
    
    confidence = "High" if abs(prob - 0.5) > 0.2 else ("Medium" if abs(prob - 0.5) > 0.1 else "Low")
    direction = "BUY" if prob > 0.5 else "SELL"
    
    return {
        "symbol": symbol,
        "probability": round(float(prob) * 100, 1),
        "direction": direction,
        "confidence": confidence
    }

@app.websocket("/ws/{symbol}")
async def websocket_endpoint(websocket: WebSocket, symbol: str):
    await websocket.accept()
    try:
        # Get base quote
        base_quote = fetcher.get_quote(symbol)
        price = base_quote.get("price", 100.0)
        
        while True:
            # Simulate high-frequency noise/movements (0.01% - 0.05%)
            import random
            move = price * random.uniform(-0.0005, 0.0005)
            price += move
            
            data = {
                "symbol": symbol,
                "price": round(price, 5),
                "timestamp": datetime.now().isoformat(),
                "type": "trade"
            }
            await websocket.send_text(json.dumps(data))
            await asyncio.sleep(1) # Stream every second
            
    except WebSocketDisconnect:
        print(f"Client disconnected for {symbol}")
    except Exception as e:
        print(f"WS Error: {e}")
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
