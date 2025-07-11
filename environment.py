import numpy as np
import pandas as pd
import json
from typing import Dict, List, Tuple, Any
import logging

class TradingEnvironment:
    def __init__(self, config: Dict[str, Any], data: pd.DataFrame):
        self.config = config
        self.data = data
        self.current_step = 0
        self.initial_capital = config['trading']['initial_capital']
        self.capital = self.initial_capital
        self.position = 0
        self.trades = []
        self.current_price = 0
        self.done = False
        
        # Trading parameters
        self.symbol = config['trading']['symbol']
        self.position_size = config['trading']['position_size']
        self.max_positions = config['trading']['max_positions']
        self.stop_loss = config['trading']['stop_loss']
        self.take_profit = config['trading']['take_profit']
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def reset(self) -> np.ndarray:
        """Reset the environment to initial state"""
        self.current_step = 0
        self.capital = self.initial_capital
        self.position = 0
        self.trades = []
        self.done = False
        self.current_price = self.data.iloc[self.current_step]['close']
        
        return self._get_state()
    
    def step(self, action: int) -> Tuple[np.ndarray, float, bool, Dict[str, Any]]:
        """Execute one step in the environment"""
        if self.done:
            return self._get_state(), 0, True, {}
        
        # Actions: 0 = hold, 1 = buy, 2 = sell
        reward = 0
        info = {}
        
        # Get current price
        self.current_price = self.data.iloc[self.current_step]['close']
        
        # Execute action
        if action == 1 and self.position == 0:  # Buy
            self.position = 1
            self.entry_price = self.current_price
            self.logger.info(f"Buy at {self.current_price}")
            
        elif action == 2 and self.position == 1:  # Sell
            self.position = 0
            profit = (self.current_price - self.entry_price) / self.entry_price
            self.capital *= (1 + profit)
            reward = profit
            self.trades.append({
                'entry_price': self.entry_price,
                'exit_price': self.current_price,
                'profit': profit,
                'step': self.current_step
            })
            self.logger.info(f"Sell at {self.current_price}, Profit: {profit:.4f}")
        
        # Check stop loss and take profit
        if self.position == 1:
            current_profit = (self.current_price - self.entry_price) / self.entry_price
            
            if current_profit <= -self.stop_loss:  # Stop loss
                self.position = 0
                self.capital *= (1 - self.stop_loss)
                reward = -self.stop_loss
                self.trades.append({
                    'entry_price': self.entry_price,
                    'exit_price': self.current_price,
                    'profit': -self.stop_loss,
                    'step': self.current_step,
                    'reason': 'stop_loss'
                })
                self.logger.info(f"Stop loss triggered at {self.current_price}")
                
            elif current_profit >= self.take_profit:  # Take profit
                self.position = 0
                self.capital *= (1 + self.take_profit)
                reward = self.take_profit
                self.trades.append({
                    'entry_price': self.entry_price,
                    'exit_price': self.current_price,
                    'profit': self.take_profit,
                    'step': self.current_step,
                    'reason': 'take_profit'
                })
                self.logger.info(f"Take profit triggered at {self.current_price}")
        
        # Move to next step
        self.current_step += 1
        
        # Check if episode is done
        if self.current_step >= len(self.data) - 1:
            self.done = True
            # Close any open position
            if self.position == 1:
                final_profit = (self.current_price - self.entry_price) / self.entry_price
                self.capital *= (1 + final_profit)
                reward += final_profit
                self.trades.append({
                    'entry_price': self.entry_price,
                    'exit_price': self.current_price,
                    'profit': final_profit,
                    'step': self.current_step,
                    'reason': 'episode_end'
                })
        
        info = {
            'capital': self.capital,
            'position': self.position,
            'current_price': self.current_price,
            'total_trades': len(self.trades)
        }
        
        return self._get_state(), reward, self.done, info
    
    def _get_state(self) -> np.ndarray:
        """Get the current state representation"""
        if self.current_step >= len(self.data):
            return np.zeros(10)  # Return zero state if out of bounds
        
        # Get current data point
        current_data = self.data.iloc[self.current_step]
        
        # Create feature vector
        features = [
            current_data['close'],
            current_data['volume'],
            current_data['rsi'],
            current_data['macd'],
            current_data['bb_upper'],
            current_data['bb_lower'],
            current_data['sma_20'],
            current_data['ema_12'],
            self.position,
            self.capital / self.initial_capital  # Normalized capital
        ]
        
        return np.array(features, dtype=np.float32)
    
    def get_total_profit(self) -> float:
        """Calculate total profit/loss"""
        return (self.capital - self.initial_capital) / self.initial_capital
    
    def get_trade_history(self) -> List[Dict[str, Any]]:
        """Get trade history"""
        return self.trades