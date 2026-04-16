import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import requests
import time
from config import FINNHUB_API_KEY, ALPHA_VANTAGE_KEY
from src.analysis.sentiment_analyzer import SentimentAnalyzer

# Initialize Sentiment Analyzer
sentiment_engine = SentimentAnalyzer()

import yfinance as yf

# Unified Data Fetcher (Yahoo Finance Priority)
class MarketFetcher:
    def __init__(self):
        # YFinance doesn't require API keys
        pass

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

    @st.cache_data(ttl=60)
    def get_candles(_self, symbol, resolution="15", days=7):
        mapped_symbol = _self._map_symbol(symbol)
        interval = "15m" if resolution == "15" else ("1m" if resolution == "1" else "1d")
        period = f"{days}d"
        try:
            ticker = yf.Ticker(mapped_symbol)
            df = ticker.history(period=period, interval=interval)
            if not df.empty:
                df = df.rename(columns={
                    "Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"
                })
                df['time'] = df.index
                return df
            return None
        except Exception:
            return None

    @st.cache_data(ttl=15)
    def get_bulk_quotes(_self, symbols):
        mapped_symbols = [_self._map_symbol(s) for s in symbols]
        try:
            # yfinance allows fetching multiple tickers at once
            data = yf.download(mapped_symbols, period="1d", interval="1m", group_by='ticker', progress=False)
            quotes = {}
            for i, s in enumerate(symbols):
                m_s = mapped_symbols[i]
                if m_s in data:
                    s_data = data[m_s]
                else:
                    s_data = data # if only one ticker, it's not grouped by ticker sometimes
                
                if not s_data.empty:
                    latest = s_data.iloc[-1]
                    prev_close = s_data.iloc[0]['Open'] # Crude way to estimate change
                    price = latest['Close']
                    change = price - prev_close
                    change_pct = (change / prev_close) * 100
                    quotes[s] = {
                        'c': float(price),
                        'd': float(change),
                        'dp': float(change_pct)
                    }
            return quotes
        except Exception:
            return {}

    @st.cache_data(ttl=15)
    def get_quote(_self, symbol):
        # Specific fast quote for single asset
        mapped_symbol = _self._map_symbol(symbol)
        try:
            ticker = yf.Ticker(mapped_symbol)
            # Use fast_info if available (it is in newer yfinance)
            info = ticker.fast_info
            return {
                'c': float(info.last_price),
                'd': 0.0, # fast_info doesn't easily give change
                'dp': 0.0 # but we'll prioritize candles for trend
            }
        except Exception:
            # Fallback to bulk logic if fast_info fails
            qs = _self.get_bulk_quotes([symbol])
            return qs.get(symbol)

fetcher = MarketFetcher()

