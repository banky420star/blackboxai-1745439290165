import pandas as pd
import numpy as np
import talib
from typing import Dict, Any

def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate technical indicators for the given dataframe"""
    # Ensure we have the required columns
    required_columns = ['open', 'high', 'low', 'close', 'volume']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")
    
    # Convert to float if needed
    for col in required_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Remove any rows with NaN values
    df = df.dropna()
    
    # Calculate RSI
    df['rsi'] = talib.RSI(df['close'].values, timeperiod=14)
    
    # Calculate MACD
    macd, macd_signal, macd_hist = talib.MACD(df['close'].values, 
                                             fastperiod=12, 
                                             slowperiod=26, 
                                             signalperiod=9)
    df['macd'] = macd
    df['macd_signal'] = macd_signal
    df['macd_hist'] = macd_hist
    
    # Calculate Bollinger Bands
    bb_upper, bb_middle, bb_lower = talib.BBANDS(df['close'].values, 
                                                timeperiod=20, 
                                                nbdevup=2, 
                                                nbdevdn=2)
    df['bb_upper'] = bb_upper
    df['bb_middle'] = bb_middle
    df['bb_lower'] = bb_lower
    
    # Calculate Bollinger Band position (0-1 scale)
    df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
    
    # Calculate Stochastic Oscillator
    stoch_k, stoch_d = talib.STOCH(df['high'].values, 
                                  df['low'].values, 
                                  df['close'].values,
                                  fastk_period=14, 
                                  slowk_period=3, 
                                  slowd_period=3)
    df['stoch_k'] = stoch_k
    df['stoch_d'] = stoch_d
    
    # Calculate Average True Range (ATR)
    df['atr'] = talib.ATR(df['high'].values, 
                         df['low'].values, 
                         df['close'].values, 
                         timeperiod=14)
    
    # Calculate Moving Averages
    df['sma_20'] = talib.SMA(df['close'].values, timeperiod=20)
    df['sma_50'] = talib.SMA(df['close'].values, timeperiod=50)
    df['ema_12'] = talib.EMA(df['close'].values, timeperiod=12)
    df['ema_26'] = talib.EMA(df['close'].values, timeperiod=26)
    
    # Calculate price momentum
    df['price_momentum'] = df['close'].pct_change(periods=5)
    
    # Calculate volume indicators
    df['volume_sma'] = talib.SMA(df['volume'].values, timeperiod=20)
    df['volume_ratio'] = df['volume'] / df['volume_sma']
    
    # Calculate volatility
    df['volatility'] = df['close'].rolling(window=20).std()
    
    # Remove any remaining NaN values
    df = df.dropna()
    
    return df

def normalize_features(df: pd.DataFrame, feature_columns: list) -> pd.DataFrame:
    """Normalize features using min-max scaling"""
    df_normalized = df.copy()
    
    for col in feature_columns:
        if col in df.columns:
            min_val = df[col].min()
            max_val = df[col].max()
            if max_val > min_val:
                df_normalized[col] = (df[col] - min_val) / (max_val - min_val)
            else:
                df_normalized[col] = 0
    
    return df_normalized

def get_feature_columns() -> list:
    """Get list of technical indicator columns"""
    return [
        'rsi', 'macd', 'macd_signal', 'macd_hist',
        'bb_upper', 'bb_middle', 'bb_lower', 'bb_position',
        'stoch_k', 'stoch_d', 'atr',
        'sma_20', 'sma_50', 'ema_12', 'ema_26',
        'price_momentum', 'volume_ratio', 'volatility'
    ]