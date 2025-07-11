import requests
import json
import logging
from typing import Dict, Any, Optional

class TelegramBot:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.bot_token = config['telegram']['bot_token']
        self.chat_id = config['telegram']['chat_id']
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.logger = logging.getLogger(__name__)
    
    def send_message(self, message: str) -> bool:
        """Send a message to Telegram"""
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, data=data)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    self.logger.info("Message sent successfully to Telegram")
                    return True
                else:
                    self.logger.error(f"Telegram API error: {result.get('description')}")
                    return False
            else:
                self.logger.error(f"HTTP error: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error sending Telegram message: {str(e)}")
            return False
    
    def send_trade_notification(self, action: str, symbol: str, price: float, 
                              quantity: float, profit: Optional[float] = None) -> bool:
        """Send a trade notification"""
        emoji_map = {
            'buy': '🟢',
            'sell': '🔴',
            'hold': '⚪'
        }
        
        emoji = emoji_map.get(action.lower(), '📊')
        
        message = f"{emoji} <b>Trade Alert</b>\n\n"
        message += f"<b>Action:</b> {action.upper()}\n"
        message += f"<b>Symbol:</b> {symbol}\n"
        message += f"<b>Price:</b> ${price:.2f}\n"
        message += f"<b>Quantity:</b> {quantity:.4f}\n"
        
        if profit is not None:
            profit_emoji = "💰" if profit > 0 else "📉"
            message += f"<b>Profit:</b> {profit_emoji} ${profit:.2f}\n"
        
        return self.send_message(message)
    
    def send_portfolio_update(self, portfolio_value: float, capital: float, 
                            shares_held: float, total_profit: float) -> bool:
        """Send portfolio update"""
        message = "📈 <b>Portfolio Update</b>\n\n"
        message += f"<b>Portfolio Value:</b> ${portfolio_value:.2f}\n"
        message += f"<b>Available Capital:</b> ${capital:.2f}\n"
        message += f"<b>Shares Held:</b> {shares_held:.4f}\n"
        
        profit_emoji = "💰" if total_profit > 0 else "📉"
        message += f"<b>Total Profit:</b> {profit_emoji} ${total_profit:.2f}\n"
        
        return self.send_message(message)
    
    def send_error_notification(self, error_message: str) -> bool:
        """Send error notification"""
        message = "⚠️ <b>Error Alert</b>\n\n"
        message += f"<b>Error:</b> {error_message}\n"
        message += "\nPlease check the bot logs for more details."
        
        return self.send_message(message)
    
    def send_training_update(self, episode: int, total_episodes: int, 
                           reward: float, portfolio_value: float, epsilon: float) -> bool:
        """Send training progress update"""
        progress = (episode / total_episodes) * 100
        
        message = "🤖 <b>Training Update</b>\n\n"
        message += f"<b>Episode:</b> {episode}/{total_episodes} ({progress:.1f}%)\n"
        message += f"<b>Reward:</b> {reward:.2f}\n"
        message += f"<b>Portfolio Value:</b> ${portfolio_value:.2f}\n"
        message += f"<b>Epsilon:</b> {epsilon:.3f}\n"
        
        return self.send_message(message)