import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple
import logging

class TradingEnvironment:
    def __init__(self, data: pd.DataFrame, config: Dict[str, Any]):
        self.data = data
        self.config = config
        self.current_step = 0
        self.initial_capital = config['trading']['initial_capital']
        self.capital = self.initial_capital
        self.shares_held = 0
        self.cost_basis = 0
        self.total_shares_sold = 0
        self.total_sales_value = 0
        self.lookback_period = config['data']['lookback_period']
        
        # Trading parameters
        self.position_size = config['trading']['position_size']
        self.max_positions = config['trading']['max_positions']
        self.stop_loss = config['trading']['stop_loss']
        self.take_profit = config['trading']['take_profit']
        
        self.logger = logging.getLogger(__name__)
        
    def reset(self) -> np.ndarray:
        """Reset the environment to initial state"""
        self.current_step = self.lookback_period
        self.capital = self.initial_capital
        self.shares_held = 0
        self.cost_basis = 0
        self.total_shares_sold = 0
        self.total_sales_value = 0
        
        return self._get_observation()
    
    def step(self, action: int) -> Tuple[np.ndarray, float, bool, Dict[str, Any]]:
        """Execute one step in the environment"""
        if self.current_step >= len(self.data) - 1:
            return self._get_observation(), 0, True, {}
        
        # Actions: 0 = hold, 1 = buy, 2 = sell
        current_price = self.data.iloc[self.current_step]['close']
        next_price = self.data.iloc[self.current_step + 1]['close']
        
        reward = 0
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
                        info['action'] = f'Bought {shares_to_buy} shares at {current_price}'
        
        elif action == 2:  # Sell
            if self.shares_held > 0:
                # Check stop loss and take profit
                price_change = (current_price - self.cost_basis) / self.cost_basis
                
                if price_change <= -self.stop_loss or price_change >= self.take_profit:
                    sell_value = self.shares_held * current_price
                    self.capital += sell_value
                    self.total_shares_sold += self.shares_held
                    self.total_sales_value += sell_value
                    
                    # Calculate reward based on profit/loss
                    profit = sell_value - (self.shares_held * self.cost_basis)
                    reward = profit
                    
                    info['action'] = f'Sold {self.shares_held} shares at {current_price}, profit: {profit:.2f}'
                    self.shares_held = 0
                    self.cost_basis = 0
        
        # Calculate current portfolio value
        portfolio_value = self.capital + (self.shares_held * current_price)
        
        # Move to next step
        self.current_step += 1
        
        # Check if episode is done
        done = self.current_step >= len(self.data) - 1
        
        # Add portfolio value to info
        info['portfolio_value'] = portfolio_value
        info['capital'] = self.capital
        info['shares_held'] = self.shares_held
        
        return self._get_observation(), reward, done, info
    
    def _get_observation(self) -> np.ndarray:
        """Get current state observation"""
        if self.current_step < self.lookback_period:
            return np.zeros(self.lookback_period * 5)  # 5 features per timestep
        
        # Get the last lookback_period rows
        data_slice = self.data.iloc[self.current_step - self.lookback_period:self.current_step]
        
        # Extract features
        features = []
        for _, row in data_slice.iterrows():
            features.extend([
                row['close'],
                row['volume'],
                row['rsi'],
                row['macd'],
                row['bb_position']
            ])
        
        # Add current position information
        current_price = self.data.iloc[self.current_step]['close']
        portfolio_value = self.capital + (self.shares_held * current_price)
        
        features.extend([
            self.capital / self.initial_capital,  # Normalized capital
            self.shares_held / self.max_positions,  # Normalized shares held
            portfolio_value / self.initial_capital,  # Normalized portfolio value
            (current_price - self.cost_basis) / self.cost_basis if self.cost_basis > 0 else 0  # Price change
        ])
        
        return np.array(features, dtype=np.float32)
    
    def get_portfolio_value(self) -> float:
        """Get current portfolio value"""
        if self.current_step >= len(self.data):
            return self.capital
        
        current_price = self.data.iloc[self.current_step]['close']
        return self.capital + (self.shares_held * current_price)