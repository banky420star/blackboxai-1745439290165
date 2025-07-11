import requests
import json
from typing import Dict, Any, Optional
from datetime import datetime

class TelegramBot:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.bot_token = config['telegram']['bot_token']
        self.chat_id = config['telegram']['chat_id']
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    def send_message(self, message: str) -> bool:
        """Send a message to Telegram"""
        if not self.bot_token or not self.chat_id:
            print("Telegram bot not configured")
            return False
        
        url = f"{self.base_url}/sendMessage"
        data = {
            'chat_id': self.chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        
        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Error sending Telegram message: {e}")
            return False
    
    def send_trade_notification(self, action: str, symbol: str, price: float, 
                              quantity: float, profit: Optional[float] = None) -> bool:
        """Send trade notification"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        message = f"🤖 <b>Trading Bot Alert</b>\n\n"
        message += f"📊 <b>Action:</b> {action.upper()}\n"
        message += f"💱 <b>Symbol:</b> {symbol}\n"
        message += f"💰 <b>Price:</b> ${price:.2f}\n"
        message += f"📈 <b>Quantity:</b> {quantity:.4f}\n"
        message += f"⏰ <b>Time:</b> {timestamp}\n"
        
        if profit is not None:
            profit_emoji = "✅" if profit > 0 else "❌"
            message += f"{profit_emoji} <b>Profit:</b> ${profit:.2f}\n"
        
        return self.send_message(message)
    
    def send_status_update(self, status: Dict[str, Any]) -> bool:
        """Send status update"""
        message = f"📊 <b>Trading Bot Status</b>\n\n"
        message += f"💰 <b>Capital:</b> ${status.get('capital', 0):.2f}\n"
        message += f"📈 <b>Portfolio Value:</b> ${status.get('portfolio_value', 0):.2f}\n"
        message += f"🔄 <b>Total Trades:</b> {status.get('total_trades', 0)}\n"
        message += f"📊 <b>Current Price:</b> ${status.get('current_price', 0):.2f}\n"
        message += f"⏰ <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return self.send_message(message)
    
    def send_error_notification(self, error: str) -> bool:
        """Send error notification"""
        message = f"🚨 <b>Trading Bot Error</b>\n\n"
        message += f"❌ <b>Error:</b> {error}\n"
        message += f"⏰ <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return self.send_message(message)
    
    def send_profit_alert(self, profit: float, threshold: float = 0) -> bool:
        """Send profit alert when threshold is reached"""
        if profit > threshold:
            message = f"🎉 <b>Profit Target Reached!</b>\n\n"
            message += f"💰 <b>Current Profit:</b> ${profit:.2f}\n"
            message += f"🎯 <b>Target:</b> ${threshold:.2f}\n"
            message += f"⏰ <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            return self.send_message(message)
        return False
    
    def test_connection(self) -> bool:
        """Test Telegram bot connection"""
        url = f"{self.base_url}/getMe"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            if data['ok']:
                bot_info = data['result']
                print(f"Telegram bot connected: @{bot_info['username']}")
                return True
            else:
                print("Telegram bot connection failed")
                return False
        except Exception as e:
            print(f"Error testing Telegram connection: {e}")
            return False