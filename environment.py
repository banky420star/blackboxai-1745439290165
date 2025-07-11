import numpy as np
import pandas as pd
import json
from typing import Dict, List, Tuple, Any

class TradingEnvironment:
    def __init__(self, config: Dict[str, Any], data: pd.DataFrame):
        self.config = config
        self.data = data
        self.current_step = 0
        self.initial_capital = config['trading']['initial_capital']
        self.capital = self.initial_capital
        self.shares_held = 0
        self.cost_basis = 0
        self.total_shares_sold = 0
        self.total_sales_value = 0
        self.trades = []
        
        # Trading parameters
        self.position_size = config['trading']['position_size']
        self.max_positions = config['trading']['max_positions']
        self.stop_loss = config['trading']['stop_loss']
        self.take_profit = config['trading']['take_profit']
        
    def reset(self) -> np.ndarray:
        """Reset the environment to initial state"""
        self.current_step = 0
        self.capital = self.initial_capital
        self.shares_held = 0
        self.cost_basis = 0
        self.total_shares_sold = 0
        self.total_sales_value = 0
        self.trades = []
        return self._get_observation()
    
    def step(self, action: int) -> Tuple[np.ndarray, float, bool, Dict[str, Any]]:
        """Execute one step in the environment"""
        # Actions: 0 = hold, 1 = buy, 2 = sell
        current_price = self.data.iloc[self.current_step]['close']
        
        reward = 0
        done = False
        info = {}
        
        if action == 1:  # Buy
            if self.shares_held < self.max_positions:
                shares_to_buy = int(self.capital * self.position_size / current_price)
                if shares_to_buy > 0:
                    cost = shares_to_buy * current_price
                    if cost <= self.capital:
                        self.shares_held += shares_to_buy
                        self.capital -= cost
                        self.cost_basis = current_price
                        self.trades.append({
                            'step': self.current_step,
                            'action': 'buy',
                            'shares': shares_to_buy,
                            'price': current_price,
                            'cost': cost
                        })
        
        elif action == 2:  # Sell
            if self.shares_held > 0:
                shares_to_sell = self.shares_held
                revenue = shares_to_sell * current_price
                self.capital += revenue
                self.total_shares_sold += shares_to_sell
                self.total_sales_value += revenue
                self.shares_held = 0
                
                # Calculate profit/loss
                if self.cost_basis > 0:
                    profit = revenue - (shares_to_sell * self.cost_basis)
                    reward = profit
                
                self.trades.append({
                    'step': self.current_step,
                    'action': 'sell',
                    'shares': shares_to_sell,
                    'price': current_price,
                    'revenue': revenue
                })
        
        # Calculate current portfolio value
        portfolio_value = self.capital + (self.shares_held * current_price)
        
        # Check if episode is done
        if self.current_step >= len(self.data) - 1:
            done = True
            # Sell remaining shares at the end
            if self.shares_held > 0:
                final_revenue = self.shares_held * current_price
                self.capital += final_revenue
                portfolio_value = self.capital
        
        # Calculate reward based on portfolio value change
        if self.current_step > 0:
            prev_portfolio_value = self.capital + (self.shares_held * self.data.iloc[self.current_step - 1]['close'])
            reward = (portfolio_value - prev_portfolio_value) / self.initial_capital
        
        self.current_step += 1
        
        info = {
            'portfolio_value': portfolio_value,
            'capital': self.capital,
            'shares_held': self.shares_held,
            'current_price': current_price
        }
        
        return self._get_observation(), reward, done, info
    
    def _get_observation(self) -> np.ndarray:
        """Get the current state observation"""
        if self.current_step >= len(self.data):
            return np.zeros(10)  # Return zeros if at end of data
        
        current_data = self.data.iloc[self.current_step]
        
        # Create feature vector
        features = [
            current_data['close'],
            current_data['volume'],
            current_data.get('rsi', 50),
            current_data.get('macd', 0),
            current_data.get('bb_upper', current_data['close']),
            current_data.get('bb_lower', current_data['close']),
            self.capital / self.initial_capital,  # Normalized capital
            self.shares_held / self.max_positions,  # Normalized shares held
            current_data.get('ema_12', current_data['close']) / current_data['close'],
            current_data.get('ema_26', current_data['close']) / current_data['close']
        ]
        
        return np.array(features, dtype=np.float32)
    
    def get_state(self) -> Dict[str, Any]:
        """Get current environment state"""
        current_price = self.data.iloc[self.current_step]['close'] if self.current_step < len(self.data) else 0
        portfolio_value = self.capital + (self.shares_held * current_price)
        
        return {
            'step': self.current_step,
            'capital': self.capital,
            'shares_held': self.shares_held,
            'portfolio_value': portfolio_value,
            'current_price': current_price,
            'total_trades': len(self.trades)
        }