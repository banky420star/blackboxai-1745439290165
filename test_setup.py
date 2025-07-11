#!/usr/bin/env python3
"""
Test script to verify the trading bot setup
"""

import json
import sys
import os
from typing import Dict, Any

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        import numpy
        print("✅ numpy imported successfully")
    except ImportError as e:
        print(f"❌ numpy import failed: {e}")
        return False
    
    try:
        import pandas
        print("✅ pandas imported successfully")
    except ImportError as e:
        print(f"❌ pandas import failed: {e}")
        return False
    
    try:
        import tensorflow
        print("✅ tensorflow imported successfully")
    except ImportError as e:
        print(f"❌ tensorflow import failed: {e}")
        return False
    
    try:
        import talib
        print("✅ TA-Lib imported successfully")
    except ImportError as e:
        print(f"❌ TA-Lib import failed: {e}")
        return False
    
    try:
        import flask
        print("✅ Flask imported successfully")
    except ImportError as e:
        print(f"❌ Flask import failed: {e}")
        return False
    
    try:
        import requests
        print("✅ requests imported successfully")
    except ImportError as e:
        print(f"❌ requests import failed: {e}")
        return False
    
    return True

def test_config():
    """Test configuration file"""
    print("\n🔍 Testing configuration...")
    
    if not os.path.exists('config.json'):
        print("❌ config.json not found")
        return False
    
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        print("✅ config.json loaded successfully")
    except json.JSONDecodeError as e:
        print(f"❌ config.json is invalid JSON: {e}")
        return False
    
    # Check required sections
    required_sections = ['bybit', 'telegram', 'trading', 'model', 'data']
    for section in required_sections:
        if section not in config:
            print(f"❌ Missing section: {section}")
            return False
    
    print("✅ All required configuration sections present")
    
    # Check API keys
    if config['bybit']['api_key'] == 'YOUR_BYBIT_API_KEY':
        print("⚠️ Bybit API key not configured")
    else:
        print("✅ Bybit API key configured")
    
    if config['bybit']['api_secret'] == 'YOUR_BYBIT_API_SECRET':
        print("⚠️ Bybit API secret not configured")
    else:
        print("✅ Bybit API secret configured")
    
    return True

def test_modules():
    """Test our custom modules"""
    print("\n🔍 Testing custom modules...")
    
    try:
        from environment import TradingEnvironment
        print("✅ TradingEnvironment imported successfully")
    except ImportError as e:
        print(f"❌ TradingEnvironment import failed: {e}")
        return False
    
    try:
        from agent import DDQNAgent
        print("✅ DDQNAgent imported successfully")
    except ImportError as e:
        print(f"❌ DDQNAgent import failed: {e}")
        return False
    
    try:
        from model import DDQNModel
        print("✅ DDQNModel imported successfully")
    except ImportError as e:
        print(f"❌ DDQNModel import failed: {e}")
        return False
    
    try:
        from replay_buffer import ReplayBuffer
        print("✅ ReplayBuffer imported successfully")
    except ImportError as e:
        print(f"❌ ReplayBuffer import failed: {e}")
        return False
    
    try:
        from feature_engineering import calculate_technical_indicators
        print("✅ Feature engineering functions imported successfully")
    except ImportError as e:
        print(f"❌ Feature engineering import failed: {e}")
        return False
    
    try:
        from fetch_bybit_data import BybitDataFetcher
        print("✅ BybitDataFetcher imported successfully")
    except ImportError as e:
        print(f"❌ BybitDataFetcher import failed: {e}")
        return False
    
    try:
        from telegram_bot import TelegramBot
        print("✅ TelegramBot imported successfully")
    except ImportError as e:
        print(f"❌ TelegramBot import failed: {e}")
        return False
    
    try:
        from utils import log_trade, save_bot_status
        print("✅ Utility functions imported successfully")
    except ImportError as e:
        print(f"❌ Utility functions import failed: {e}")
        return False
    
    return True

def test_model_creation():
    """Test model creation"""
    print("\n🔍 Testing model creation...")
    
    try:
        from model import DDQNModel
        import numpy as np
        
        # Create a simple model
        model = DDQNModel(state_size=10, action_size=3)
        print("✅ Model created successfully")
        
        # Test prediction
        test_state = np.random.random(10)
        prediction = model.predict(test_state.reshape(1, -1))
        print(f"✅ Model prediction successful: {prediction.shape}")
        
        return True
    except Exception as e:
        print(f"❌ Model creation failed: {e}")
        return False

def test_environment():
    """Test environment creation"""
    print("\n🔍 Testing environment creation...")
    
    try:
        from environment import TradingEnvironment
        import pandas as pd
        
        # Create sample data
        sample_data = pd.DataFrame({
            'close': [100, 101, 102, 103, 104],
            'volume': [1000, 1100, 1200, 1300, 1400],
            'open': [99, 100, 101, 102, 103],
            'high': [101, 102, 103, 104, 105],
            'low': [98, 99, 100, 101, 102]
        })
        
        # Create sample config
        config = {
            'trading': {
                'initial_capital': 1000,
                'position_size': 0.1,
                'max_positions': 1,
                'stop_loss': 0.02,
                'take_profit': 0.04
            }
        }
        
        # Create environment
        env = TradingEnvironment(config, sample_data)
        print("✅ Environment created successfully")
        
        # Test reset
        state = env.reset()
        print(f"✅ Environment reset successful: {state.shape}")
        
        return True
    except Exception as e:
        print(f"❌ Environment creation failed: {e}")
        return False

def test_web_server():
    """Test web server"""
    print("\n🔍 Testing web server...")
    
    try:
        from trade_server import app
        print("✅ Flask app created successfully")
        
        # Test if app has required routes
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        required_routes = ['/api/profit_loss', '/api/training_status', '/api/trade_history']
        
        for route in required_routes:
            if route in routes:
                print(f"✅ Route {route} found")
            else:
                print(f"❌ Route {route} missing")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Web server test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting DDQN Trading Bot Setup Test")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_config),
        ("Custom Modules", test_modules),
        ("Model Creation", test_model_creation),
        ("Environment", test_environment),
        ("Web Server", test_web_server)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} test failed")
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your trading bot is ready to use.")
        print("\nNext steps:")
        print("1. Configure your API keys in config.json")
        print("2. Run 'python main.py' to start training")
        print("3. Run 'python trade_server.py' to start the web dashboard")
        print("4. Run 'python train_forever.py' for continuous training")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())