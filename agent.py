import numpy as np
import json
import os
from typing import Dict, Any, Tuple
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
        self.update_target_freq = config['model']['update_target_freq']
        
        # Initialize model and replay buffer
        self.model = DDQNModel(state_size, action_size, self.learning_rate)
        self.replay_buffer = ReplayBuffer(config['model']['memory_size'])
        
        # Training counters
        self.step_count = 0
        self.episode_count = 0
        
    def act(self, state: np.ndarray) -> int:
        """Choose action using epsilon-greedy policy"""
        if np.random.random() <= self.epsilon:
            return np.random.randint(self.action_size)
        
        q_values = self.model.predict(state.reshape(1, -1))
        return np.argmax(q_values[0])
    
    def train(self, batch_size: int = None) -> float:
        """Train the agent on a batch of experiences"""
        if batch_size is None:
            batch_size = self.batch_size
        
        if len(self.replay_buffer) < batch_size:
            return 0.0
        
        # Sample batch from replay buffer
        states, actions, rewards, next_states, dones = self.replay_buffer.sample(batch_size)
        
        # Get current Q-values
        current_q_values = self.model.predict(states)
        
        # Get next Q-values from target model
        next_q_values = self.model.predict_target(next_states)
        
        # Calculate target Q-values using Double DQN
        target_q_values = current_q_values.copy()
        
        for i in range(batch_size):
            if dones[i]:
                target_q_values[i][actions[i]] = rewards[i]
            else:
                # Double DQN: use main model to select action, target model to evaluate
                best_action = np.argmax(self.model.predict(next_states[i:i+1])[0])
                target_q_values[i][actions[i]] = rewards[i] + self.gamma * next_q_values[i][best_action]
        
        # Train the model
        history = self.model.train(states, target_q_values, epochs=1, verbose=0)
        loss = history.history['loss'][0] if history.history['loss'] else 0.0
        
        # Update target model periodically
        if self.step_count % self.update_target_freq == 0:
            self.model.update_target_model()
        
        # Decay epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        
        return loss
    
    def remember(self, state: np.ndarray, action: int, reward: float, 
                next_state: np.ndarray, done: bool):
        """Store experience in replay buffer"""
        self.replay_buffer.add(state, action, reward, next_state, done)
        self.step_count += 1
    
    def save_model(self, filepath: str):
        """Save the trained model"""
        self.model.save(filepath)
    
    def load_model(self, filepath: str):
        """Load a trained model"""
        if os.path.exists(filepath):
            self.model.load(filepath)
            print(f"Model loaded from {filepath}")
        else:
            print(f"Model file {filepath} not found")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            'epsilon': self.epsilon,
            'step_count': self.step_count,
            'episode_count': self.episode_count,
            'replay_buffer_size': len(self.replay_buffer)
        }