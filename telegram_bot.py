import requests
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

class TelegramBot:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.bot_token = config['telegram']['bot_token']
        self.chat_id = config['telegram']['chat_id']
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def send_message(self, message: str) -> bool:
        """Send a message to Telegram"""
        try:
            if not self.bot_token or self.bot_token == "YOUR_TELEGRAM_BOT_TOKEN":
                self.logger.warning("Telegram bot token not configured")
                return False
            
            if not self.chat_id or self.chat_id == "YOUR_TELEGRAM_CHAT_ID":
                self.logger.warning("Telegram chat ID not configured")
                return False
            
            url = f"{self.base_url}/sendMessage"
            data = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            
            response = requests.post(url, data=data)
            
            if response.status_code == 200:
                self.logger.info("Telegram message sent successfully")
                return True
            else:
                self.logger.error(f"Failed to send Telegram message: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error sending Telegram message: {str(e)}")
            return False
    
    def send_trade_notification(self, trade_type: str, symbol: str, price: float, 
                              quantity: float, profit: Optional[float] = None) -> bool:
        """Send trade notification"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if trade_type == "BUY":
                emoji = "🟢"
                action = "Bought"
            elif trade_type == "SELL":
                emoji = "🔴"
                action = "Sold"
            else:
                emoji = "⚪"
                action = trade_type
            
            message = f"{emoji} <b>{action} {symbol}</b>\n"
            message += f"💰 Price: ${price:,.2f}\n"
            message += f"📊 Quantity: {quantity:.4f}\n"
            message += f"⏰ Time: {timestamp}\n"
            
            if profit is not None:
                profit_emoji = "📈" if profit > 0 else "📉"
                message += f"{profit_emoji} Profit: {profit:+.2f}%\n"
            
            return self.send_message(message)
            
        except Exception as e:
            self.logger.error(f"Error sending trade notification: {str(e)}")
            return False
    
    def send_profit_update(self, current_profit: float, total_trades: int, 
                          current_capital: float, initial_capital: float) -> bool:
        """Send profit update notification"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            profit_emoji = "📈" if current_profit > 0 else "📉"
            
            message = f"{profit_emoji} <b>Profit Update</b>\n"
            message += f"💰 Current Profit: {current_profit:+.2f}%\n"
            message += f"💵 Capital: ${current_capital:,.2f}\n"
            message += f"📊 Total Trades: {total_trades}\n"
            message += f"⏰ Time: {timestamp}\n"
            
            return self.send_message(message)
            
        except Exception as e:
            self.logger.error(f"Error sending profit update: {str(e)}")
            return False
    
    def send_error_notification(self, error_message: str, context: str = "") -> bool:
        """Send error notification"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            message = f"⚠️ <b>Error Alert</b>\n"
            message += f"🚨 Error: {error_message}\n"
            if context:
                message += f"📋 Context: {context}\n"
            message += f"⏰ Time: {timestamp}\n"
            
            return self.send_message(message)
            
        except Exception as e:
            self.logger.error(f"Error sending error notification: {str(e)}")
            return False
    
    def send_training_update(self, episode: int, reward: float, profit: float, 
                           epsilon: float) -> bool:
        """Send training progress update"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            message = f"🤖 <b>Training Update</b>\n"
            message += f"📈 Episode: {episode}\n"
            message += f"🎯 Reward: {reward:.4f}\n"
            message += f"💰 Profit: {profit:+.2f}%\n"
            message += f"🎲 Epsilon: {epsilon:.4f}\n"
            message += f"⏰ Time: {timestamp}\n"
            
            return self.send_message(message)
            
        except Exception as e:
            self.logger.error(f"Error sending training update: {str(e)}")
            return False
    
    def send_startup_notification(self, bot_name: str = "Trading Bot") -> bool:
        """Send startup notification"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            message = f"🚀 <b>{bot_name} Started</b>\n"
            message += f"✅ Bot is now running\n"
            message += f"⏰ Started at: {timestamp}\n"
            
            return self.send_message(message)
            
        except Exception as e:
            self.logger.error(f"Error sending startup notification: {str(e)}")
            return False
    
    def send_shutdown_notification(self, bot_name: str = "Trading Bot", 
                                 final_profit: Optional[float] = None) -> bool:
        """Send shutdown notification"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            message = f"🛑 <b>{bot_name} Stopped</b>\n"
            message += f"❌ Bot has been stopped\n"
            if final_profit is not None:
                profit_emoji = "📈" if final_profit > 0 else "📉"
                message += f"{profit_emoji} Final Profit: {final_profit:+.2f}%\n"
            message += f"⏰ Stopped at: {timestamp}\n"
            
            return self.send_message(message)
            
        except Exception as e:
            self.logger.error(f"Error sending shutdown notification: {str(e)}")
            return False
    
    def test_connection(self) -> bool:
        """Test Telegram bot connection"""
        try:
            url = f"{self.base_url}/getMe"
            response = requests.get(url)
            
            if response.status_code == 200:
                bot_info = response.json()
                if bot_info.get("ok"):
                    self.logger.info(f"Telegram bot connection successful: {bot_info['result']['username']}")
                    return True
                else:
                    self.logger.error("Telegram bot connection failed")
                    return False
            else:
                self.logger.error(f"Telegram bot connection failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error testing Telegram connection: {str(e)}")
            return False