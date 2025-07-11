#!/bin/bash

echo "🚀 Deploying Trading Bot to V Server..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run as root (use sudo)"
    exit 1
fi

# Update system
echo "📦 Updating system packages..."
apt-get update
apt-get upgrade -y

# Install required system packages
echo "📚 Installing system dependencies..."
apt-get install -y python3 python3-pip python3-venv
apt-get install -y build-essential wget curl
apt-get install -y libta-lib0 libta-lib-dev
apt-get install -y nginx supervisor
apt-get install -y git

# Create application directory
APP_DIR="/opt/trading-bot"
echo "📁 Creating application directory: $APP_DIR"
mkdir -p $APP_DIR
cd $APP_DIR

# Copy application files
echo "📋 Copying application files..."
cp -r /workspace/* $APP_DIR/

# Set permissions
echo "🔐 Setting permissions..."
chown -R ubuntu:ubuntu $APP_DIR
chmod +x $APP_DIR/*.sh

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
sudo -u ubuntu python3 -m venv $APP_DIR/venv

# Install Python dependencies
echo "📦 Installing Python dependencies..."
sudo -u ubuntu $APP_DIR/venv/bin/pip install --upgrade pip
sudo -u ubuntu $APP_DIR/venv/bin/pip install -r $APP_DIR/requirements.txt

# Create necessary directories
echo "📁 Creating application directories..."
sudo -u ubuntu mkdir -p $APP_DIR/logs
sudo -u ubuntu mkdir -p $APP_DIR/models
sudo -u ubuntu mkdir -p $APP_DIR/data
sudo -u ubuntu mkdir -p $APP_DIR/backups

# Setup systemd service
echo "⚙️ Setting up systemd service..."
cp $APP_DIR/systemd/trading-bot.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable trading-bot.service

# Setup Nginx
echo "🌐 Setting up Nginx..."
cat > /etc/nginx/sites-available/trading-bot << EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static {
        alias $APP_DIR/static;
    }
}
EOF

# Enable Nginx site
ln -sf /etc/nginx/sites-available/trading-bot /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
nginx -t
if [ $? -eq 0 ]; then
    systemctl restart nginx
    systemctl enable nginx
else
    echo "❌ Nginx configuration test failed"
    exit 1
fi

# Setup firewall
echo "🔥 Setting up firewall..."
ufw allow ssh
ufw allow 80
ufw allow 443
ufw --force enable

# Create startup script
echo "📝 Creating startup script..."
cat > $APP_DIR/start.sh << 'EOF'
#!/bin/bash
cd /opt/trading-bot
source venv/bin/activate

# Start the trading bot
python train_forever.py &
BOT_PID=$!

# Start the web server
python trade_server.py &
SERVER_PID=$!

echo "Trading bot started with PID: $BOT_PID"
echo "Web server started with PID: $SERVER_PID"

# Wait for processes
wait $BOT_PID $SERVER_PID
EOF

chmod +x $APP_DIR/start.sh

# Create monitoring script
echo "📊 Creating monitoring script..."
cat > $APP_DIR/monitor.sh << 'EOF'
#!/bin/bash
cd /opt/trading-bot

echo "=== Trading Bot Status ==="
if systemctl is-active --quiet trading-bot; then
    echo "✅ Trading bot service is running"
else
    echo "❌ Trading bot service is not running"
fi

echo ""
echo "=== Web Server Status ==="
if curl -s http://localhost:5000/api/profit_loss > /dev/null; then
    echo "✅ Web server is responding"
else
    echo "❌ Web server is not responding"
fi

echo ""
echo "=== Recent Logs ==="
tail -n 10 logs/trading_bot.log

echo ""
echo "=== System Resources ==="
echo "CPU Usage: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"
echo "Memory Usage: $(free | grep Mem | awk '{printf("%.1f%%", $3/$2 * 100.0)}')"
echo "Disk Usage: $(df -h / | awk 'NR==2 {print $5}')"
EOF

chmod +x $APP_DIR/monitor.sh

# Create backup script
echo "💾 Creating backup script..."
cat > $APP_DIR/backup.sh << 'EOF'
#!/bin/bash
cd /opt/trading-bot

BACKUP_DIR="backups/backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

# Backup important files
cp config.json $BACKUP_DIR/
cp -r models $BACKUP_DIR/
cp -r data $BACKUP_DIR/
cp *.csv $BACKUP_DIR/ 2>/dev/null || true
cp *.json $BACKUP_DIR/ 2>/dev/null || true

echo "Backup created in: $BACKUP_DIR"
EOF

chmod +x $APP_DIR/backup.sh

# Setup log rotation
echo "📋 Setting up log rotation..."
cat > /etc/logrotate.d/trading-bot << EOF
$APP_DIR/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 ubuntu ubuntu
    postrotate
        systemctl reload trading-bot
    endscript
}
EOF

echo "✅ Deployment completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Edit $APP_DIR/config.json with your API keys"
echo "2. Start the service: systemctl start trading-bot"
echo "3. Check status: systemctl status trading-bot"
echo "4. Monitor: $APP_DIR/monitor.sh"
echo "5. Access web dashboard: http://your-server-ip"
echo ""
echo "🔧 Useful commands:"
echo "  - Start service: systemctl start trading-bot"
echo "  - Stop service: systemctl stop trading-bot"
echo "  - Restart service: systemctl restart trading-bot"
echo "  - View logs: journalctl -u trading-bot -f"
echo "  - Monitor: $APP_DIR/monitor.sh"
echo "  - Backup: $APP_DIR/backup.sh"