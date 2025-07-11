import requests
import pandas as pd
import time
import hmac
import hashlib
import json
from typing import Dict, Any, Optional
import logging
from datetime import datetime, timedelta

class BybitDataFetcher:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_key = config['bybit']['api_key']
        self.api_secret = config['bybit']['api_secret']
        self.testnet = config['bybit']['testnet']
        
        # API endpoints
        if self.testnet:
            self.base_url = "https://api-testnet.bybit.com"
        else:
            self.base_url = "https://api.bybit.com"
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def _generate_signature(self, params: str) -> str:
        """Generate HMAC signature for API requests"""
        return hmac.new(
            self.api_secret.encode(),
            params.encode(),
            hashlib.sha256
        ).hexdigest()
    
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None, method: str = "GET") -> Dict[str, Any]:
        """Make authenticated API request"""
        try:
            # Add timestamp
            params = params or {}
            params['api_key'] = self.api_key
            params['timestamp'] = str(int(time.time() * 1000))
            
            # Create query string
            query_string = '&'.join([f"{k}={v}" for k, v in sorted(params.items())])
            
            # Generate signature
            signature = self._generate_signature(query_string)
            query_string += f"&sign={signature}"
            
            # Make request
            url = f"{self.base_url}{endpoint}?{query_string}"
            
            if method == "GET":
                response = requests.get(url)
            else:
                response = requests.post(url)
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"API request failed: {response.status_code} - {response.text}")
                return {"error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            self.logger.error(f"Error making API request: {str(e)}")
            return {"error": str(e)}
    
    def get_kline_data(self, symbol: str, interval: str = "1", limit: int = 1000, 
                      start_time: Optional[int] = None, end_time: Optional[int] = None) -> pd.DataFrame:
        """Fetch kline/candlestick data from Bybit"""
        try:
            endpoint = "/v2/public/linear/kline"
            params = {
                "symbol": symbol,
                "interval": interval,
                "limit": limit
            }
            
            if start_time:
                params["from"] = start_time
            if end_time:
                params["to"] = end_time
            
            response = self._make_request(endpoint, params)
            
            if "error" in response:
                self.logger.error(f"Failed to fetch kline data: {response['error']}")
                return pd.DataFrame()
            
            if response.get("ret_code") != 0:
                self.logger.error(f"API error: {response.get('ret_msg', 'Unknown error')}")
                return pd.DataFrame()
            
            # Parse response
            data = response.get("result", [])
            if not data:
                self.logger.warning("No data received from API")
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(data, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume', 'turnover'
            ])
            
            # Convert types
            numeric_columns = ['open', 'high', 'low', 'close', 'volume', 'turnover']
            for col in numeric_columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
            
            # Sort by timestamp
            df = df.sort_values('timestamp').reset_index(drop=True)
            
            self.logger.info(f"Fetched {len(df)} kline records for {symbol}")
            return df
            
        except Exception as e:
            self.logger.error(f"Error fetching kline data: {str(e)}")
            return pd.DataFrame()
    
    def get_historical_data(self, symbol: str, interval: str = "1", 
                          days_back: int = 30) -> pd.DataFrame:
        """Fetch historical data for specified number of days"""
        try:
            # Calculate time range
            end_time = int(time.time())
            start_time = end_time - (days_back * 24 * 60 * 60)
            
            all_data = []
            current_start = start_time
            
            while current_start < end_time:
                # Calculate end time for this batch (max 1000 records)
                current_end = min(current_start + (1000 * 60 * 60), end_time)
                
                # Fetch batch
                batch_df = self.get_kline_data(
                    symbol=symbol,
                    interval=interval,
                    start_time=current_start,
                    end_time=current_end
                )
                
                if not batch_df.empty:
                    all_data.append(batch_df)
                
                # Move to next batch
                current_start = current_end
                
                # Rate limiting
                time.sleep(0.1)
            
            if all_data:
                # Combine all batches
                combined_df = pd.concat(all_data, ignore_index=True)
                combined_df = combined_df.drop_duplicates(subset=['timestamp']).sort_values('timestamp')
                
                self.logger.info(f"Fetched {len(combined_df)} total historical records for {symbol}")
                return combined_df
            else:
                self.logger.warning("No historical data fetched")
                return pd.DataFrame()
                
        except Exception as e:
            self.logger.error(f"Error fetching historical data: {str(e)}")
            return pd.DataFrame()
    
    def get_account_info(self) -> Dict[str, Any]:
        """Get account information"""
        try:
            endpoint = "/v2/private/wallet/balance"
            response = self._make_request(endpoint)
            
            if "error" in response:
                return {"error": response["error"]}
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error fetching account info: {str(e)}")
            return {"error": str(e)}
    
    def get_symbol_info(self, symbol: str) -> Dict[str, Any]:
        """Get symbol information"""
        try:
            endpoint = "/v2/public/symbols"
            params = {"symbol": symbol}
            response = self._make_request(endpoint, params)
            
            if "error" in response:
                return {"error": response["error"]}
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error fetching symbol info: {str(e)}")
            return {"error": str(e)}
    
    def save_data(self, df: pd.DataFrame, filename: str):
        """Save data to CSV file"""
        try:
            df.to_csv(filename, index=False)
            self.logger.info(f"Data saved to {filename}")
        except Exception as e:
            self.logger.error(f"Error saving data: {str(e)}")
    
    def load_data(self, filename: str) -> pd.DataFrame:
        """Load data from CSV file"""
        try:
            df = pd.read_csv(filename)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            self.logger.info(f"Data loaded from {filename}")
            return df
        except Exception as e:
            self.logger.error(f"Error loading data: {str(e)}")
            return pd.DataFrame()