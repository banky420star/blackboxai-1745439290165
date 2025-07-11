# DDQN Trading Bot - Deployment Guide

This guide will help you deploy the DDQN Trading Bot on your V server.

## Prerequisites

- A V server with Ubuntu 18.04+ or Debian 9+
- Root access or sudo privileges
- At least 2GB RAM and 10GB storage
- Bybit API credentials
- Telegram bot token (optional but recommended)

## Quick Deployment

### 1. Upload Files to Server

First, upload all project files to your server. You can use SCP, SFTP, or Git:

```bash
# Using SCP
scp -r . user@your-server-ip:/tmp/trading-bot

# Using Git (if you have a repository)
git clone https://your-repo-url.git /tmp/trading-bot
```

### 2. Run Deployment Script

SSH into your server and run the deployment script:

```bash
cd /tmp/trading-bot
sudo chmod +x deploy.sh
sudo ./deploy.sh
```

The deployment script will:
- Install all system dependencies
- Set up Python virtual environment
- Install Python packages
- Create systemd services
- Configure nginx
- Set up firewall
- Create management scripts

### 3. Configure API Keys

Edit the configuration file:

```bash
sudo nano /opt/trading-bot/config.json
```

Update the following fields:
- `bybit.api_key`: Your Bybit API key
- `bybit.api_secret`: Your Bybit API secret
- `telegram.bot_token`: Your Telegram bot token (optional)
- `telegram.chat_id`: Your Telegram chat ID (optional)

### 4. Start the Bot

```bash
# Start the trading bot
sudo trading-bot-manage start

# Check status
sudo trading-bot-manage status

# View logs
sudo trading-bot-manage logs
```

## Manual Deployment

If you prefer to deploy manually, follow these steps:

### 1. System Setup

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install dependencies
sudo apt-get install -y python3 python3-pip python3-venv nginx git curl wget build-essential

# Install TA-Lib dependencies
sudo apt-get install -y libta-lib-dev
```

### 2. Create Application User

```bash
sudo useradd -r -s /bin/bash -d /opt/trading-bot trading-bot
sudo mkdir -p /opt/trading-bot
sudo chown trading-bot:trading-bot /opt/trading-bot
```

### 3. Install Application

```bash
# Copy files
sudo cp -r . /opt/trading-bot/
sudo chown -R trading-bot:trading-bot /opt/trading-bot

# Create virtual environment
cd /opt/trading-bot
sudo -u trading-bot python3 -m venv venv
sudo -u trading-bot venv/bin/pip install --upgrade pip
sudo -u trading-bot venv/bin/pip install -r requirements.txt

# Create directories
sudo -u trading-bot mkdir -p logs models data
```

### 4. Create Systemd Services

Create `/etc/systemd/system/trading-bot.service`:

```ini
[Unit]
Description=DDQN Trading Bot
After=network.target

[Service]
Type=simple
User=trading-bot
WorkingDirectory=/opt/trading-bot
Environment=PATH=/opt/trading-bot/venv/bin
ExecStart=/opt/trading-bot/venv/bin/python train_forever.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/trading-bot-web.service`:

```ini
[Unit]
Description=DDQN Trading Bot Web Server
After=network.target

[Service]
Type=simple
User=trading-bot
WorkingDirectory=/opt/trading-bot
Environment=PATH=/opt/trading-bot/venv/bin
ExecStart=/opt/trading-bot/venv/bin/gunicorn --bind 127.0.0.1:5000 trade_server:app
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### 5. Configure Nginx

Create `/etc/nginx/sites-available/trading-bot`:

```nginx
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /opt/trading-bot/static;
    }
}
```

Enable the site:

```bash
sudo ln -sf /etc/nginx/sites-available/trading-bot /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo systemctl restart nginx
```

### 6. Configure Firewall

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable
```

### 7. Start Services

```bash
sudo systemctl daemon-reload
sudo systemctl enable trading-bot
sudo systemctl enable trading-bot-web
sudo systemctl enable nginx

sudo systemctl start nginx
sudo systemctl start trading-bot-web
sudo systemctl start trading-bot
```

## Management Commands

The deployment script creates a management script at `/usr/local/bin/trading-bot-manage`:

```bash
# Start the bot
sudo trading-bot-manage start

# Stop the bot
sudo trading-bot-manage stop

# Restart the bot
sudo trading-bot-manage restart

# Check status
sudo trading-bot-manage status

# View logs
sudo trading-bot-manage logs

# View web server logs
sudo trading-bot-manage web-logs

# Update and restart
sudo trading-bot-manage update
```

## Monitoring

### Web Dashboard

Access the web dashboard at `http://your-server-ip` to monitor:
- Wallet balance
- Profit/loss
- Training status
- Model indicators
- Trade history

### Logs

View logs using systemd journal:

```bash
# Trading bot logs
sudo journalctl -u trading-bot -f

# Web server logs
sudo journalctl -u trading-bot-web -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Telegram Notifications

If configured, the bot will send notifications for:
- Trade executions
- Status updates
- Error alerts
- Profit milestones

## SSL Setup (Optional)

To enable HTTPS:

```bash
# Install Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## Troubleshooting

### Common Issues

1. **TA-Lib installation fails**
   ```bash
   # Install from source
   wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
   tar -xzf ta-lib-0.4.0-src.tar.gz
   cd ta-lib/
   ./configure --prefix=/usr
   make
   sudo make install
   ```

2. **Permission errors**
   ```bash
   sudo chown -R trading-bot:trading-bot /opt/trading-bot
   ```

3. **Service won't start**
   ```bash
   sudo systemctl status trading-bot
   sudo journalctl -u trading-bot -n 50
   ```

4. **Web dashboard not accessible**
   ```bash
   sudo systemctl status nginx
   sudo systemctl status trading-bot-web
   ```

### Performance Optimization

1. **Increase memory limit** (if needed):
   ```bash
   # Edit systemd service
   sudo nano /etc/systemd/system/trading-bot.service
   # Add: Environment=PYTHONUNBUFFERED=1
   ```

2. **Enable swap** (if low memory):
   ```bash
   sudo fallocate -l 2G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
   ```

## Security Considerations

1. **Firewall**: Only allow necessary ports (22, 80, 443)
2. **API Keys**: Store securely and rotate regularly
3. **Updates**: Keep system and dependencies updated
4. **Monitoring**: Set up log monitoring and alerts
5. **Backups**: Regular backups of configuration and models

## Backup and Recovery

### Backup Configuration

```bash
# Create backup
sudo tar -czf trading-bot-backup-$(date +%Y%m%d).tar.gz /opt/trading-bot/config.json /opt/trading-bot/models/

# Restore backup
sudo tar -xzf trading-bot-backup-YYYYMMDD.tar.gz -C /
```

### Model Backup

```bash
# Backup trained models
sudo cp /opt/trading-bot/best_model_default.weights.h5 /backup/

# Restore models
sudo cp /backup/best_model_default.weights.h5 /opt/trading-bot/
sudo chown trading-bot:trading-bot /opt/trading-bot/best_model_default.weights.h5
```

## Support

For issues and questions:
1. Check the logs: `sudo trading-bot-manage logs`
2. Verify configuration: `python3 -c "import json; json.load(open('config.json'))"`
3. Test API connection: Check Bybit API credentials
4. Monitor system resources: `htop`, `df -h`, `free -h`