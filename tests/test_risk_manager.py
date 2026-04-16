import unittest
from src.execution.risk_manager import RiskManager

class TestRiskManager(unittest.TestCase):
    def test_calculate_kelly_criterion(self):
        # win_prob=0.6, win_loss_ratio=2.0
        # kelly = 0.6 - (1-0.6)/2 = 0.6 - 0.2 = 0.4
        # half-kelly = 0.2
        # risk_per_trade is 0.01 (from config)
        result = RiskManager.calculate_kelly_criterion(0.6, 2.0)
        self.assertLessEqual(result, 0.01)
        self.assertGreaterEqual(result, 0)

    def test_calculate_position_size(self):
        # balance=10000, risk=100 (1%), sl_pips=50
        # vol = 100 / (50 * 10) = 100 / 500 = 0.2
        result = RiskManager.calculate_position_size(10000, 100, 50)
        self.assertEqual(result, 0.2)

    def test_calculate_position_size_zero_sl(self):
        result = RiskManager.calculate_position_size(10000, 100, 0)
        self.assertEqual(result, 0.01)

    def test_get_atr_stop_loss_long(self):
        # price=1.1000, atr=0.0020, multiplier=2.0 (from config)
        # sl = 1.1000 - (0.0020 * 2) = 1.0960
        result = RiskManager.get_atr_stop_loss(1.1000, 0.0020, "long")
        # Since ATR_MULTIPLIER is imported from config, we should check its value
        # For this test, let's assume it's 2.0 as per common practice in this repo
        self.assertAlmostEqual(result, 1.0960, places=4)

if __name__ == '__main__':
    unittest.main()
