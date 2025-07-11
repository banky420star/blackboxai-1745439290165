#!/usr/bin/env python3
"""
Main training script for the Trading Bot
"""

import json
import logging
import pandas as pd
import numpy as np
from typing import Dict, Any
import os
import sys

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
            logging.FileHandler('logs/trading_bot.log'),
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

def fetch_and_prepare_data(config: Dict[str, Any]) -> pd.DataFrame:
    """Fetch and prepare data for training"""
    logger = logging.getLogger(__name__)
    
    # Initialize data fetcher
    data_fetcher = BybitDataFetcher(config)
    
    # Check if we have existing data
    historical_file = config['data']['historical_data_file']
    engineered_file = config['data']['engineered_data_file']
    
    if os.path.exists(engineered_file):
        logger.info(f"Loading existing engineered data from {engineered_file}")
        df = data_fetcher.load_data(engineered_file)
        if not df.empty:
            return df
    
    # Fetch new data
    logger.info("Fetching historical data from Bybit...")
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
    df = data_fetcher.get_historical_data(symbol, interval, days_back=30)
    
    if df.empty:
        logger.error("Failed to fetch data from Bybit")
        sys.exit(1)
    
    # Save raw data
    data_fetcher.save_data(df, historical_file)
    logger.info(f"Saved raw data to {historical_file}")
    
    # Engineer features
    logger.info("Engineering features...")
    feature_engineer = FeatureEngineer(config)
    df = feature_engineer.process_data(df)
    
    if df.empty:
        logger.error("Feature engineering failed")
        sys.exit(1)
    
    # Save engineered data
    data_fetcher.save_data(df, engineered_file)
    logger.info(f"Saved engineered data to {engineered_file}")
    
    return df

def train_model(config: Dict[str, Any], data: pd.DataFrame) -> DDQNAgent:
    """Train the trading model"""
    logger = logging.getLogger(__name__)
    
    # Initialize components
    env = TradingEnvironment(config, data)
    state_size = 10  # Number of features in state
    action_size = 3  # Hold, Buy, Sell
    
    agent = DDQNAgent(config, state_size, action_size)
    
    # Initialize Telegram bot
    telegram_bot = TelegramBot(config)
    
    # Initialize loggers
    trade_logger = TradeLogger()
    results_logger = ResultsLogger()
    
    # Send startup notification
    telegram_bot.send_startup_notification("Trading Bot")
    
    # Training parameters
    episodes = 100
    best_profit = -float('inf')
    best_model_path = "models/best_model_default.weights.h5"
    
    logger.info(f"Starting training for {episodes} episodes...")
    
    try:
        # Train the model
        results = agent.train(env, episodes=episodes)
        
        for result in results:
            # Log result
            results_logger.log_result(result)
            
            # Send training update every 10 episodes
            if result['episode'] % 10 == 0:
                telegram_bot.send_training_update(
                    result['episode'],
                    result['total_reward'],
                    result['total_profit'],
                    result['epsilon']
                )
            
            # Save best model
            if result['total_profit'] > best_profit:
                best_profit = result['total_profit']
                agent.save_model(best_model_path)
                logger.info(f"New best model saved with profit: {best_profit:.2f}%")
        
        # Log final trades
        trades = env.get_trade_history()
        for trade in trades:
            trade_logger.log_trade(trade)
        
        # Send final results
        final_profit = env.get_total_profit()
        telegram_bot.send_profit_update(
            final_profit * 100,
            len(trades),
            env.capital,
            config['trading']['initial_capital']
        )
        
        logger.info(f"Training completed. Final profit: {final_profit:.2f}%")
        
    except Exception as e:
        logger.error(f"Training error: {str(e)}")
        telegram_bot.send_error_notification(str(e), "Training process")
        raise
    
    return agent

def main():
    """Main function"""
    print("🚀 Starting Trading Bot Training...")
    
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
        # Fetch and prepare data
        print("📊 Fetching and preparing data...")
        data = fetch_and_prepare_data(config)
        
        if data.empty:
            print("❌ No data available for training")
            sys.exit(1)
        
        print(f"✅ Data prepared: {len(data)} records with {len(data.columns)} features")
        
        # Train model
        print("🤖 Training model...")
        agent = train_model(config, data)
        
        print("✅ Training completed successfully!")
        print("📈 Model saved to models/best_model_default.weights.h5")
        print("📊 Results saved to bot_results.csv")
        print("📝 Trade history saved to trade_history.csv")
        
    except KeyboardInterrupt:
        print("\n⚠️ Training interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error during training: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()