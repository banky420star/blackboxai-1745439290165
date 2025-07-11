#!/usr/bin/env python3
"""
Main training script for the DDQN Trading Bot
"""

import json
import logging
import pandas as pd
import numpy as np
from datetime import datetime
import os

from environment import TradingEnvironment
from agent import DDQNAgent
from fetch_bybit_data import BybitDataFetcher
from feature_engineering import calculate_technical_indicators
from telegram_bot import TelegramBot
from utils import setup_logging, save_results, update_bot_status, log_trade

def load_config(config_file: str = "config.json") -> dict:
    """Load configuration from file"""
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Configuration file {config_file} not found!")
        exit(1)
    except json.JSONDecodeError as e:
        print(f"Error parsing configuration file: {e}")
        exit(1)

def fetch_and_prepare_data(config: dict) -> pd.DataFrame:
    """Fetch data from Bybit and prepare it for training"""
    logger = logging.getLogger(__name__)
    
    # Initialize data fetcher
    fetcher = BybitDataFetcher(config)
    
    # Fetch historical data
    symbol = config['trading']['symbol']
    timeframe = config['trading']['timeframe']
    
    logger.info(f"Fetching historical data for {symbol} with {timeframe} timeframe...")
    df = fetcher.get_historical_data(symbol, timeframe, limit=2000)
    
    if df.empty:
        logger.error("Failed to fetch data from Bybit")
        return pd.DataFrame()
    
    # Calculate technical indicators
    logger.info("Calculating technical indicators...")
    df = calculate_technical_indicators(df)
    
    # Save engineered data
    engineered_file = config['data']['engineered_data_file']
    df.to_csv(engineered_file)
    logger.info(f"Engineered data saved to {engineered_file}")
    
    return df

def train_model(config: dict, data: pd.DataFrame, episodes: int = 100) -> dict:
    """Train the DDQN model"""
    logger = logging.getLogger(__name__)
    
    # Initialize environment and agent
    env = TradingEnvironment(data, config)
    agent = DDQNAgent(config)
    
    # Initialize Telegram bot for notifications
    telegram_bot = TelegramBot(config)
    
    logger.info(f"Starting training for {episodes} episodes...")
    telegram_bot.send_message(f"🤖 Starting training for {episodes} episodes...")
    
    # Train the model
    results = agent.train(env, episodes)
    
    # Save the trained model
    model_file = "best_model_default.weights.h5"
    agent.save(model_file)
    logger.info(f"Model saved to {model_file}")
    
    # Calculate final metrics
    initial_capital = config['trading']['initial_capital']
    final_portfolio = results['portfolio_values'][-1] if results['portfolio_values'] else initial_capital
    total_profit = final_portfolio - initial_capital
    
    # Send final results to Telegram
    telegram_bot.send_message(
        f"✅ Training completed!\n\n"
        f"Final Portfolio: ${final_portfolio:.2f}\n"
        f"Total Profit: ${total_profit:.2f}\n"
        f"Profit %: {(total_profit/initial_capital)*100:.2f}%"
    )
    
    return results

def main():
    """Main function"""
    # Load configuration
    config = load_config()
    
    # Setup logging
    logger = setup_logging(config)
    logger.info("Starting DDQN Trading Bot Training")
    
    try:
        # Fetch and prepare data
        data = fetch_and_prepare_data(config)
        if data.empty:
            logger.error("Failed to prepare data for training")
            return
        
        # Train the model
        results = train_model(config, data, episodes=50)
        
        # Save results
        save_results(results)
        
        # Update bot status
        status = {
            'scenario': 'default',
            'epoch': len(results['episodes']),
            'step': len(results['episodes']) * 100,  # Approximate
            'reward': results['rewards'][-1] if results['rewards'] else 0,
            'capital': results['portfolio_values'][-1] if results['portfolio_values'] else config['trading']['initial_capital']
        }
        update_bot_status(status)
        
        logger.info("Training completed successfully!")
        
    except Exception as e:
        logger.error(f"Training failed: {str(e)}")
        
        # Send error notification
        try:
            telegram_bot = TelegramBot(config)
            telegram_bot.send_error_notification(str(e))
        except:
            pass

if __name__ == "__main__":
    main()