#!/usr/bin/env python3
"""
Continuous training script for the DDQN Trading Bot
"""

import json
import logging
import pandas as pd
import numpy as np
from datetime import datetime
import time
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

def continuous_training(config: dict):
    """Run continuous training"""
    logger = logging.getLogger(__name__)
    
    # Initialize components
    fetcher = BybitDataFetcher(config)
    telegram_bot = TelegramBot(config)
    
    # Load existing model if available
    agent = DDQNAgent(config)
    model_file = "best_model_default.weights.h5"
    
    if os.path.exists(model_file):
        logger.info("Loading existing model...")
        agent.load(model_file)
        telegram_bot.send_message("🔄 Loading existing model for continuous training...")
    else:
        logger.info("No existing model found, starting fresh...")
        telegram_bot.send_message("🆕 Starting fresh model for continuous training...")
    
    episode_count = 0
    
    while True:
        try:
            episode_count += 1
            logger.info(f"Starting episode {episode_count}")
            
            # Fetch fresh data
            symbol = config['trading']['symbol']
            timeframe = config['trading']['timeframe']
            
            logger.info(f"Fetching fresh data for {symbol}...")
            df = fetcher.get_historical_data(symbol, timeframe, limit=1000)
            
            if df.empty:
                logger.error("Failed to fetch data, retrying in 60 seconds...")
                time.sleep(60)
                continue
            
            # Calculate technical indicators
            df = calculate_technical_indicators(df)
            
            # Save updated data
            engineered_file = config['data']['engineered_data_file']
            df.to_csv(engineered_file)
            
            # Create environment
            env = TradingEnvironment(df, config)
            
            # Train for one episode
            state = env.reset()
            total_reward = 0
            step_count = 0
            
            while True:
                action = agent.act(state)
                next_state, reward, done, info = env.step(action)
                
                agent.remember(state, action, reward, next_state, done)
                state = next_state
                total_reward += reward
                step_count += 1
                
                # Train the model
                if len(agent.memory) > agent.batch_size:
                    loss = agent.replay()
                
                # Update target model periodically
                if agent.step_count % agent.update_target_freq == 0:
                    agent.update_target_model()
                
                if done:
                    break
            
            # Get final portfolio value
            portfolio_value = env.get_portfolio_value()
            initial_capital = config['trading']['initial_capital']
            profit = portfolio_value - initial_capital
            
            # Save model periodically
            if episode_count % 10 == 0:
                agent.save(model_file)
                logger.info(f"Model saved after {episode_count} episodes")
            
            # Update status
            status = {
                'scenario': 'default',
                'epoch': episode_count,
                'step': step_count,
                'reward': total_reward,
                'capital': portfolio_value
            }
            update_bot_status(status)
            
            # Send periodic updates
            if episode_count % 5 == 0:
                telegram_bot.send_training_update(
                    episode_count, 100, total_reward, portfolio_value, agent.epsilon
                )
            
            logger.info(f"Episode {episode_count} completed - "
                       f"Reward: {total_reward:.2f}, "
                       f"Portfolio: {portfolio_value:.2f}, "
                       f"Profit: {profit:.2f}")
            
            # Wait before next episode
            time.sleep(300)  # 5 minutes between episodes
            
        except Exception as e:
            logger.error(f"Error in episode {episode_count}: {str(e)}")
            telegram_bot.send_error_notification(f"Episode {episode_count} failed: {str(e)}")
            time.sleep(60)  # Wait before retrying

def main():
    """Main function"""
    # Load configuration
    config = load_config()
    
    # Setup logging
    logger = setup_logging(config)
    logger.info("Starting Continuous DDQN Trading Bot Training")
    
    # Send startup notification
    telegram_bot = TelegramBot(config)
    telegram_bot.send_message("🚀 Starting continuous training mode...")
    
    # Start continuous training
    continuous_training(config)

if __name__ == "__main__":
    main()