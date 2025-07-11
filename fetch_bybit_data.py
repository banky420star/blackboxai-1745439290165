import requests
import pandas as pd
import time
import json
from typing import Dict, Any, Optional
import logging

class BybitDataFetcher:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.base_url = "https://api.bybit.com"
        self.testnet_url = "https://api-testnet.bybit.com"
        self.logger = logging.getLogger(__name__)
        
    def get_historical_data(self, symbol: str, interval: str = "1h", 
                          limit: int = 1000) -> pd.DataFrame:
        """Fetch historical kline data from Bybit"""
        try:
            # Use testnet if configured
            base_url = self.testnet_url if self.config['bybit'].get('testnet', False) else self.base_url
            
            endpoint = "/v2/public/linear/kline"
            params = {
                'symbol': symbol,
                'interval': interval,
                'limit': limit
            }
            
            url = f"{base_url}{endpoint}"
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('ret_code') == 0:
                    result = data.get('result', [])
                    
                    # Convert to DataFrame
                    df = pd.DataFrame(result, columns=[
                        'timestamp', 'open', 'high', 'low', 'close', 
                        'volume', 'turnover'
                    ])
                    
                    # Convert types
                    for col in ['open', 'high', 'low', 'close', 'volume', 'turnover']:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                    
                    # Convert timestamp to datetime
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                    df = df.set_index('timestamp')
                    
                    # Sort by timestamp
                    df = df.sort_index()
                    
                    self.logger.info(f"Successfully fetched {len(df)} records for {symbol}")
                    return df
                else:
                    self.logger.error(f"API error: {data.get('ret_msg')}")
                    return pd.DataFrame()
            else:
                self.logger.error(f"HTTP error: {response.status_code}")
                return pd.DataFrame()
                
        except Exception as e:
            self.logger.error(f"Error fetching data: {str(e)}")
            return pd.DataFrame()
    
    def get_account_info(self) -> Dict[str, Any]:
        """Get account information"""
        try:
            api_key = self.config['bybit']['api_key']
            api_secret = self.config['bybit']['api_secret']
            
            # Use testnet if configured
            base_url = self.testnet_url if self.config['bybit'].get('testnet', False) else self.base_url
            
            endpoint = "/v2/private/wallet/balance"
            timestamp = str(int(time.time() * 1000))
            
            # Create signature
            import hmac
            import hashlib
            
            params = f"api_key={api_key}&timestamp={timestamp}"
            sign_payload = f"{endpoint}?{params}"
            signature = hmac.new(api_secret.encode(), sign_payload.encode(), hashlib.sha256).hexdigest()
            
            url = f"{base_url}{endpoint}?{params}&sign={signature}"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ret_code') == 0:
                    return data.get('result', {})
                else:
                    self.logger.error(f"API error: {data.get('ret_msg')}")
                    return {}
            else:
                self.logger.error(f"HTTP error: {response.status_code}")
                return {}
                
        except Exception as e:
            self.logger.error(f"Error fetching account info: {str(e)}")
            return {}
    
    def place_order(self, symbol: str, side: str, order_type: str, 
                   qty: float, price: Optional[float] = None) -> Dict[str, Any]:
        """Place an order on Bybit"""
        try:
            api_key = self.config['bybit']['api_key']
            api_secret = self.config['bybit']['api_secret']
            
            # Use testnet if configured
            base_url = self.testnet_url if self.config['bybit'].get('testnet', False) else self.base_url
            
            endpoint = "/v2/private/order/create"
            timestamp = str(int(time.time() * 1000))
            
            # Prepare parameters
            params = {
                'api_key': api_key,
                'timestamp': timestamp,
                'symbol': symbol,
                'side': side,
                'order_type': order_type,
                'qty': str(qty)
            }
            
            if price:
                params['price'] = str(price)
            
            # Create signature
            import hmac
            import hashlib
            
            param_str = '&'.join([f"{k}={v}" for k, v in sorted(params.items())])
            sign_payload = f"{endpoint}?{param_str}"
            signature = hmac.new(api_secret.encode(), sign_payload.encode(), hashlib.sha256).hexdigest()
            
            params['sign'] = signature
            
            url = f"{base_url}{endpoint}"
            response = requests.post(url, data=params)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ret_code') == 0:
                    self.logger.info(f"Order placed successfully: {data.get('result')}")
                    return data.get('result', {})
                else:
                    self.logger.error(f"Order failed: {data.get('ret_msg')}")
                    return {}
            else:
                self.logger.error(f"HTTP error: {response.status_code}")
                return {}
                
        except Exception as e:
            self.logger.error(f"Error placing order: {str(e)}")
            return {}