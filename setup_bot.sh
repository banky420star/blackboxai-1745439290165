#!/bin/bash

echo "🚀 Setting up Trading Bot Environment..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python version: $python_version"

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
echo "📚 Installing system dependencies..."
if command -v apt-get &> /dev/null; then
    # Ubuntu/Debian
    sudo apt-get update
    sudo apt-get install -y build-essential wget
    sudo apt-get install -y libta-lib0 libta-lib-dev
elif command -v yum &> /dev/null; then
    # CentOS/RHEL
    sudo yum groupinstall -y "Development Tools"
    sudo yum install -y wget
    sudo yum install -y ta-lib ta-lib-devel
elif command -v brew &> /dev/null; then
    # macOS
    brew install ta-lib
else
    echo "⚠️ Could not install TA-Lib system dependencies automatically."
    echo "Please install TA-Lib manually for your system."
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "❌ requirements.txt not found"
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs models data backups

# Check if config.json exists
if [ ! -f "config.json" ]; then
    echo "⚠️ config.json not found. Please create it with your API keys."
    echo "You can copy the example from the README."
else
    echo "✅ config.json found"
fi

# Test imports
echo "🧪 Testing imports..."
python3 -c "
import sys
try:
    import numpy
    import pandas
    import tensorflow
    import talib
    import flask
    import requests
    print('✅ All required packages imported successfully')
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    echo "✅ Setup completed successfully!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Edit config.json with your API keys"
    echo "2. Run: python3 main.py (for initial training)"
    echo "3. Run: python3 train_forever.py (for continuous training)"
    echo "4. Run: python3 trade_server.py (for web dashboard)"
else
    echo "❌ Setup failed. Please check the errors above."
    exit 1
fi