import json
import pandas as pd
import os
from typing import Dict, Any, List
from datetime import datetime

def log_trade(trade_data: Dict[str, Any], trade_history_file: str = "trade_history.csv"):
    """Log a trade to CSV file"""
    trade_data['timestamp'] = datetime.now().isoformat()
    
    # Create DataFrame from trade data
    df_trade = pd.DataFrame([trade_data])
    
    # Append to existing file or create new one
    if os.path.exists(trade_history_file):
        df_existing = pd.read_csv(trade_history_file)
        df_combined = pd.concat([df_existing, df_trade], ignore_index=True)
    else:
        df_combined = df_trade
    
    df_combined.to_csv(trade_history_file, index=False)
    print(f"Trade logged: {trade_data['action']} {trade_data.get('shares', 0)} shares at ${trade_data.get('price', 0):.2f}")

def save_bot_status(status: Dict[str, Any], status_file: str = "bot_status.json"):
    """Save bot status to JSON file"""
    status['last_updated'] = datetime.now().isoformat()
    
    with open(status_file, 'w') as f:
        json.dump(status, f, indent=2, default=str)

def load_bot_status(status_file: str = "bot_status.json") -> Dict[str, Any]:
    """Load bot status from JSON file"""
    if os.path.exists(status_file):
        with open(status_file, 'r') as f:
            return json.load(f)
    else:
        return {}

def save_results(results: List[Dict[str, Any]], results_file: str = "bot_results.csv"):
    """Save training results to CSV file"""
    df_results = pd.DataFrame(results)
    df_results.to_csv(results_file, index=False)
    print(f"Results saved to {results_file}")

def calculate_performance_metrics(trade_history_file: str = "trade_history.csv") -> Dict[str, float]:
    """Calculate performance metrics from trade history"""
    if not os.path.exists(trade_history_file):
        return {}
    
    df_trades = pd.read_csv(trade_history_file)
    
    if df_trades.empty:
        return {}
    
    # Calculate basic metrics
    total_trades = len(df_trades)
    buy_trades = len(df_trades[df_trades['action'] == 'buy'])
    sell_trades = len(df_trades[df_trades['action'] == 'sell'])
    
    # Calculate profit/loss for sell trades
    sell_trades_df = df_trades[df_trades['action'] == 'sell']
    total_profit = 0
    winning_trades = 0
    
    if not sell_trades_df.empty:
        for _, trade in sell_trades_df.iterrows():
            # Find corresponding buy trade
            buy_trade = df_trades[
                (df_trades['action'] == 'buy') & 
                (df_trades['timestamp'] < trade['timestamp'])
            ].iloc[-1] if len(df_trades[df_trades['action'] == 'buy']) > 0 else None
            
            if buy_trade is not None:
                profit = (trade['price'] - buy_trade['price']) * trade['shares']
                total_profit += profit
                if profit > 0:
                    winning_trades += 1
    
    # Calculate metrics
    win_rate = (winning_trades / sell_trades * 100) if sell_trades > 0 else 0
    avg_profit = total_profit / sell_trades if sell_trades > 0 else 0
    
    return {
        'total_trades': total_trades,
        'buy_trades': buy_trades,
        'sell_trades': sell_trades,
        'total_profit': total_profit,
        'win_rate': win_rate,
        'avg_profit': avg_profit
    }

def create_logs_directory():
    """Create logs directory if it doesn't exist"""
    if not os.path.exists('logs'):
        os.makedirs('logs')
        print("Created logs directory")

def setup_logging():
    """Setup logging configuration"""
    import logging
    
    create_logs_directory()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/trading_bot.log'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

def validate_config(config: Dict[str, Any]) -> bool:
    """Validate configuration file"""
    required_sections = ['bybit', 'telegram', 'trading', 'model', 'data']
    
    for section in required_sections:
        if section not in config:
            print(f"Missing required section: {section}")
            return False
    
    # Check Bybit configuration
    if not config['bybit'].get('api_key') or config['bybit']['api_key'] == 'YOUR_BYBIT_API_KEY':
        print("Please configure your Bybit API key")
        return False
    
    if not config['bybit'].get('api_secret') or config['bybit']['api_secret'] == 'YOUR_BYBIT_API_SECRET':
        print("Please configure your Bybit API secret")
        return False
    
    # Check Telegram configuration (optional)
    if not config['telegram'].get('bot_token') or config['telegram']['bot_token'] == 'YOUR_TELEGRAM_BOT_TOKEN':
        print("Warning: Telegram bot not configured")
    
    return True