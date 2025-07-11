#!/bin/bash

echo "🚀 Setting up DDQN Trading Bot..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python version $python_version is too old. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python $python_version detected"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install system dependencies for TA-Lib
echo "📦 Installing system dependencies..."
if command -v apt-get &> /dev/null; then
    # Ubuntu/Debian
    sudo apt-get update
    sudo apt-get install -y build-essential wget
    sudo apt-get install -y libta-lib-dev
elif command -v yum &> /dev/null; then
    # CentOS/RHEL
    sudo yum groupinstall -y "Development Tools"
    sudo yum install -y wget
    sudo yum install -y ta-lib-devel
elif command -v brew &> /dev/null; then
    # macOS
    brew install ta-lib
else
    echo "⚠️ Could not install TA-Lib system dependencies automatically."
    echo "Please install TA-Lib manually for your system."
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p models
mkdir -p data

# Check if config.json exists and is configured
if [ ! -f "config.json" ]; then
    echo "❌ config.json not found. Please create and configure it."
    exit 1
fi

# Validate configuration
echo "🔍 Validating configuration..."
python3 -c "
import json
import sys

try:
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    # Check required fields
    required_fields = [
        ('bybit', 'api_key'),
        ('bybit', 'api_secret'),
        ('trading', 'symbol'),
        ('trading', 'timeframe')
    ]
    
    for section, field in required_fields:
        if section not in config:
            print(f'❌ Missing section: {section}')
            sys.exit(1)
        if field not in config[section]:
            print(f'❌ Missing field: {section}.{field}')
            sys.exit(1)
        if config[section][field] in ['YOUR_BYBIT_API_KEY', 'YOUR_BYBIT_API_SECRET']:
            print(f'❌ Please configure {section}.{field}')
            sys.exit(1)
    
    print('✅ Configuration validated')
    
except Exception as e:
    print(f'❌ Configuration error: {e}')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Configuration validation failed. Please fix config.json"
    exit 1
fi

# Test imports
echo "🧪 Testing imports..."
python3 -c "
try:
    import numpy
    import pandas
    import tensorflow
    import talib
    import flask
    import requests
    print('✅ All imports successful')
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Import test failed. Please check your installation."
    exit 1
fi

echo "✅ Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Configure your API keys in config.json"
echo "2. Run 'python main.py' to start training"
echo "3. Run 'python trade_server.py' to start the web dashboard"
echo "4. Run 'python train_forever.py' for continuous training"