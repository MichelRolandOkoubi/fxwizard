import xgboost as xgb
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
import joblib
import os
from config import MODEL_PATH

class PredictionModel:
    def __init__(self):
        self.model = None
        if os.path.exists(MODEL_PATH):
            self.model = joblib.load(MODEL_PATH)

    def prepare_features(self, df):
        """Converts raw indicators into features for the model."""
        features = df[['RSI', 'MACD', 'MACD_SIGNAL', 'ATR', 'BB_UP', 'BB_LOW']].copy()
        features['returns'] = df['close'].pct_change()
        features.dropna(inplace=True)
        return features

    def train(self, df):
        """Trains an XGBoost model to predict if next close > current close."""
        features = self.prepare_features(df)
        X = features.values[:-1]
        y = (features['returns'].shift(-1) > 0).astype(int).values[:-1]
        
        self.model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            objective='binary:logistic'
        )
        self.model.fit(X, y)
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        joblib.dump(self.model, MODEL_PATH)

    def predict_probability(self, latest_df):
        """Returns the probability of price going up."""
        if self.model is None:
            return 0.5 # Neutral
            
        features = self.prepare_features(latest_df).tail(1)
        if features.empty:
            return 0.5
            
        prob = self.model.predict_proba(features.values)[0][1]
        return prob
