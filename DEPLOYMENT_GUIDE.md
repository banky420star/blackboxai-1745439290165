# DDQN Trading Bot - Deployment Guide

## 🚀 Quick Start

This guide will help you deploy the DDQN Trading Bot on your V server. The bot uses reinforcement learning to trade cryptocurrency on Bybit.

## 📋 Prerequisites

Before deploying, ensure you have:

1. **V Server** with Ubuntu 18.04+ or similar Linux distribution
2. **Bybit Account** with API access
3. **Telegram Bot** (optional, for notifications)
4. **Domain Name** (optional, for HTTPS)

## 🔑 Required API Keys

### Bybit API Setup
1. Log into your Bybit account
2. Go to API Management
3. Create a new API key with the following permissions:
   - Read (for fetching data)
   - Trade (for placing orders)
   - Transfer (optional)
4. Save your API key and secret

### Telegram Bot Setup (Optional)
1. Message @BotFather on Telegram
2. Create a new bot with `/newbot`
3. Get your bot token
4. Start a chat with your bot and get your chat ID

## 🛠️ Installation

### Option 1: Automated Deployment (Recommended)

1. **Clone the repository to your server:**
   ```bash
   git clone <your-repo-url> /opt/trading-bot
   cd /opt/trading-bot
   ```

2. **Run the deployment script:**
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

3. **Configure the bot:**
   ```bash
   sudo nano /opt/trading-bot/config.json
   ```

### Option 2: Manual Installation

1. **Update system packages:**
   ```bash
   sudo apt-get update && sudo apt-get upgrade -y
   ```

2. **Install dependencies:**
   ```bash
   sudo apt-get install -y python3 python3-pip python3-venv
   sudo apt-get install -y build-essential wget curl
   sudo apt-get install -y libta-lib0 libta-lib-dev
   sudo apt-get install -y nginx supervisor
   ```

3. **Set up the application:**
   ```bash
   sudo mkdir -p /opt/trading-bot
   sudo chown $USER:$USER /opt/trading-bot
   cp -r * /opt/trading-bot/
   cd /opt/trading-bot
   ```

4. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

5. **Run setup script:**
   ```bash
   chmod +x setup_bot.sh
   ./setup_bot.sh
   ```

## ⚙️ Configuration

### 1. Edit Configuration File

Edit `/opt/trading-bot/config.json` with your API keys:

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
  }
}
```

### 2. Important Configuration Options

- **`testnet`**: Set to `true` for testing, `false` for live trading
- **`initial_capital`**: Starting capital for the bot
- **`position_size`**: Percentage of capital to use per trade
- **`stop_loss`**: Stop loss percentage
- **`take_profit`**: Take profit percentage

## 🚀 Starting the Bot

### 1. Start the Web Server
```bash
sudo systemctl start trading-bot
sudo systemctl enable trading-bot
```

### 2. Check Status
```bash
sudo systemctl status trading-bot
```

### 3. View Logs
```bash
sudo journalctl -u trading-bot -f
```

## 📊 Web Dashboard

The bot includes a web dashboard accessible at:
- **Local**: http://localhost:5000
- **Remote**: http://your-server-ip

### Dashboard Features:
- Real-time portfolio overview
- Wallet balance
- Training status
- Model indicators
- Trade history
- Performance charts

## 🔄 Training the Model

### Initial Training
```bash
cd /opt/trading-bot
source venv/bin/activate
python main.py
```

### Continuous Training
```bash
python train_forever.py
```

### Using the Interactive Launcher
```bash
./run_bot.sh
```

## 📈 Monitoring

### 1. System Monitoring
```bash
# Check system resources
htop

# Check disk space
df -h

# Check memory usage
free -h
```

### 2. Bot Monitoring
```bash
# View real-time logs
tail -f /opt/trading-bot/logs/trading_bot.log

# Check bot status
curl http://localhost:5000/api/training_status

# View trade history
curl http://localhost:5000/api/trade_history
```

### 3. Telegram Notifications
The bot will send notifications for:
- Trade executions
- Portfolio updates
- Training progress
- Error alerts

## 🔧 Troubleshooting

### Common Issues

1. **TA-Lib Installation Failed**
   ```bash
   # For Ubuntu/Debian
   sudo apt-get install -y libta-lib0 libta-lib-dev
   
   # For CentOS/RHEL
   sudo yum install -y ta-lib ta-lib-devel
   ```

2. **Permission Denied**
   ```bash
   sudo chown -R $USER:$USER /opt/trading-bot
   chmod +x /opt/trading-bot/*.sh
   ```

3. **Port Already in Use**
   ```bash
   sudo netstat -tulpn | grep :5000
   sudo kill -9 <PID>
   ```

4. **API Connection Issues**
   - Verify API keys are correct
   - Check if testnet is enabled/disabled as needed
   - Ensure API permissions are set correctly

### Log Files
- **Application logs**: `/opt/trading-bot/logs/trading_bot.log`
- **System logs**: `sudo journalctl -u trading-bot`
- **Nginx logs**: `/var/log/nginx/access.log` and `/var/log/nginx/error.log`

## 🔒 Security Considerations

1. **Firewall Setup**
   ```bash
   sudo ufw allow 22/tcp
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw --force enable
   ```

2. **API Key Security**
   - Never commit API keys to version control
   - Use environment variables for sensitive data
   - Regularly rotate API keys

3. **SSL/HTTPS Setup** (Recommended)
   ```bash
   sudo apt-get install -y certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com
   ```

## 📊 Performance Optimization

1. **System Resources**
   - Ensure adequate RAM (minimum 2GB)
   - Use SSD storage for better I/O performance
   - Monitor CPU usage during training

2. **Bot Configuration**
   - Adjust `batch_size` based on available memory
   - Tune `learning_rate` for better convergence
   - Optimize `lookback_period` for your trading strategy

## 🔄 Updates and Maintenance

### Updating the Bot
```bash
cd /opt/trading-bot
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart trading-bot
```

### Backup Strategy
```bash
# Backup configuration and models
tar -czf backup-$(date +%Y%m%d).tar.gz \
  config.json \
  *.h5 \
  trade_history.csv \
  bot_results.csv
```

## 📞 Support

If you encounter issues:

1. Check the logs: `sudo journalctl -u trading-bot -f`
2. Verify configuration: `cat /opt/trading-bot/config.json`
3. Test API connection: `python -c "from fetch_bybit_data import BybitDataFetcher; print('API test')"`

## ⚠️ Disclaimer

This trading bot is for educational purposes. Cryptocurrency trading involves significant risk. Never invest more than you can afford to lose. The authors are not responsible for any financial losses.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.