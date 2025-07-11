import json
import pandas as pd
import logging
from datetime import datetime
from typing import Dict, Any, List

def setup_logging(config: Dict[str, Any]) -> logging.Logger:
    """Setup logging configuration"""
    log_level = getattr(logging, config['logging']['level'].upper())
    log_file = config['logging']['file']
    
    # Create logger
    logger = logging.getLogger('trading_bot')
    logger.setLevel(log_level)
    
    # Create file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(log_level)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def log_trade(trade_data: Dict[str, Any], trade_history_file: str = "trade_history.csv"):
    """Log a trade to CSV file"""
    try:
        # Add timestamp if not present
        if 'timestamp' not in trade_data:
            trade_data['timestamp'] = datetime.now().isoformat()
        
        # Convert to DataFrame
        df_new = pd.DataFrame([trade_data])
        
        # Load existing data or create new
        try:
            df_existing = pd.read_csv(trade_history_file)
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        except FileNotFoundError:
            df_combined = df_new
        
        # Save to CSV
        df_combined.to_csv(trade_history_file, index=False)
        
    except Exception as e:
        logging.error(f"Error logging trade: {str(e)}")

def save_results(results: Dict[str, Any], results_file: str = "bot_results.csv"):
    """Save training results to CSV"""
    try:
        df = pd.DataFrame(results)
        df.to_csv(results_file, index=False)
        logging.info(f"Results saved to {results_file}")
    except Exception as e:
        logging.error(f"Error saving results: {str(e)}")

def update_bot_status(status_data: Dict[str, Any], status_file: str = "bot_status.json"):
    """Update bot status file"""
    try:
        # Add timestamp
        status_data['timestamp'] = datetime.now().isoformat()
        
        with open(status_file, 'w') as f:
            json.dump(status_data, f, indent=2)
        
        logging.info("Bot status updated")
    except Exception as e:
        logging.error(f"Error updating bot status: {str(e)}")

def load_bot_status(status_file: str = "bot_status.json") -> Dict[str, Any]:
    """Load bot status from file"""
    try:
        with open(status_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except Exception as e:
        logging.error(f"Error loading bot status: {str(e)}")
        return {}

def calculate_metrics(portfolio_values: List[float], initial_capital: float) -> Dict[str, float]:
    """Calculate trading performance metrics"""
    if not portfolio_values:
        return {}
    
    returns = []
    for i in range(1, len(portfolio_values)):
        ret = (portfolio_values[i] - portfolio_values[i-1]) / portfolio_values[i-1]
        returns.append(ret)
    
    if not returns:
        return {}
    
    total_return = (portfolio_values[-1] - initial_capital) / initial_capital
    avg_return = sum(returns) / len(returns)
    volatility = (sum((r - avg_return) ** 2 for r in returns) / len(returns)) ** 0.5
    
    # Calculate maximum drawdown
    peak = portfolio_values[0]
    max_drawdown = 0
    
    for value in portfolio_values:
        if value > peak:
            peak = value
        drawdown = (peak - value) / peak
        if drawdown > max_drawdown:
            max_drawdown = drawdown
    
    return {
        'total_return': total_return,
        'avg_return': avg_return,
        'volatility': volatility,
        'max_drawdown': max_drawdown,
        'sharpe_ratio': avg_return / volatility if volatility > 0 else 0
    }

def format_currency(amount: float) -> str:
    """Format amount as currency string"""
    return f"${amount:,.2f}"

def format_percentage(value: float) -> str:
    """Format value as percentage string"""
    return f"{value:.2%}"