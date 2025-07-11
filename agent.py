import numpy as np
import json
import logging
from typing import Dict, Any, List
from model import DDQNModel
from replay_buffer import ReplayBuffer
from environment import TradingEnvironment

class DDQNAgent:
    def __init__(self, config: Dict[str, Any], state_size: int, action_size: int):
        self.config = config
        self.state_size = state_size
        self.action_size = action_size
        
        # Model parameters
        self.learning_rate = config['model']['learning_rate']
        self.gamma = config['model']['gamma']
        self.epsilon = config['model']['epsilon']
        self.epsilon_min = config['model']['epsilon_min']
        self.epsilon_decay = config['model']['epsilon_decay']
        self.batch_size = config['model']['batch_size']
        self.memory_size = config['model']['memory_size']
        self.target_update_freq = config['model']['target_update_freq']
        
        # Initialize components
        self.model = DDQNModel(state_size, action_size, self.learning_rate)
        self.memory = ReplayBuffer(self.memory_size)
        
        # Training variables
        self.step_count = 0
        self.episode_count = 0
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def act(self, state: np.ndarray) -> int:
        """Choose action using epsilon-greedy policy"""
        if np.random.random() <= self.epsilon:
            return np.random.randint(self.action_size)
        
        q_values = self.model.predict(state.reshape(1, -1))
        return np.argmax(q_values[0])
    
    def remember(self, state: np.ndarray, action: int, reward: float, 
                next_state: np.ndarray, done: bool):
        """Store experience in replay buffer"""
        self.memory.add(state, action, reward, next_state, done)
    
    def replay(self) -> float:
        """Train the model on a batch of experiences"""
        if len(self.memory) < self.batch_size:
            return 0.0
        
        # Sample batch from memory
        states, actions, rewards, next_states, dones = self.memory.sample(self.batch_size)
        
        # Get current Q-values
        current_q_values = self.model.predict(states)
        
        # Get next Q-values from target network
        next_q_values = self.model.predict_target(next_states)
        
        # Calculate target Q-values using Double DQN
        target_q_values = current_q_values.copy()
        
        for i in range(self.batch_size):
            if dones[i]:
                target_q_values[i][actions[i]] = rewards[i]
            else:
                # Double DQN: use main network to select action, target network to evaluate
                best_action = np.argmax(self.model.predict(next_states[i:i+1])[0])
                target_q_values[i][actions[i]] = rewards[i] + self.gamma * next_q_values[i][best_action]
        
        # Train the model
        loss = self.model.train(states, target_q_values)
        
        # Update epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        
        return loss
    
    def update_target_network(self):
        """Update target network"""
        self.model.update_target_network()
    
    def train(self, env: TradingEnvironment, episodes: int = 100) -> List[Dict[str, Any]]:
        """Train the agent for specified number of episodes"""
        results = []
        
        for episode in range(episodes):
            state = env.reset()
            total_reward = 0
            total_trades = 0
            
            while not env.done:
                # Choose action
                action = self.act(state)
                
                # Take action
                next_state, reward, done, info = env.step(action)
                
                # Store experience
                self.remember(state, action, reward, next_state, done)
                
                # Train on batch
                loss = self.replay()
                
                # Update state and counters
                state = next_state
                total_reward += reward
                total_trades = info.get('total_trades', 0)
                self.step_count += 1
                
                # Update target network periodically
                if self.step_count % self.target_update_freq == 0:
                    self.update_target_network()
            
            # Episode finished
            self.episode_count += 1
            total_profit = env.get_total_profit()
            
            result = {
                'episode': episode + 1,
                'total_reward': total_reward,
                'total_profit': total_profit,
                'total_trades': total_trades,
                'epsilon': self.epsilon,
                'capital': env.capital
            }
            
            results.append(result)
            
            # Log progress
            self.logger.info(f"Episode {episode + 1}: Reward={total_reward:.4f}, "
                           f"Profit={total_profit:.4f}, Trades={total_trades}, "
                           f"Epsilon={self.epsilon:.4f}")
            
            # Save status
            self._save_status(result)
        
        return results
    
    def _save_status(self, result: Dict[str, Any]):
        """Save current training status"""
        status = {
            'scenario': 'default',
            'epoch': result['episode'],
            'step': self.step_count,
            'reward': result['total_reward'],
            'capital': result['capital'],
            'epsilon': self.epsilon
        }
        
        with open('bot_status.json', 'w') as f:
            json.dump(status, f)
    
    def save_model(self, filepath: str):
        """Save the trained model"""
        self.model.save_model(filepath)
        self.logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load a trained model"""
        self.model.load_model(filepath)
        self.logger.info(f"Model loaded from {filepath}")
    
    def get_epsilon(self) -> float:
        """Get current epsilon value"""
        return self.epsilon