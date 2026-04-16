import unittest
import pandas as pd
import numpy as np
import sys
from unittest.mock import patch, MagicMock

# Mock talib if not installed
try:
    import talib
except ImportError:
    mock_talib = MagicMock()
    sys.modules['talib'] = mock_talib

from src.analysis.technical_engine import TechnicalEngine

class TestTechnicalEngine(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame({
            'open': [1.1000] * 100,
            'high': [1.1010] * 100,
            'low': [1.0990] * 100,
            'close': [1.1000] * 100,
            'tick_volume': [100] * 100
        })

    @patch('talib.RSI')
    @patch('talib.BBANDS')
    @patch('talib.MACD')
    @patch('talib.ATR')
    def test_add_indicators(self, mock_atr, mock_macd, mock_bbands, mock_rsi):
        # Mock returns
        mock_rsi.return_value = np.array([50.0] * 100)
        mock_bbands.return_value = (np.array([1.1100] * 100), np.array([1.1000] * 100), np.array([1.0900] * 100))
        mock_macd.return_value = (np.array([0.0] * 100), np.array([0.0] * 100), np.array([0.0] * 100))
        mock_atr.return_value = np.array([0.0020] * 100)

        result_df = TechnicalEngine.add_indicators(self.df)

        # Check if columns are added
        self.assertIn('RSI', result_df.columns)
        self.assertIn('BB_UP', result_df.columns)
        self.assertIn('MACD', result_df.columns)
        self.assertIn('ATR', result_df.columns)
        self.assertIn('tenkan_sen', result_df.columns)
        self.assertIn('senkou_span_a', result_df.columns)
        self.assertIn('FIB_61_8', result_df.columns)

    def test_add_indicators_empty_df(self):
        empty_df = pd.DataFrame()
        result_df = TechnicalEngine.add_indicators(empty_df)
        self.assertTrue(result_df.empty)

if __name__ == '__main__':
    unittest.main()
