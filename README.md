# Trading Bot - Complete Implementation

Built by https://www.blackbox.ai

---

## 🚀 Project Overview

This project implements a complete **AI-powered cryptocurrency trading bot** that utilizes **Double Deep Q-Networks (DDQN)** for reinforcement learning-based trading decisions. The bot features real-time market data fetching, advanced technical analysis, automated trading strategies, and a comprehensive web dashboard for monitoring.

## ✨ Features

- **🤖 AI-Powered Trading**: Uses DDQN reinforcement learning for intelligent trading decisions
- **📊 Real-time Data**: Fetches live market data from Bybit exchange
- **📈 Technical Analysis**: 20+ technical indicators (RSI, MACD, Bollinger Bands, etc.)
- **🌐 Web Dashboard**: Real-time monitoring via Flask web server
- **📱 Telegram Notifications**: Instant alerts for trades and updates
- **🔄 Continuous Learning**: Self-improving model with continuous training
- **📋 Trade Logging**: Comprehensive trade history and performance tracking
- **🛡️ Risk Management**: Stop-loss, take-profit, and position sizing
- **🚀 Production Ready**: Complete deployment setup for V servers

## 📁 Project Structure

```
trading-bot/
├── 📄 Core Files
│   ├── main.py                 # Main training script
│   ├── train_forever.py        # Continuous training script
│   ├── trade_server.py         # Flask web server
│   ├── config.json             # Configuration file
│   └── requirements.txt        # Python dependencies
│
├── 🧠 AI Components
│   ├── agent.py                # DDQN agent implementation
│   ├── model.py                # Neural network architecture
│   ├── environment.py          # Trading environment simulation
│   └── replay_buffer.py        # Experience replay buffer
│
├── 📊 Data Processing
│   ├── fetch_bybit_data.py     # Bybit API data fetcher
│   ├── feature_engineering.py  # Technical indicators & features
│   └── utils.py                # Utility functions & logging
│
├── 📱 Communication
│   └── telegram_bot.py         # Telegram notifications
│
├── 🚀 Deployment
│   ├── deploy.sh               # V server deployment script
│   ├── setup_bot.sh            # Environment setup script
│   ├── gunicorn.conf.py        # Production server config
│   └── systemd/                # System service files
│
├── 📋 Scripts
│   ├── run_bot.sh              # Interactive launcher
│   ├── launch_live_bot.sh      # Live trading launcher
│   └── README.md               # This file
│
└── 📁 Directories (auto-created)
    ├── logs/                   # Application logs
    ├── models/                 # Trained model files
    ├── data/                   # Market data files
    └── backups/                # Backup files
```

## 🛠️ Installation & Setup

### Option 1: Quick Setup (Recommended)

```bash
# Clone or download the project
cd trading-bot

# Run the automated setup
./setup_bot.sh
```

### Option 2: Manual Setup

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create directories
mkdir -p logs models data backups

# 4. Configure API keys (see Configuration section)
```

## ⚙️ Configuration

### 1. Edit `config.json`

```json
{
  "bybit": {
    "api_key": "YOUR_BYBIT_API_KEY",
    "api_secret": "YOUR_BYBIT_API_SECRET",
    "testnet": true
  },
  "telegram": {
    "bot_token": "YOUR_TELEGRAM_BOT_TOKEN",
    "chat_id": "YOUR_TELEGRAM_CHAT_ID"
  },
  "trading": {
    "symbol": "BTCUSDT",
    "timeframe": "1h",
    "initial_capital": 1000.0,
    "position_size": 0.1,
    "stop_loss": 0.02,
    "take_profit": 0.04
  }
}
```

### 2. Get API Keys

**Bybit API:**
1. Create account at [Bybit](https://www.bybit.com)
2. Go to API Management
3. Create API key with trading permissions
4. Use testnet for testing

**Telegram Bot:**
1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Create new bot with `/newbot`
3. Get bot token
4. Get your chat ID by messaging [@userinfobot](https://t.me/userinfobot)

## 🚀 Usage

### 1. Initial Training

```bash
# Train the model with historical data
python3 main.py
```

### 2. Continuous Trading

```bash
# Run continuous training and trading
python3 train_forever.py
```

### 3. Web Dashboard

```bash
# Start the web server
python3 trade_server.py
```

Then visit: `http://localhost:5000`

### 4. Interactive Launcher

```bash
# Use the interactive launcher
./run_bot.sh
```

## 🌐 Web Dashboard

The web dashboard provides real-time monitoring:

