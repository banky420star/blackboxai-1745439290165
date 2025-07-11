import pandas as pd
import numpy as np
import talib
from typing import Dict, Any

def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate technical indicators for the given dataframe"""
    # Make a copy to avoid modifying original data
    df = df.copy()
    
    # Ensure required columns exist
    required_columns = ['open', 'high', 'low', 'close', 'volume']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Required column '{col}' not found in dataframe")
    
    # Moving averages
    df['sma_20'] = talib.SMA(df['close'], timeperiod=20)
    df['sma_50'] = talib.SMA(df['close'], timeperiod=50)
    df['ema_12'] = talib.EMA(df['close'], timeperiod=12)
    df['ema_26'] = talib.EMA(df['close'], timeperiod=26)
    
    # RSI
    df['rsi'] = talib.RSI(df['close'], timeperiod=14)
    
    # MACD
    macd, macd_signal, macd_hist = talib.MACD(df['close'], fastperiod=12, slowperiod=26, signalperiod=9)
    df['macd'] = macd
    df['macd_signal'] = macd_signal
    df['macd_hist'] = macd_hist
    
    # Bollinger Bands
    bb_upper, bb_middle, bb_lower = talib.BBANDS(df['close'], timeperiod=20, nbdevup=2, nbdevdn=2)
    df['bb_upper'] = bb_upper
    df['bb_middle'] = bb_middle
    df['bb_lower'] = bb_lower
    df['bb_width'] = (bb_upper - bb_lower) / bb_middle
    
    # Stochastic
    slowk, slowd = talib.STOCH(df['high'], df['low'], df['close'], fastk_period=5, slowk_period=3, slowd_period=3)
    df['stoch_k'] = slowk
    df['stoch_d'] = slowd
    
    # Williams %R
    df['williams_r'] = talib.WILLR(df['high'], df['low'], df['close'], timeperiod=14)
    
    # Average True Range (ATR)
    df['atr'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=14)
    
    # Commodity Channel Index (CCI)
    df['cci'] = talib.CCI(df['high'], df['low'], df['close'], timeperiod=14)
    
    # Money Flow Index (MFI)
    df['mfi'] = talib.MFI(df['high'], df['low'], df['close'], df['volume'], timeperiod=14)
    
    # On Balance Volume (OBV)
    df['obv'] = talib.OBV(df['close'], df['volume'])
    
    # Price rate of change
    df['roc'] = talib.ROC(df['close'], timeperiod=10)
    
    # Momentum
    df['mom'] = talib.MOM(df['close'], timeperiod=10)
    
    # Volume indicators
    df['volume_sma'] = talib.SMA(df['volume'], timeperiod=20)
    df['volume_ratio'] = df['volume'] / df['volume_sma']
    
    # Price volatility
    df['volatility'] = df['close'].rolling(window=20).std()
    
    # Price momentum features
    df['price_change'] = df['close'].pct_change()
    df['price_change_5'] = df['close'].pct_change(periods=5)
    df['price_change_10'] = df['close'].pct_change(periods=10)
    
    # Remove NaN values
    df = df.dropna()
    
    return df

def normalize_features(df: pd.DataFrame, feature_columns: list = None) -> pd.DataFrame:
    """Normalize features using min-max scaling"""
    if feature_columns is None:
        # Default feature columns (excluding basic OHLCV and datetime)
        exclude_columns = ['open', 'high', 'low', 'close', 'volume', 'datetime', 'timestamp']
        feature_columns = [col for col in df.columns if col not in exclude_columns]
    
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

def create_lag_features(df: pd.DataFrame, columns: list, lags: list = [1, 2, 3, 5, 10]) -> pd.DataFrame:
    """Create lag features for specified columns"""
    df_lagged = df.copy()
    
    for col in columns:
        if col in df.columns:
            for lag in lags:
                df_lagged[f'{col}_lag_{lag}'] = df[col].shift(lag)
    
    return df_lagged

def engineer_features(config: Dict[str, Any], df: pd.DataFrame) -> pd.DataFrame:
    """Main feature engineering function"""
    print("Calculating technical indicators...")
    df = calculate_technical_indicators(df)
    
    # Create lag features for important indicators
    lag_columns = ['close', 'volume', 'rsi', 'macd', 'bb_width', 'atr']
    print("Creating lag features...")
    df = create_lag_features(df, lag_columns)
    
    # Normalize features
    print("Normalizing features...")
    df = normalize_features(df)
    
    # Remove any remaining NaN values
    df = df.dropna()
    
    print(f"Feature engineering complete. Final shape: {df.shape}")
    return df