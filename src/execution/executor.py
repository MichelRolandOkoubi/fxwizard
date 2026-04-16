import MetaTrader5 as mt5
from config import MT5_LOGIN
from src.execution.notifier import TelegramNotifier

class Executor:
    def __init__(self):
        self.notifier = TelegramNotifier()

    def place_order(self, symbol, volume, order_type, stop_loss=0.0, take_profit=0.0):
        """Sends an order to MT5."""
        if order_type == "long":
            type_const = mt5.ORDER_TYPE_BUY
            price = mt5.symbol_info_tick(symbol).ask
        else:
            type_const = mt5.ORDER_TYPE_SELL
            price = mt5.symbol_info_tick(symbol).bid

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": type_const,
            "price": price,
            "sl": stop_loss,
            "tp": take_profit,
            "deviation": 20,
            "magic": 123456,
            "comment": "FXWizard AI Bot",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"Order failed for {symbol}: {result.comment}")
            self.notifier.send_message(f"❌ *TRADE FAILED:* {symbol}\nError: {result.comment}")
            return None
            
        print(f"Order successful: {symbol} {order_type} {volume}")
        self.notifier.notify_trade(symbol, order_type, volume, price, sl=stop_loss)
        return result

    def close_position(self, ticket):
        """Closes a specific position by ticket."""
        # Implementation for closing...
        pass
