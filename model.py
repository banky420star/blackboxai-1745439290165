import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np

class DDQNModel:
    def __init__(self, state_size: int, action_size: int, learning_rate: float = 0.001):
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate
        
        # Build the main model
        self.model = self._build_model()
        
        # Build the target model
        self.target_model = self._build_model()
        self.update_target_model()
    
    def _build_model(self):
        """Build the neural network model"""
        model = keras.Sequential([
            layers.Dense(128, activation='relu', input_shape=(self.state_size,)),
            layers.Dropout(0.2),
            layers.Dense(128, activation='relu'),
            layers.Dropout(0.2),
            layers.Dense(64, activation='relu'),
            layers.Dropout(0.2),
            layers.Dense(self.action_size, activation='linear')
        ])
        
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=self.learning_rate),
            loss='mse'
        )
        
        return model
    
    def update_target_model(self):
        """Update target model weights with main model weights"""
        self.target_model.set_weights(self.model.get_weights())
    
    def predict(self, state: np.ndarray) -> np.ndarray:
        """Predict Q-values for given state"""
        return self.model.predict(state, verbose=0)
    
    def predict_target(self, state: np.ndarray) -> np.ndarray:
        """Predict Q-values using target model"""
        return self.target_model.predict(state, verbose=0)
    
    def train(self, states: np.ndarray, targets: np.ndarray, batch_size: int = 32) -> float:
        """Train the model on a batch of data"""
        history = self.model.fit(
            states, targets, 
            batch_size=batch_size, 
            epochs=1, 
            verbose=0
        )
        return history.history['loss'][0]
    
    def save(self, filepath: str):
        """Save the model weights"""
        self.model.save_weights(filepath)
    
    def load(self, filepath: str):
        """Load the model weights"""
        self.model.load_weights(filepath)
        self.update_target_model()