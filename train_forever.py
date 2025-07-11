#!/usr/bin/env python3
"""
Continuous training script for live trading
"""

import json
import logging
import pandas as pd
import numpy as np
from typing import Dict, Any
import os
import sys
import time
from datetime import datetime, timedelta

# Import our modules
from fetch_bybit_data import BybitDataFetcher
from feature_engineering import FeatureEngineer
from environment import TradingEnvironment
from agent import DDQNAgent
from telegram_bot import TelegramBot
from utils import TradeLogger, ResultsLogger, create_directories, validate_config

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/train_forever.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def load_config() -> Dict[str, Any]:
    """Load configuration from config.json"""
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print("Error: config.json not found. Please create a configuration file.")
        sys.exit(1)
    except json.JSONDecodeError:
        print("Error: Invalid JSON in config.json")
        sys.exit(1)

def get_latest_data(config: Dict[str, Any]) -> pd.DataFrame:
    """Get the latest market data"""
    logger = logging.getLogger(__name__)
    
    # Initialize data fetcher
    data_fetcher = BybitDataFetcher(config)
    
    # Fetch recent data (last 24 hours)
    symbol = config['trading']['symbol']
    timeframe = config['trading']['timeframe']
    
    # Convert timeframe to Bybit format
    timeframe_map = {
        '1m': '1',
        '5m': '5', 
        '15m': '15',
        '30m': '30',
        '1h': '60',
        '4h': '240',
        '1d': 'D'
    }
    
    interval = timeframe_map.get(timeframe, '60')
    df = data_fetcher.get_historical_data(symbol, interval, days_back=1)
    
    if df.empty:
        logger.error("Failed to fetch latest data from Bybit")
        return pd.DataFrame()
    
    # Engineer features
    feature_engineer = FeatureEngineer(config)
    df = feature_engineer.process_data(df)
    
    return df

def continuous_training(config: Dict[str, Any]):
    """Run continuous training"""
    logger = logging.getLogger(__name__)
    
    # Initialize components
    telegram_bot = TelegramBot(config)
    trade_logger = TradeLogger()
    results_logger = ResultsLogger()
    
    # Send startup notification
    telegram_bot.send_startup_notification("Continuous Trading Bot")
    
    # Training parameters
    state_size = 10
    action_size = 3
    episodes_per_cycle = 10
    cycle_interval = 3600  # 1 hour
    
    # Initialize agent
    agent = DDQNAgent(config, state_size, action_size)
    
    # Load existing model if available
    best_model_path = "models/best_model_default.weights.h5"
    if os.path.exists(best_model_path):
        agent.load_model(best_model_path)
        logger.info("Loaded existing model")
    
    cycle_count = 0
    total_episodes = 0
    
    logger.info("Starting continuous training...")
    
    try:
        while True:
            cycle_count += 1
            logger.info(f"Starting training cycle {cycle_count}")
            
            # Get latest data
            data = get_latest_data(config)
            if data.empty:
                logger.warning("No data available, waiting for next cycle")
                time.sleep(cycle_interval)
                continue
            
            # Create environment
            env = TradingEnvironment(config, data)
            
            # Train for a few episodes
            results = agent.train(env, episodes=episodes_per_cycle)
            total_episodes += episodes_per_cycle
            
            # Process results
            for result in results:
                results_logger.log_result(result)
                
                # Send update every 50 episodes
                if total_episodes % 50 == 0:
                    telegram_bot.send_training_update(
                        total_episodes,
                        result['total_reward'],
                        result['total_profit'],
                        result['epsilon']
                    )
            
            # Log trades
            trades = env.get_trade_history()
            for trade in trades:
                trade_logger.log_trade(trade)
            
            # Save model periodically
            if cycle_count % 5 == 0:
                agent.save_model(best_model_path)
                logger.info(f"Model saved after {cycle_count} cycles")
            
            # Send cycle summary
            final_profit = env.get_total_profit()
            telegram_bot.send_profit_update(
                final_profit * 100,
                len(trades),
                env.capital,
                config['trading']['initial_capital']
            )
            
            logger.info(f"Cycle {cycle_count} completed. Total episodes: {total_episodes}")
            
            # Wait for next cycle
            time.sleep(cycle_interval)
            
    except KeyboardInterrupt:
        logger.info("Continuous training interrupted by user")
        telegram_bot.send_shutdown_notification("Continuous Trading Bot")
    except Exception as e:
        logger.error(f"Error in continuous training: {str(e)}")
        telegram_bot.send_error_notification(str(e), "Continuous training")
        raise

def main():
    """Main function"""
    print("🔄 Starting Continuous Trading Bot...")
    
    # Setup
    setup_logging()
    create_directories()
    
    # Load configuration
    config = load_config()
    
    # Validate configuration
    if not validate_config(config):
        print("❌ Configuration validation failed. Please check your config.json")
        sys.exit(1)
    
    try:
        # Start continuous training
        continuous_training(config)
        
    except KeyboardInterrupt:
        print("\n⚠️ Continuous training interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error during continuous training: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()