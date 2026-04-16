import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

class TelegramNotifier:
    def __init__(self):
        self.token = TELEGRAM_BOT_TOKEN
        self.chat_id = TELEGRAM_CHAT_ID
        self.enabled = bool(self.token and self.chat_id)

    def send_message(self, message):
        """Sends a text message to the Telegram chat."""
        if not self.enabled:
            print(f"Telegram Notification (Disabled): {message}")
            return
            
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        try:
            response = requests.post(url, json=payload)
            if response.status_code != 200:
                print(f"Failed to send Telegram message: {response.text}")
        except Exception as e:
            print(f"Error sending Telegram notification: {e}")

    def notify_trade(self, symbol, order_type, volume, price, sl=None):
        """Specific alert for new trade execution."""
        emoji = "🚀" if order_type == "buy" or order_type == mt5.ORDER_TYPE_BUY else "🔥"
        msg = f"{emoji} *NEW TRADE EXECUTED*\n\n"
        msg += f"*Symbol:* {symbol}\n"
        msg += f"*Type:* {order_type}\n"
        msg += f"*Volume:* {volume}\n"
        msg += f"*Price:* {price}\n"
        if sl:
            msg += f"*Stop Loss:* {sl}\n"
        
        self.send_message(msg)
