import numpy as np
import json
import logging
from typing import Dict, Any, Tuple
from environment import TradingEnvironment
from model import DDQNModel
from replay_buffer import ReplayBuffer

class DDQNAgent:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.state_size = config['data']['lookback_period'] * 5 + 4  # 5 features per timestep + 4 position features
        self.action_size = 3  # hold, buy, sell
        self.memory = ReplayBuffer(config['model']['memory_size'])
        
        # Model parameters
        self.learning_rate = config['model']['learning_rate']
        self.gamma = config['model']['gamma']
        self.epsilon = config['model']['epsilon']
        self.epsilon_min = config['model']['epsilon_min']
        self.epsilon_decay = config['model']['epsilon_decay']
        self.batch_size = config['model']['batch_size']
        self.update_target_freq = config['model']['update_target_freq']
        
        # Initialize models
        self.model = DDQNModel(self.state_size, self.action_size, self.learning_rate)
        self.target_model = DDQNModel(self.state_size, self.action_size, self.learning_rate)
        
        self.logger = logging.getLogger(__name__)
        self.step_count = 0
        
    def act(self, state: np.ndarray) -> int:
        """Choose action using epsilon-greedy policy"""
        if np.random.random() <= self.epsilon:
            return np.random.randint(self.action_size)
        
        act_values = self.model.predict(state.reshape(1, -1))
        return np.argmax(act_values[0])
    
    def remember(self, state: np.ndarray, action: int, reward: float, 
                next_state: np.ndarray, done: bool):
        """Store experience in replay buffer"""
        self.memory.add(state, action, reward, next_state, done)
    
    def replay(self) -> float:
        """Train the model on a batch of experiences"""
        if len(self.memory) < self.batch_size:
            return 0.0
        
        states, actions, rewards, next_states, dones = self.memory.sample(self.batch_size)
        
        # Get current Q-values
        current_q_values = self.model.predict(states)
        
        # Get next Q-values from target model
        next_q_values = self.target_model.predict(next_states)
        
        # Calculate target Q-values using Double DQN
        target_q_values = current_q_values.copy()
        
        for i in range(self.batch_size):
            if dones[i]:
                target_q_values[i][actions[i]] = rewards[i]
            else:
                # Double DQN: use main model to select action, target model to evaluate
                best_action = np.argmax(self.model.predict(next_states[i:i+1])[0])
                target_q_values[i][actions[i]] = rewards[i] + self.gamma * next_q_values[i][best_action]
        
        # Train the model
        loss = self.model.train(states, target_q_values, self.batch_size)
        
        # Update epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        
        return loss
    
    def update_target_model(self):
        """Update target model weights"""
        self.target_model.update_target_model()
    
    def save(self, filepath: str):
        """Save the model"""
        self.model.save(filepath)
    
    def load(self, filepath: str):
        """Load the model"""
        self.model.load(filepath)
        self.update_target_model()
    
    def train(self, env: TradingEnvironment, episodes: int = 100) -> Dict[str, Any]:
        """Train the agent"""
        results = {
            'episodes': [],
            'rewards': [],
            'portfolio_values': [],
            'losses': []
        }
        
        for episode in range(episodes):
            state = env.reset()
            total_reward = 0
            episode_losses = []
            
            while True:
                action = self.act(state)
                next_state, reward, done, info = env.step(action)
                
                self.remember(state, action, reward, next_state, done)
                state = next_state
                total_reward += reward
                
                # Train the model
                if len(self.memory) > self.batch_size:
                    loss = self.replay()
                    episode_losses.append(loss)
                
                # Update target model periodically
                self.step_count += 1
                if self.step_count % self.update_target_freq == 0:
                    self.update_target_model()
                
                if done:
                    break
            
            # Record results
            portfolio_value = env.get_portfolio_value()
            avg_loss = np.mean(episode_losses) if episode_losses else 0
            
            results['episodes'].append(episode)
            results['rewards'].append(total_reward)
            results['portfolio_values'].append(portfolio_value)
            results['losses'].append(avg_loss)
            
            self.logger.info(f"Episode {episode + 1}/{episodes} - "
                           f"Reward: {total_reward:.2f}, "
                           f"Portfolio: {portfolio_value:.2f}, "
                           f"Epsilon: {self.epsilon:.3f}")
        
        return results