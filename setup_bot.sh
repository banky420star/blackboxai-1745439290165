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

echo "✅ Python version $python_version is compatible"

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
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p data
mkdir -p models

# Create sample data files if they don't exist
if [ ! -f "engineered_data.csv" ]; then
    echo "📄 Creating sample data files..."
    echo "timestamp,open,high,low,close,volume" > engineered_data.csv
fi

if [ ! -f "bot_results.csv" ]; then
    echo "📄 Creating results file..."
    echo "episodes,rewards,portfolio_values,losses" > bot_results.csv
fi

if [ ! -f "trade_history.csv" ]; then
    echo "📄 Creating trade history file..."
    echo "timestamp,action,symbol,price,quantity,profit" > trade_history.csv
fi

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x run_bot.sh
chmod +x launch_live_bot.sh

echo "✅ Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Edit config.json with your API keys"
echo "2. Run 'python main.py' to train the model"
echo "3. Run 'python trade_server.py' to start the web dashboard"
echo "4. Run './run_bot.sh' for interactive setup"
echo ""
echo "🔑 Don't forget to set your Bybit API keys and Telegram bot credentials in config.json!"