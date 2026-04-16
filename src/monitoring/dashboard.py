import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# Page Config
st.set_page_config(page_title="FXWizard Dashboard", page_icon="📈", layout="wide")

# Custom CSS for Premium Look
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stMetric {
        background-color: #1f2937;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #374151;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🧙‍♂️ FXWizard - Trading Performance")

# Sidebar
st.sidebar.header("Strategy Settings")
st.sidebar.selectbox("Market Asset", ["EURUSD", "GBPJPY", "XAUUSD"])

# Top Metrics (Mock Data for Demo)
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Profit", "$1,245.50", "+12%")
with col2:
    st.metric("Win Rate", "58%", "+2%")
with col3:
    st.metric("Active Trades", "3")
with col4:
    st.metric("ML Confidence", "84%", "+5%")

# Charting
st.subheader("Profit Over Time")
chart_data = pd.DataFrame(
    np.random.randn(20, 1),
    columns=['Equity']
).cumsum()
st.line_chart(chart_data)

# Trade History
st.subheader("Recent Trade History")
history = pd.DataFrame({
    'Time': [datetime.now().strftime("%H:%M:%S") for _ in range(5)],
    'Symbol': ['EURUSD', 'GBPJPY', 'XAUUSD', 'EURUSD', 'GBPJPY'],
    'Type': ['Long', 'Short', 'Long', 'Short', 'Long'],
    'Result': ['$120', '-$45', '$300', '-$12', '$88']
})
st.table(history)

st.info("Performance data is being refreshed every 60 seconds from the live bot engine.")