# Page Config
st.set_page_config(
    page_title="FXWizard Pro Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for Premium Look
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stMetric {
        background-color: #1e2130;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .chart-container {
        background-color: #1e2130;
        padding: 20px;
        border-radius: 15px;
    }
</style>
""", unsafe_allow_html=True)

# Helper for Loading Data
def load_backtest_data():
    if os.path.exists("backtest_results.csv"):
        return pd.read_csv("backtest_results.csv")
    return None

# Sidebar
with st.sidebar:
    st.title("FXWizard Pro")
    st.image("https://img.freepik.com/free-vector/gradient-stock-market-concept_23-2149166910.jpg?w=800", use_container_width=True)
    st.markdown("---")
    
    st.write("### ⚙️ Feed Settings")
    resolution = st.selectbox("Chart Resolution", ["1", "5", "15", "60", "D"], index=2)
    days_to_show = st.slider("Days to show", 1, 30, 7)
    
    if st.button("🔄 Force Refresh Data"):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")
    st.write("### Account Status")
    st.metric("Balance", "$10,000", "+$0.00")
    st.metric("Equity", "$10,000", "0%")
    st.markdown("---")
    st.status("Bot Status: **IDLE**", state="complete")
    if st.button("🚀 Start Trading Bot"):
        st.toast("Bot Starting...", icon="✅")

# Main Dashboard
st.title("📊 Quantitative Trading Intelligence")

# Asset Selection
assets_forex = ["EURUSD", "GBPJPY"]
assets_commodities_indices = ["XAUUSD", "USOIL", "US500", "USTECH"]
assets_stocks = ["AAPL", "COST", "MSFT"]
all_assets = assets_forex + assets_commodities_indices + assets_stocks

selected_asset = st.selectbox("🎯 Select Asset for Analysis", all_assets)

# Fetch Quote for KPIs
quote = fetcher.get_quote(selected_asset)
current_price = quote.get('c') if quote else None
price_change = quote.get('d') if quote else 0
price_change_pct = quote.get('dp') if quote else 0

# Ensure numeric types for formatting
current_price = float(current_price) if current_price is not None else None
price_change = float(price_change) if price_change is not None else 0.0
price_change_pct = float(price_change_pct) if price_change_pct is not None else 0.0

# KPIs Row
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    price_display = f"${current_price:,.2f}" if current_price is not None else "N/A"
    change_display = f"{price_change:+.2f} ({price_change_pct:+.2f}%)" if current_price is not None else "N/A"
    st.metric(f"{selected_asset} Price", price_display, change_display)
with kpi2:
    st.metric("Sharpe Ratio", "N/A", delta_color="inverse")
with kpi3:
    st.metric("Max Drawdown", "0.0%", delta_color="inverse")
with kpi4:
    st.metric("Win Rate", "N/A", delta_color="normal")

# Charts and Sentiment Row
col_main, col_sentiment = st.columns([3, 1])

with col_main:
    st.subheader(f"📈 Real-Time Chart: {selected_asset} ({resolution} min)")
    
    # Fetch real candle data
    df_candles = fetcher.get_candles(selected_asset, resolution=resolution, days=days_to_show)
    
    if df_candles is not None:
        fig = go.Figure(data=[go.Candlestick(x=df_candles['time'],
                    open=df_candles['open'],
                    high=df_candles['high'],
                    low=df_candles['low'],
                    close=df_candles['close'])])
    else:
        st.warning(f"Could not fetch candle data for {selected_asset}. Showing sample.")
        
        # Safe fallback for current_price if None
        base_p = current_price if current_price is not None else 100.0
        
        dates = pd.date_range(start="2023-01-01", periods=100, freq="H")
        fig = go.Figure(data=[go.Candlestick(x=dates,
                    open=[base_p + i*0.01 for i in range(100)],
                    high=[base_p + 0.1 + i*0.01 for i in range(100)],
                    low=[base_p - 0.1 + i*0.01 for i in range(100)],
                    close=[base_p + 0.05 + i*0.01 for i in range(100)])])
    
    fig.update_layout(
        template="plotly_dark",
        xaxis_rangeslider_visible=False,
        height=500,
        margin=dict(l=10, r=10, t=10, b=10),
    )
    st.plotly_chart(fig, use_container_width=True)

with col_sentiment:
    st.subheader("🌍 Live News Sentiment")
    
    # Pre-fetch bulk quotes for featured assets to show prices next to sentiment
    featured_symbols = ["EURUSD", "XAUUSD", "AAPL", "MSFT"]
    featured_quotes = fetcher.get_bulk_quotes(featured_symbols)

    # Function to create a neat sentiment row
    def sentiment_row(symbol):
        score = sentiment_engine.get_news_sentiment(symbol)
        trend = "Bullish" if score > 0 else ("Bearish" if score < 0 else "Neutral")
        
        q = featured_quotes.get(symbol, {})
        price = q.get('c', 0)
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.write(f"**{symbol}** (${price:,.2f})" if price else f"**{symbol}**")
            st.progress(max(0.01, min(1.0, (score + 1) / 2))) # Normalize -1..1 to 0..1 for progress bar
        with col2:
            st.write(f"{trend}")

    st.write("### Featured Assets")
    for asset in featured_symbols:
        sentiment_row(asset)
    
    st.markdown("---")
    current_score = sentiment_engine.get_news_sentiment(selected_asset)
    st.write(f"**Selected Asset Sentiment ({selected_asset})**")
    st.write(f"Score: {current_score:+.2f}")
    
    st.info("💡 **Signals Detected**: Fetching live signals...")

# Strategy Backtest Results
st.markdown("---")
st.subheader("📜 Backtest History")
df_results = load_backtest_data()
if df_results is not None:
    st.dataframe(df_results, use_container_width=True)
else:
    st.warning("No backtest results found. Run verify_strategy.py first.")

# User Interaction Section
with st.expander("🛠 Advanced Configuration"):
    st.number_input("Risk Per Trade (%)", 1.0, 5.0, 1.0)
    st.slider("ATR Multiplier", 1.0, 5.0, 2.0)

st.success("Dashboard Initialized Successfully.")
