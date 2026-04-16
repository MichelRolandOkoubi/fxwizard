import numpy as np
from config import RISK_PER_TRADE, ATR_MULTIPLIER

class RiskManager:
    @staticmethod
    def calculate_kelly_criterion(win_prob, win_loss_ratio):
        """Calculates the Kelly bet size."""
        # K = W - [(1 - W) / R]
        # W = Win probability, R = win/loss ratio
        if win_loss_ratio == 0:
            return 0
        kelly = win_prob - ((1 - win_prob) / win_loss_ratio)
        return max(0, min(kelly * 0.5, RISK_PER_TRADE)) # Use "Half-Kelly" for safety

    @staticmethod
    def calculate_position_size(account_balance, risk_amount, stop_loss_pips):
        """Calculates volume based on risk per trade and SL distance."""
        # Simple formula: Volume = Risk_Amount / (SL_Pips * Pip_Value)
        # Needs symbol-specific pip value (e.g. 10 for standard lots on EURUSD)
        if stop_loss_pips == 0:
            return 0.01 # Minimum
        return round(risk_amount / (stop_loss_pips * 10), 2)

    @staticmethod
    def get_atr_stop_loss(current_price, atr, direction="long"):
        """Calculates ATR-based stop loss."""
        if direction == "long":
            return current_price - (atr * ATR_MULTIPLIER)
        else:
            return current_price + (atr * ATR_MULTIPLIER)