- **📊 Profit/Loss**: Current trading performance
- **💰 Wallet Balance**: Account balance from Bybit
- **📈 Training Status**: Model training progress
- **📋 Trade History**: Recent trades and performance
- **📊 Model Indicators**: Technical analysis data

## 📱 Telegram Notifications

The bot sends notifications for:
- 🚀 Bot startup/shutdown
- 📈 Trade executions (buy/sell)
- 💰 Profit updates
- ⚠️ Error alerts
- 🤖 Training progress

## 🚀 V Server Deployment

### Automated Deployment

```bash
# Run as root on your V server
sudo ./deploy.sh
```

### Manual Deployment

```bash
# 1. Copy files to server
scp -r . user@your-server:/opt/trading-bot/

# 2. SSH into server
ssh user@your-server

# 3. Run deployment
cd /opt/trading-bot
sudo ./deploy.sh
```

### Post-Deployment

```bash
# 1. Configure API keys
sudo nano /opt/trading-bot/config.json

# 2. Start the service
sudo systemctl start trading-bot

# 3. Check status
sudo systemctl status trading-bot

# 4. Monitor
/opt/trading-bot/monitor.sh
```

### Useful Commands

```bash
# Service management
sudo systemctl start trading-bot
sudo systemctl stop trading-bot
sudo systemctl restart trading-bot
sudo systemctl status trading-bot

# View logs
sudo journalctl -u trading-bot -f

# Monitor system
/opt/trading-bot/monitor.sh

# Create backup
/opt/trading-bot/backup.sh
```

## 📊 Performance Monitoring

### Web Dashboard
- Access: `http://your-server-ip`
- Real-time profit/loss tracking
- Trade history and analysis
- Model performance metrics

### Command Line Monitoring
```bash
# Check bot status
/opt/trading-bot/monitor.sh

# View recent logs
tail -f /opt/trading-bot/logs/trading_bot.log

# Check system resources
htop
df -h
```

## 🔧 Customization

### Trading Strategy
Edit `config.json` to modify:
- Trading pairs (`symbol`)
- Timeframes (`timeframe`)
- Risk parameters (`stop_loss`, `take_profit`)
- Position sizing (`position_size`)

### Model Parameters
Adjust in `config.json`:
- Learning rate (`learning_rate`)
- Exploration rate (`epsilon`)
- Memory size (`memory_size`)
- Batch size (`batch_size`)

### Technical Indicators
Modify `feature_engineering.py` to add/remove indicators:
- RSI, MACD, Bollinger Bands
- Moving averages
- Volume indicators
- Custom indicators

## 🛡️ Security & Best Practices

### API Security
- Use testnet for testing
- Limit API permissions
- Rotate keys regularly
- Monitor API usage

### Server Security
- Keep system updated
- Use strong passwords
- Configure firewall
- Regular backups

### Trading Safety
- Start with small amounts
- Monitor performance closely
- Set appropriate stop-losses
- Don't risk more than you can afford to lose

## 📈 Performance Optimization

### System Requirements
- **CPU**: 2+ cores recommended
- **RAM**: 4GB+ for optimal performance
- **Storage**: 20GB+ for data and models
- **Network**: Stable internet connection

### Optimization Tips
- Use SSD storage for faster I/O
- Increase RAM for larger datasets
- Optimize batch sizes for your hardware
- Monitor resource usage

## 🔍 Troubleshooting

### Common Issues

**Import Errors:**
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

**API Errors:**
- Check API keys in `config.json`
- Verify API permissions
- Test with testnet first

**Service Won't Start:**
```bash
# Check logs
sudo journalctl -u trading-bot -f

# Check configuration
sudo systemctl status trading-bot
```

**Web Dashboard Not Loading:**
```bash
# Check if server is running
curl http://localhost:5000/api/profit_loss

# Check Nginx
sudo systemctl status nginx
```

## 📞 Support

### Logs Location
- Application logs: `/opt/trading-bot/logs/`
- System logs: `sudo journalctl -u trading-bot`
- Nginx logs: `/var/log/nginx/`

### Debug Mode
```bash
# Run in debug mode
python3 -u main.py 2>&1 | tee debug.log
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## ⚠️ Disclaimer

This trading bot is for educational and research purposes. Cryptocurrency trading involves significant risk. Always:
- Test thoroughly before live trading
- Start with small amounts
- Monitor performance closely
- Never risk more than you can afford to lose

The authors are not responsible for any financial losses incurred through the use of this software.

---

**🚀 Ready to deploy!** Follow the deployment instructions above to get your trading bot running on your V server.