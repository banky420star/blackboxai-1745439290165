#!/usr/bin/env python3
"""
Main training script for the DDQN Trading Bot
"""

import json
import os
import sys
import numpy as np
import pandas as pd
from typing import Dict, Any, List

# Import our modules
from environment import TradingEnvironment
from agent import DDQNAgent
from feature_engineering import engineer_features
from fetch_bybit_data import fetch_market_data
from telegram_bot import TelegramBot
from utils import log_trade, save_bot_status, save_results, setup_logging, validate_config

def load_config() -> Dict[str, Any]:
    """Load configuration from config.json"""
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: config.json not found. Please create a configuration file.")
        sys.exit(1)
    except json.JSONDecodeError:
        print("Error: Invalid JSON in config.json")
        sys.exit(1)

def prepare_data(config: Dict[str, Any]) -> pd.DataFrame:
    """Prepare and engineer market data"""
    print("Fetching market data...")
    
    # Check if we have existing data
    if os.path.exists(config['data']['historical_data_file']):
        print("Loading existing historical data...")
        df = pd.read_csv(config['data']['historical_data_file'])
    else:
        print("Fetching new data from Bybit...")
        df = fetch_market_data(config)
    
    if df.empty:
        print("Error: No data available for training")
        sys.exit(1)
    
    print("Engineering features...")
    df_engineered = engineer_features(config, df)
    
    # Save engineered data
    df_engineered.to_csv(config['data']['engineered_data_file'], index=False)
    print(f"Engineered data saved to {config['data']['engineered_data_file']}")
    
    return df_engineered

def train_episode(env: TradingEnvironment, agent: DDQNAgent, 
                 episode: int, max_steps: int = 1000) -> Dict[str, Any]:
    """Train for one episode"""
    state = env.reset()
    total_reward = 0
    step_count = 0
    
    for step in range(max_steps):
        # Choose action
        action = agent.act(state)
        
        # Take action
        next_state, reward, done, info = env.step(action)
        
        # Store experience
        agent.remember(state, action, reward, next_state, done)
        
        # Train agent
        if len(agent.replay_buffer) > agent.batch_size:
            loss = agent.train()
        
        total_reward += reward
        state = next_state
        step_count += 1
        
        # Log trade if action was taken
        if action in [1, 2]:  # Buy or sell
            trade_data = {
                'episode': episode,
                'step': step,
                'action': 'buy' if action == 1 else 'sell',
                'price': info['current_price'],
                'shares': info.get('shares_held', 0),
                'reward': reward,
                'capital': info['capital']
            }
            log_trade(trade_data)
        
        if done:
            break
    
    # Get final state
    final_state = env.get_state()
    
    return {
        'episode': episode,
        'total_reward': total_reward,
        'step_count': step_count,
        'final_capital': final_state['capital'],
        'final_portfolio_value': final_state['portfolio_value'],
        'total_trades': final_state['total_trades']
    }

def main():
    """Main training function"""
    print("🚀 Starting DDQN Trading Bot Training")
    
    # Setup logging
    logger = setup_logging()
    
    # Load configuration
    config = load_config()
    
    # Validate configuration
    if not validate_config(config):
        print("Configuration validation failed. Please check your config.json")
        sys.exit(1)
    
    # Initialize Telegram bot
    telegram_bot = TelegramBot(config)
    if telegram_bot.test_connection():
        telegram_bot.send_message("🤖 Trading bot training started!")
    
    # Prepare data
    df = prepare_data(config)
    
    # Initialize environment and agent
    env = TradingEnvironment(config, df)
    state_size = 10  # Number of features in state
    action_size = 3  # Hold, Buy, Sell
    
    agent = DDQNAgent(config, state_size, action_size)
    
    # Training parameters
    episodes = 100
    best_reward = float('-inf')
    results = []
    
    print(f"Starting training for {episodes} episodes...")
    
    for episode in range(episodes):
        print(f"\nEpisode {episode + 1}/{episodes}")
        
        # Train one episode
        episode_result = train_episode(env, agent, episode)
        results.append(episode_result)
        
        # Print episode results
        print(f"  Total Reward: {episode_result['total_reward']:.2f}")
        print(f"  Final Capital: ${episode_result['final_capital']:.2f}")
        print(f"  Portfolio Value: ${episode_result['final_portfolio_value']:.2f}")
        print(f"  Total Trades: {episode_result['total_trades']}")
        print(f"  Epsilon: {agent.epsilon:.4f}")
        
        # Save best model
        if episode_result['total_reward'] > best_reward:
            best_reward = episode_result['total_reward']
            agent.save_model('best_model_default.weights.h5')
            print(f"  🎉 New best model saved! (Reward: {best_reward:.2f})")
        
        # Save status
        status = {
            'scenario': 'default',
            'epoch': episode + 1,
            'step': episode_result['step_count'],
            'reward': episode_result['total_reward'],
            'capital': episode_result['final_capital'],
            'epsilon': agent.epsilon
        }
        save_bot_status(status)
        
        # Send status update every 10 episodes
        if (episode + 1) % 10 == 0:
            if telegram_bot.test_connection():
                telegram_bot.send_status_update(status)
    
    # Save final results
    save_results(results)
    
    # Save final model
    agent.save_model('final_model_default.weights.h5')
    
    # Send completion notification
    if telegram_bot.test_connection():
        final_profit = results[-1]['final_capital'] - config['trading']['initial_capital']
        telegram_bot.send_message(f"🎉 Training completed!\nFinal Profit: ${final_profit:.2f}")
    
    print("\n✅ Training completed!")
    print(f"Best reward: {best_reward:.2f}")
    print(f"Final profit: ${results[-1]['final_capital'] - config['trading']['initial_capital']:.2f}")

if __name__ == "__main__":
    main()