import pandas as pd
import json
import logging
from typing import Dict, Any, List
from datetime import datetime
import os

class TradeLogger:
    def __init__(self, filename: str = "trade_history.csv"):
        self.filename = filename
        self.trades = []
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Load existing trades if file exists
        self.load_trades()
    
    def log_trade(self, trade_data: Dict[str, Any]):
        """Log a trade to the history"""
        try:
            # Add timestamp if not present
            if 'timestamp' not in trade_data:
                trade_data['timestamp'] = datetime.now().isoformat()
            
            # Add trade to list
            self.trades.append(trade_data)
            
            # Save to file
            self.save_trades()
            
            self.logger.info(f"Trade logged: {trade_data.get('action', 'Unknown')} "
                           f"{trade_data.get('symbol', 'Unknown')} at "
                           f"{trade_data.get('price', 0)}")
            
        except Exception as e:
            self.logger.error(f"Error logging trade: {str(e)}")
    
    def save_trades(self):
        """Save trades to CSV file"""
        try:
            if self.trades:
                df = pd.DataFrame(self.trades)
                df.to_csv(self.filename, index=False)
                self.logger.info(f"Trades saved to {self.filename}")
        except Exception as e:
            self.logger.error(f"Error saving trades: {str(e)}")
    
    def load_trades(self):
        """Load trades from CSV file"""
        try:
            if os.path.exists(self.filename):
                df = pd.read_csv(self.filename)
                self.trades = df.to_dict('records')
                self.logger.info(f"Loaded {len(self.trades)} trades from {self.filename}")
            else:
                self.trades = []
                self.logger.info("No existing trade history found")
        except Exception as e:
            self.logger.error(f"Error loading trades: {str(e)}")
            self.trades = []
    
    def get_trades(self) -> List[Dict[str, Any]]:
        """Get all trades"""
        return self.trades
    
    def get_recent_trades(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get recent trades"""
        return self.trades[-count:] if self.trades else []
    
    def get_trades_by_symbol(self, symbol: str) -> List[Dict[str, Any]]:
        """Get trades for a specific symbol"""
        return [trade for trade in self.trades if trade.get('symbol') == symbol]
    
    def get_total_profit(self) -> float:
        """Calculate total profit from all trades"""
        total_profit = 0.0
        for trade in self.trades:
            profit = trade.get('profit', 0)
            if isinstance(profit, (int, float)):
                total_profit += profit
        return total_profit
    
    def get_win_rate(self) -> float:
        """Calculate win rate"""
        if not self.trades:
            return 0.0
        
        winning_trades = sum(1 for trade in self.trades 
                           if trade.get('profit', 0) > 0)
        return (winning_trades / len(self.trades)) * 100

class ResultsLogger:
    def __init__(self, filename: str = "bot_results.csv"):
        self.filename = filename
        self.results = []
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Load existing results if file exists
        self.load_results()
    
    def log_result(self, result_data: Dict[str, Any]):
        """Log a training result"""
        try:
            # Add timestamp if not present
            if 'timestamp' not in result_data:
                result_data['timestamp'] = datetime.now().isoformat()
            
            # Add result to list
            self.results.append(result_data)
            
            # Save to file
            self.save_results()
            
            self.logger.info(f"Result logged: Episode {result_data.get('episode', 'Unknown')}, "
                           f"Profit: {result_data.get('total_profit', 0):.2f}%")
            
        except Exception as e:
            self.logger.error(f"Error logging result: {str(e)}")
    
    def save_results(self):
        """Save results to CSV file"""
        try:
            if self.results:
                df = pd.DataFrame(self.results)
                df.to_csv(self.filename, index=False)
                self.logger.info(f"Results saved to {self.filename}")
        except Exception as e:
            self.logger.error(f"Error saving results: {str(e)}")
    
    def load_results(self):
        """Load results from CSV file"""
        try:
            if os.path.exists(self.filename):
                df = pd.read_csv(self.filename)
                self.results = df.to_dict('records')
                self.logger.info(f"Loaded {len(self.results)} results from {self.filename}")
            else:
                self.results = []
                self.logger.info("No existing results found")
        except Exception as e:
            self.logger.error(f"Error loading results: {str(e)}")
            self.results = []
    
    def get_results(self) -> List[Dict[str, Any]]:
        """Get all results"""
        return self.results
    
    def get_best_result(self) -> Dict[str, Any]:
        """Get the best result based on total profit"""
        if not self.results:
            return {}
        
        return max(self.results, key=lambda x: x.get('total_profit', 0))
    
    def get_average_profit(self) -> float:
        """Calculate average profit"""
        if not self.results:
            return 0.0
        
        total_profit = sum(result.get('total_profit', 0) for result in self.results)
        return total_profit / len(self.results)

def create_directories():
    """Create necessary directories"""
    directories = ['logs', 'models', 'data', 'backups']
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")

def backup_files():
    """Create backup of important files"""
    import shutil
    from datetime import datetime
    
    backup_dir = f"backups/backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    files_to_backup = [
        'config.json',
        'trade_history.csv',
        'bot_results.csv',
        'bot_status.json'
    ]
    
    for file in files_to_backup:
        if os.path.exists(file):
            shutil.copy2(file, backup_dir)
            print(f"Backed up: {file}")
    
    print(f"Backup created in: {backup_dir}")

def validate_config(config: Dict[str, Any]) -> bool:
    """Validate configuration file"""
    required_sections = ['bybit', 'telegram', 'trading', 'model', 'data']
    
    for section in required_sections:
        if section not in config:
            print(f"Missing required section: {section}")
            return False
    
    # Check Bybit configuration
    bybit_config = config['bybit']
    if not bybit_config.get('api_key') or bybit_config['api_key'] == "YOUR_BYBIT_API_KEY":
        print("Bybit API key not configured")
        return False
    
    if not bybit_config.get('api_secret') or bybit_config['api_secret'] == "YOUR_BYBIT_API_SECRET":
        print("Bybit API secret not configured")
        return False
    
    # Check trading configuration
    trading_config = config['trading']
    if trading_config.get('initial_capital', 0) <= 0:
        print("Initial capital must be greater than 0")
        return False
    
    if trading_config.get('position_size', 0) <= 0 or trading_config.get('position_size', 0) > 1:
        print("Position size must be between 0 and 1")
        return False
    
    print("Configuration validation passed")
    return True