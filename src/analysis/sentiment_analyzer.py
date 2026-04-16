import requests
from textblob import TextBlob
from config import FINNHUB_API_KEY, SENTIMENT_THRESHOLD

class SentimentAnalyzer:
    def __init__(self):
        self.api_key = FINNHUB_API_KEY

    def get_news_sentiment(self, symbol):
        """Fetches and analyzes news sentiment for a given symbol."""
        if not self.api_key:
            return 0.0 # Neutral if no API key
            
        url = f"https://finnhub.io/api/v1/news-sentiment?symbol={symbol}&token={self.api_key}"
        try:
            response = requests.get(url)
            data = response.json()
            
            if 'sentiment' in data:
                # Finnhub provides a score between 0 and 1 (bullish/bearish)
                # We normalize it to -1 to 1
                bullish = data['sentiment'].get('bullishPercent', 0.5)
                bearish = data['sentiment'].get('bearishPercent', 0.5)
                score = bearish - bullish # Negative is bearish, Positive is bullish in this mapping
                return score
            
            return 0.0
        except Exception as e:
            print(f"Error fetching sentiment: {e}")
            return 0.0

    def analyze_text(self, text):
        """Local analysis using TextBlob for low-latency social media feeds."""
        analysis = TextBlob(text)
        return analysis.sentiment.polarity # -1 to 1
