#!/bin/bash

echo "🚀 Deploying DDQN Trading Bot to V Server..."

# Configuration
APP_NAME="trading-bot"
APP_DIR="/opt/$APP_NAME"
SERVICE_USER="trading-bot"
NGINX_SITE="/etc/nginx/sites-available/$APP_NAME"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run as root (use sudo)"
    exit 1
fi

# Update system
print_status "Updating system packages..."
apt-get update
apt-get upgrade -y

# Install required system packages
print_status "Installing system dependencies..."
apt-get install -y python3 python3-pip python3-venv nginx supervisor git curl wget build-essential

# Install TA-Lib dependencies
print_status "Installing TA-Lib dependencies..."
apt-get install -y libta-lib-dev

# Create application user
print_status "Creating application user..."
if ! id "$SERVICE_USER" &>/dev/null; then
    useradd -r -s /bin/bash -d $APP_DIR $SERVICE_USER
fi

# Create application directory
print_status "Creating application directory..."
mkdir -p $APP_DIR
chown $SERVICE_USER:$SERVICE_USER $APP_DIR

# Copy application files
print_status "Copying application files..."
cp -r . $APP_DIR/
chown -R $SERVICE_USER:$SERVICE_USER $APP_DIR

# Switch to application directory
cd $APP_DIR

# Create virtual environment
print_status "Setting up Python virtual environment..."
sudo -u $SERVICE_USER python3 -m venv venv
sudo -u $SERVICE_USER $APP_DIR/venv/bin/pip install --upgrade pip

# Install Python dependencies
print_status "Installing Python dependencies..."
sudo -u $SERVICE_USER $APP_DIR/venv/bin/pip install -r requirements.txt

# Create necessary directories
print_status "Creating application directories..."
sudo -u $SERVICE_USER mkdir -p logs models data

# Create systemd service file
print_status "Creating systemd service..."
cat > /etc/systemd/system/$APP_NAME.service << EOF
[Unit]
Description=DDQN Trading Bot
After=network.target

[Service]
Type=simple
User=$SERVICE_USER
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
ExecStart=$APP_DIR/venv/bin/python train_forever.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Create systemd service for web server
print_status "Creating web server systemd service..."
cat > /etc/systemd/system/$APP_NAME-web.service << EOF
[Unit]
Description=DDQN Trading Bot Web Server
After=network.target

[Service]
Type=simple
User=$SERVICE_USER
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
ExecStart=$APP_DIR/venv/bin/gunicorn --bind 127.0.0.1:5000 trade_server:app
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Create nginx configuration
print_status "Creating nginx configuration..."
cat > $NGINX_SITE << EOF
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

# Enable nginx site
print_status "Enabling nginx site..."
ln -sf $NGINX_SITE /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Configure firewall
print_status "Configuring firewall..."
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# Set up SSL with Let's Encrypt (optional)
read -p "Do you want to set up SSL with Let's Encrypt? (y/n): " setup_ssl
if [[ $setup_ssl =~ ^[Yy]$ ]]; then
    print_status "Installing Certbot..."
    apt-get install -y certbot python3-certbot-nginx
    
    read -p "Enter your domain name: " domain_name
    if [ ! -z "$domain_name" ]; then
        print_status "Setting up SSL for $domain_name..."
        sed -i "s/server_name _;/server_name $domain_name;/" $NGINX_SITE
        certbot --nginx -d $domain_name --non-interactive --agree-tos --email admin@$domain_name
    fi
fi

# Reload systemd and start services
print_status "Starting services..."
systemctl daemon-reload
systemctl enable $APP_NAME
systemctl enable $APP_NAME-web
systemctl enable nginx

# Start services
systemctl start nginx
systemctl start $APP_NAME-web

# Wait a moment before starting the main bot
sleep 5
systemctl start $APP_NAME

# Check service status
print_status "Checking service status..."
systemctl status $APP_NAME --no-pager
systemctl status $APP_NAME-web --no-pager
systemctl status nginx --no-pager

# Create management script
print_status "Creating management script..."
cat > /usr/local/bin/$APP_NAME-manage << EOF
#!/bin/bash

case "\$1" in
    start)
        systemctl start $APP_NAME
        systemctl start $APP_NAME-web
        echo "Trading bot started"
        ;;
    stop)
        systemctl stop $APP_NAME
        systemctl stop $APP_NAME-web
        echo "Trading bot stopped"
        ;;
    restart)
        systemctl restart $APP_NAME
        systemctl restart $APP_NAME-web
        echo "Trading bot restarted"
        ;;
    status)
        systemctl status $APP_NAME --no-pager
        systemctl status $APP_NAME-web --no-pager
        ;;
    logs)
        journalctl -u $APP_NAME -f
        ;;
    web-logs)
        journalctl -u $APP_NAME-web -f
        ;;
    update)
        cd $APP_DIR
        git pull
        sudo -u $SERVICE_USER $APP_DIR/venv/bin/pip install -r requirements.txt
        systemctl restart $APP_NAME
        systemctl restart $APP_NAME-web
        echo "Trading bot updated and restarted"
        ;;
    *)
        echo "Usage: \$0 {start|stop|restart|status|logs|web-logs|update}"
        exit 1
        ;;
esac
EOF

chmod +x /usr/local/bin/$APP_NAME-manage

# Create configuration template
print_status "Creating configuration template..."
if [ ! -f "$APP_DIR/config.json" ]; then
    cp config.json $APP_DIR/config.json
    chown $SERVICE_USER:$SERVICE_USER $APP_DIR/config.json
    print_warning "Please configure your API keys in $APP_DIR/config.json"
fi

print_status "Deployment completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Configure your API keys in $APP_DIR/config.json"
echo "2. Start the bot: $APP_NAME-manage start"
echo "3. Check status: $APP_NAME-manage status"
echo "4. View logs: $APP_NAME-manage logs"
echo "5. Access web dashboard: http://your-server-ip"
echo ""
echo "🔧 Management commands:"
echo "  $APP_NAME-manage start    - Start the bot"
echo "  $APP_NAME-manage stop     - Stop the bot"
echo "  $APP_NAME-manage restart  - Restart the bot"
echo "  $APP_NAME-manage status   - Check status"
echo "  $APP_NAME-manage logs     - View logs"
echo "  $APP_NAME-manage update   - Update and restart"