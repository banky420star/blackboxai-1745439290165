import requests
import pandas as pd
import time
import json
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

class BybitDataFetcher:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_key = config['bybit']['api_key']
        self.api_secret = config['bybit']['api_secret']
        self.testnet = config['bybit']['testnet']
        
        if self.testnet:
            self.base_url = "https://api-testnet.bybit.com"
        else:
            self.base_url = "https://api.bybit.com"
    
    def fetch_klines(self, symbol: str, interval: str, limit: int = 1000, 
                    start_time: Optional[int] = None, end_time: Optional[int] = None) -> pd.DataFrame:
        """Fetch kline/candlestick data from Bybit"""
        
        url = f"{self.base_url}/v2/public/linear/kline"
        
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        }
        
        if start_time:
            params['from'] = start_time
        if end_time:
            params['to'] = end_time
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data['ret_code'] != 0:
                raise Exception(f"Bybit API error: {data['ret_msg']}")
            
            # Parse kline data
            klines = data['result']
            df_data = []
            
            for kline in klines:
                df_data.append({
                    'timestamp': int(kline[0]),
                    'open': float(kline[1]),
                    'high': float(kline[2]),
                    'low': float(kline[3]),
                    'close': float(kline[4]),
                    'volume': float(kline[5])
                })
            
            df = pd.DataFrame(df_data)
            df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
            df = df.sort_values('timestamp').reset_index(drop=True)
            
            return df
            
        except Exception as e:
            print(f"Error fetching data: {e}")
            return pd.DataFrame()
    
    def fetch_historical_data(self, symbol: str, interval: str, days: int = 30) -> pd.DataFrame:
        """Fetch historical data for specified number of days"""
        
        end_time = int(time.time())
        start_time = end_time - (days * 24 * 60 * 60)  # days to seconds
        
        print(f"Fetching {days} days of {interval} data for {symbol}...")
        
        all_data = []
        current_start = start_time
        
        while current_start < end_time:
            current_end = min(current_start + (1000 * self._get_interval_seconds(interval)), end_time)
            
            df_chunk = self.fetch_klines(symbol, interval, limit=1000, 
                                       start_time=current_start, end_time=current_end)
            
            if not df_chunk.empty:
                all_data.append(df_chunk)
            
            current_start = current_end
            time.sleep(0.1)  # Rate limiting
        
        if all_data:
            df = pd.concat(all_data, ignore_index=True)
            df = df.drop_duplicates(subset=['timestamp']).sort_values('timestamp').reset_index(drop=True)
            print(f"Fetched {len(df)} data points")
            return df
        else:
            print("No data fetched")
            return pd.DataFrame()
    
    def _get_interval_seconds(self, interval: str) -> int:
        """Convert interval string to seconds"""
        interval_map = {
            '1': 60,
            '3': 180,
            '5': 300,
            '15': 900,
            '30': 1800,
            '60': 3600,
            '120': 7200,
            '240': 14400,
            '360': 21600,
            '720': 43200,
            'D': 86400,
            'W': 604800,
            'M': 2592000
        }
        return interval_map.get(interval, 3600)
    
    def get_account_info(self) -> Dict[str, Any]:
        """Get account information"""
        import hmac
        import hashlib
        
        endpoint = "/v2/private/wallet/balance"
        timestamp = str(int(time.time() * 1000))
        params = f"api_key={self.api_key}&timestamp={timestamp}"
        
        # Create signature
        sign_payload = f"{endpoint}?{params}"
        signature = hmac.new(self.api_secret.encode(), sign_payload.encode(), hashlib.sha256).hexdigest()
        
        url = f"{self.base_url}{endpoint}?{params}&sign={signature}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching account info: {e}")
            return {}

def fetch_market_data(config: Dict[str, Any]) -> pd.DataFrame:
    """Main function to fetch market data"""
    fetcher = BybitDataFetcher(config)
    
    symbol = config['trading']['symbol']
    interval = config['trading']['timeframe']
    days = 90  # Fetch 90 days of data
    
    df = fetcher.fetch_historical_data(symbol, interval, days)
    
    if not df.empty:
        # Save raw data
        df.to_csv(config['data']['historical_data_file'], index=False)
        print(f"Data saved to {config['data']['historical_data_file']}")
    
    return df