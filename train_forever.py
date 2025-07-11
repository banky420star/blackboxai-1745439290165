#!/usr/bin/env python3
"""
Continuous training script for live trading
"""

import json
import os
import sys
import time
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

def update_market_data(config: Dict[str, Any]) -> pd.DataFrame:
    """Update market data with latest information"""
    print("Updating market data...")
    
    # Fetch latest data
    df = fetch_market_data(config)
    
    if df.empty:
        print("Warning: Could not fetch new data, using existing data")
        if os.path.exists(config['data']['historical_data_file']):
            df = pd.read_csv(config['data']['historical_data_file'])
        else:
            print("Error: No data available")
            return pd.DataFrame()
    
    # Engineer features
    df_engineered = engineer_features(config, df)
    
    # Save updated data
    df_engineered.to_csv(config['data']['engineered_data_file'], index=False)
    
    return df_engineered

def live_trading_episode(env: TradingEnvironment, agent: DDQNAgent, 
                        episode: int, telegram_bot: TelegramBot) -> Dict[str, Any]:
    """Execute one live trading episode"""
    state = env.reset()
    total_reward = 0
    step_count = 0
    trades_made = 0
    
    print(f"Starting live trading episode {episode}")
    
    for step in range(len(env.data) - 1):  # Use all available data
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
        
        # Handle trading actions
        if action in [1, 2]:  # Buy or sell
            trades_made += 1
            action_name = 'BUY' if action == 1 else 'SELL'
            
            # Log trade
            trade_data = {
                'episode': episode,
                'step': step,
                'action': action_name.lower(),
                'price': info['current_price'],
                'shares': info.get('shares_held', 0),
                'reward': reward,
                'capital': info['capital'],
                'portfolio_value': info['portfolio_value']
            }
            log_trade(trade_data)
            
            # Send Telegram notification
            if telegram_bot.test_connection():
                profit = None
                if action == 2:  # Sell
                    profit = reward * env.initial_capital
                
                telegram_bot.send_trade_notification(
                    action_name, 
                    config['trading']['symbol'],
                    info['current_price'],
                    info.get('shares_held', 0),
                    profit
                )
        
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
        'total_trades': final_state['total_trades'],
        'trades_made': trades_made
    }

def main():
    """Main continuous training function"""
    print("🚀 Starting Continuous DDQN Trading Bot")
    
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
        telegram_bot.send_message("🤖 Continuous trading bot started!")
    
    # Initialize agent
    state_size = 10
    action_size = 3
    agent = DDQNAgent(config, state_size, action_size)
    
    # Load existing model if available
    model_file = 'best_model_default.weights.h5'
    if os.path.exists(model_file):
        agent.load_model(model_file)
        print(f"Loaded existing model: {model_file}")
    else:
        print("No existing model found. Starting with fresh model.")
    
    episode = 0
    best_reward = float('-inf')
    results = []
    
    print("Starting continuous training loop...")
    
    try:
        while True:
            episode += 1
            print(f"\n{'='*50}")
            print(f"Episode {episode}")
            print(f"{'='*50}")
            
            # Update market data
            df = update_market_data(config)
            
            if df.empty:
                print("Error: Could not get market data. Waiting 5 minutes...")
                time.sleep(300)
                continue
            
            # Initialize environment with updated data
            env = TradingEnvironment(config, df)
            
            # Execute trading episode
            episode_result = live_trading_episode(env, agent, episode, telegram_bot)
            results.append(episode_result)
            
            # Print results
            print(f"Episode {episode} Results:")
            print(f"  Total Reward: {episode_result['total_reward']:.2f}")
            print(f"  Final Capital: ${episode_result['final_capital']:.2f}")
            print(f"  Portfolio Value: ${episode_result['final_portfolio_value']:.2f}")
            print(f"  Total Trades: {episode_result['total_trades']}")
            print(f"  Trades Made: {episode_result['trades_made']}")
            print(f"  Epsilon: {agent.epsilon:.4f}")
            
            # Calculate profit
            profit = episode_result['final_capital'] - config['trading']['initial_capital']
            print(f"  Profit: ${profit:.2f}")
            
            # Save best model
            if episode_result['total_reward'] > best_reward:
                best_reward = episode_result['total_reward']
                agent.save_model('best_model_default.weights.h5')
                print(f"  🎉 New best model saved! (Reward: {best_reward:.2f})")
            
            # Save status
            status = {
                'scenario': 'default',
                'epoch': episode,
                'step': episode_result['step_count'],
                'reward': episode_result['total_reward'],
                'capital': episode_result['final_capital'],
                'epsilon': agent.epsilon
            }
            save_bot_status(status)
            
            # Send status update
            if telegram_bot.test_connection():
                telegram_bot.send_status_update(status)
                
                # Send profit alert if significant
                if profit > 50:  # Alert if profit > $50
                    telegram_bot.send_profit_alert(profit, 50)
            
            # Save results periodically
            if episode % 10 == 0:
                save_results(results, 'continuous_results.csv')
            
            # Wait before next episode
            print(f"Waiting 1 hour before next episode...")
            time.sleep(3600)  # Wait 1 hour
            
    except KeyboardInterrupt:
        print("\n🛑 Continuous training stopped by user")
        
        # Save final model and results
        agent.save_model('final_model_continuous.weights.h5')
        save_results(results, 'final_continuous_results.csv')
        
        if telegram_bot.test_connection():
            telegram_bot.send_message("🛑 Continuous trading bot stopped by user")
        
        print("Final model and results saved.")

if __name__ == "__main__":
    main()