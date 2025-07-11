import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np
from typing import Tuple

class DDQNModel:
    def __init__(self, state_size: int, action_size: int, learning_rate: float = 0.001):
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate
        
        # Build the main network
        self.main_network = self._build_network()
        
        # Build the target network
        self.target_network = self._build_network()
        
        # Compile the model
        self.main_network.compile(
            optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
            loss='mse'
        )
        
        # Initialize target network with main network weights
        self.update_target_network()
    
    def _build_network(self) -> keras.Model:
        """Build the neural network architecture"""
        model = keras.Sequential([
            layers.Dense(128, activation='relu', input_shape=(self.state_size,)),
            layers.Dropout(0.2),
            layers.Dense(64, activation='relu'),
            layers.Dropout(0.2),
            layers.Dense(32, activation='relu'),
            layers.Dense(self.action_size, activation='linear')
        ])
        
        return model
    
    def predict(self, state: np.ndarray) -> np.ndarray:
        """Predict Q-values for given state"""
        return self.main_network.predict(state, verbose=0)
    
    def predict_target(self, state: np.ndarray) -> np.ndarray:
        """Predict Q-values using target network"""
        return self.target_network.predict(state, verbose=0)
    
    def train(self, states: np.ndarray, targets: np.ndarray) -> float:
        """Train the main network"""
        history = self.main_network.fit(states, targets, epochs=1, verbose=0)
        return history.history['loss'][0]
    
    def update_target_network(self):
        """Update target network weights with main network weights"""
        self.target_network.set_weights(self.main_network.get_weights())
    
    def save_model(self, filepath: str):
        """Save the model weights"""
        self.main_network.save_weights(filepath)
    
    def load_model(self, filepath: str):
        """Load the model weights"""
        try:
            self.main_network.load_weights(filepath)
            self.target_network.load_weights(filepath)
        except:
            print(f"Could not load model from {filepath}")
    
    def get_weights(self):
        """Get main network weights"""
        return self.main_network.get_weights()
    
    def set_weights(self, weights):
        """Set main network weights"""
        self.main_network.set_weights(weights)