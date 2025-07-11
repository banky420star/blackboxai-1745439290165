import pandas as pd
import numpy as np
import talib
from typing import Dict, Any
import logging

class FeatureEngineer:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.lookback_period = config['data']['lookback_period']
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators for the given dataframe"""
        try:
            # Ensure required columns exist
            required_columns = ['open', 'high', 'low', 'close', 'volume']
            for col in required_columns:
                if col not in df.columns:
                    raise ValueError(f"Required column '{col}' not found in dataframe")
            
            # Convert to numeric
            for col in required_columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Remove any rows with NaN values
            df = df.dropna()
            
            if len(df) < 50:  # Need minimum data for indicators
                self.logger.warning("Insufficient data for technical indicators")
                return df
            
            # RSI (Relative Strength Index)
            df['rsi'] = talib.RSI(df['close'].values, timeperiod=14)
            
            # MACD (Moving Average Convergence Divergence)
            macd, macd_signal, macd_hist = talib.MACD(df['close'].values)
            df['macd'] = macd
            df['macd_signal'] = macd_signal
            df['macd_histogram'] = macd_hist
            
            # Bollinger Bands
            bb_upper, bb_middle, bb_lower = talib.BBANDS(df['close'].values)
            df['bb_upper'] = bb_upper
            df['bb_middle'] = bb_middle
            df['bb_lower'] = bb_lower
            df['bb_width'] = (bb_upper - bb_lower) / bb_middle
            
            # Moving Averages
            df['sma_20'] = talib.SMA(df['close'].values, timeperiod=20)
            df['sma_50'] = talib.SMA(df['close'].values, timeperiod=50)
            df['ema_12'] = talib.EMA(df['close'].values, timeperiod=12)
            df['ema_26'] = talib.EMA(df['close'].values, timeperiod=26)
            
            # Stochastic Oscillator
            stoch_k, stoch_d = talib.STOCH(df['high'].values, df['low'].values, df['close'].values)
            df['stoch_k'] = stoch_k
            df['stoch_d'] = stoch_d
            
            # Williams %R
            df['williams_r'] = talib.WILLR(df['high'].values, df['low'].values, df['close'].values)
            
            # Average True Range (ATR)
            df['atr'] = talib.ATR(df['high'].values, df['low'].values, df['close'].values)
            
            # Commodity Channel Index (CCI)
            df['cci'] = talib.CCI(df['high'].values, df['low'].values, df['close'].values)
            
            # Money Flow Index (MFI)
            df['mfi'] = talib.MFI(df['high'].values, df['low'].values, df['close'].values, df['volume'].values)
            
            # Price Rate of Change
            df['roc'] = talib.ROC(df['close'].values, timeperiod=10)
            
            # Momentum
            df['momentum'] = talib.MOM(df['close'].values, timeperiod=10)
            
            # Rate of Change Percentage
            df['rocp'] = talib.ROCP(df['close'].values, timeperiod=10)
            
            # Normalize volume
            df['volume_sma'] = talib.SMA(df['volume'].values, timeperiod=20)
            df['volume_ratio'] = df['volume'] / df['volume_sma']
            
            # Price changes
            df['price_change'] = df['close'].pct_change()
            df['price_change_5'] = df['close'].pct_change(periods=5)
            
            # High-Low spread
            df['hl_spread'] = (df['high'] - df['low']) / df['close']
            
            # Remove NaN values that result from indicator calculations
            df = df.dropna()
            
            self.logger.info(f"Calculated {len(df.columns)} technical indicators for {len(df)} data points")
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error calculating technical indicators: {str(e)}")
            return df
    
    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create additional features for the model"""
        try:
            # Add time-based features
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df['hour'] = df['timestamp'].dt.hour
                df['day_of_week'] = df['timestamp'].dt.dayofweek
                df['month'] = df['timestamp'].dt.month
            
            # Add lagged features
            for lag in [1, 2, 3, 5]:
                df[f'close_lag_{lag}'] = df['close'].shift(lag)
                df[f'volume_lag_{lag}'] = df['volume'].shift(lag)
                df[f'rsi_lag_{lag}'] = df['rsi'].shift(lag)
            
            # Add rolling statistics
            for window in [5, 10, 20]:
                df[f'close_rolling_mean_{window}'] = df['close'].rolling(window=window).mean()
                df[f'close_rolling_std_{window}'] = df['close'].rolling(window=window).std()
                df[f'volume_rolling_mean_{window}'] = df['volume'].rolling(window=window).mean()
            
            # Add price position within Bollinger Bands
            df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
            
            # Add trend indicators
            df['trend_sma'] = np.where(df['close'] > df['sma_20'], 1, 0)
            df['trend_ema'] = np.where(df['ema_12'] > df['ema_26'], 1, 0)
            
            # Add volatility indicators
            df['volatility'] = df['close'].rolling(window=20).std() / df['close'].rolling(window=20).mean()
            
            # Remove NaN values
            df = df.dropna()
            
            self.logger.info(f"Created additional features. Total features: {len(df.columns)}")
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error creating features: {str(e)}")
            return df
    
    def normalize_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize features to improve model performance"""
        try:
            # List of features to normalize (exclude timestamp and categorical features)
            exclude_columns = ['timestamp', 'trend_sma', 'trend_ema']
            feature_columns = [col for col in df.columns if col not in exclude_columns]
            
            # Z-score normalization for most features
            for col in feature_columns:
                if col in df.columns and df[col].dtype in ['float64', 'int64']:
                    mean_val = df[col].mean()
                    std_val = df[col].std()
                    if std_val > 0:
                        df[col] = (df[col] - mean_val) / std_val
            
            self.logger.info(f"Normalized {len(feature_columns)} features")
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error normalizing features: {str(e)}")
            return df
    
    def process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Complete data processing pipeline"""
        self.logger.info("Starting feature engineering pipeline")
        
        # Calculate technical indicators
        df = self.calculate_technical_indicators(df)
        
        # Create additional features
        df = self.create_features(df)
        
        # Normalize features
        df = self.normalize_features(df)
        
        self.logger.info(f"Feature engineering completed. Final shape: {df.shape}")
        
        return df