#!/bin/bash

echo "🚀 Deploying DDQN Trading Bot to V Server..."

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "❌ Please don't run this script as root. Use a regular user with sudo privileges."
    exit 1
fi

# Update system packages
echo "📦 Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install required system packages
echo "📚 Installing system dependencies..."
sudo apt-get install -y python3 python3-pip python3-venv
sudo apt-get install -y build-essential wget curl
sudo apt-get install -y libta-lib0 libta-lib-dev
sudo apt-get install -y nginx supervisor

# Create application directory
echo "📁 Setting up application directory..."
sudo mkdir -p /opt/trading-bot
sudo chown $USER:$USER /opt/trading-bot

# Copy application files
echo "📋 Copying application files..."
cp -r * /opt/trading-bot/
cd /opt/trading-bot

# Create virtual environment
echo "🔧 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p data
mkdir -p models

# Set up Nginx configuration
echo "🌐 Setting up Nginx..."
sudo tee /etc/nginx/sites-available/trading-bot << EOF
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
        alias /opt/trading-bot/static;
    }
}
EOF

# Enable Nginx site
sudo ln -sf /etc/nginx/sites-available/trading-bot /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx

# Set up systemd service
echo "⚙️ Setting up systemd service..."
sudo cp systemd.service /etc/systemd/system/trading-bot.service
sudo systemctl daemon-reload
sudo systemctl enable trading-bot

# Set up supervisor for process management
echo "👨‍💼 Setting up supervisor..."
sudo tee /etc/supervisor/conf.d/trading-bot.conf << EOF
[program:trading-bot]
command=/opt/trading-bot/venv/bin/python /opt/trading-bot/trade_server.py
directory=/opt/trading-bot
user=$USER
autostart=true
autorestart=true
stderr_logfile=/opt/trading-bot/logs/supervisor_err.log
stdout_logfile=/opt/trading-bot/logs/supervisor_out.log
environment=PATH="/opt/trading-bot/venv/bin"
EOF

sudo systemctl enable supervisor
sudo systemctl start supervisor
sudo supervisorctl reread
sudo supervisorctl update

# Set up firewall
echo "🔥 Setting up firewall..."
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

# Create startup script
echo "📜 Creating startup script..."
tee /opt/trading-bot/start.sh << EOF
#!/bin/bash
cd /opt/trading-bot
source venv/bin/activate
python trade_server.py
EOF

chmod +x /opt/trading-bot/start.sh

# Set proper permissions
echo "🔐 Setting permissions..."
chmod +x /opt/trading-bot/*.sh
chmod 644 /opt/trading-bot/*.py
chmod 644 /opt/trading-bot/*.json

# Create environment file template
echo "📄 Creating environment template..."
tee /opt/trading-bot/.env.template << EOF
# Copy this file to .env and fill in your actual values
BYBIT_API_KEY=your_bybit_api_key_here
BYBIT_API_SECRET=your_bybit_api_secret_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here
EOF

echo "✅ Deployment completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Edit /opt/trading-bot/config.json with your API keys"
echo "2. Copy .env.template to .env and fill in your credentials"
echo "3. Start the service: sudo systemctl start trading-bot"
echo "4. Check status: sudo systemctl status trading-bot"
echo "5. View logs: sudo journalctl -u trading-bot -f"
echo ""
echo "🌐 The web dashboard will be available at: http://your-server-ip"
echo "📊 API endpoints available at: http://your-server-ip/api/"
echo ""
echo "🔑 Don't forget to set your Bybit API keys and Telegram bot credentials!"