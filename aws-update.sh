#!/bin/bash

# AWS EC2 Update Script for Greek News Analyzer
# This script updates an existing deployment with the latest version
# Usage: ./aws-update.sh [GEMINI_API_KEY]
# If no API key provided, it will keep the existing one

echo "🚀 Updating Greek News Analyzer on AWS EC2..."

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: Please run this script from the project directory"
    exit 1
fi

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "❌ Error: Please don't run this script as root"
    echo "Run as: ./aws-update.sh"
    exit 1
fi

# Determine the user (ec2-user for Amazon Linux, ubuntu for Ubuntu)
if id "ec2-user" &>/dev/null; then
    APP_USER="ec2-user"
    APP_DIR="/var/www/greek-news-analyzer"
elif id "ubuntu" &>/dev/null; then
    APP_USER="ubuntu"
    APP_DIR="/var/www/greek-news-analyzer"
else
    APP_USER=$(whoami)
    APP_DIR="/var/www/greek-news-analyzer"
fi

echo "👤 Using user: $APP_USER"
echo "📁 App directory: $APP_DIR"

# Check if app directory exists
if [ ! -d "$APP_DIR" ]; then
    echo "❌ Error: App directory $APP_DIR not found"
    echo "Please run the initial deployment script first"
    exit 1
fi

# Backup current .env file if it exists
if [ -f "$APP_DIR/.env" ]; then
    echo "💾 Backing up existing .env file..."
    cp "$APP_DIR/.env" "$APP_DIR/.env.backup.$(date +%Y%m%d_%H%M%S)"
    EXISTING_API_KEY=$(grep "GEMINI_API_KEY=" "$APP_DIR/.env" | cut -d'=' -f2)
    echo "🔑 Found existing API key"
else
    echo "⚠️  No existing .env file found"
    EXISTING_API_KEY=""
fi

# Use provided API key or existing one
if [ -n "$1" ]; then
    GEMINI_API_KEY="$1"
    echo "🔑 Using provided API key"
else
    if [ -n "$EXISTING_API_KEY" ]; then
        GEMINI_API_KEY="$EXISTING_API_KEY"
        echo "🔑 Using existing API key"
    else
        echo "❌ Error: No API key provided and no existing key found"
        echo "Usage: $0 [GEMINI_API_KEY]"
        echo "Example: $0 your_gemini_api_key_here"
        exit 1
    fi
fi

# Stop the service
echo "⏹️  Stopping Greek News Analyzer service..."
sudo systemctl stop greek-news-analyzer

# Navigate to app directory
cd "$APP_DIR"

# Pull latest changes
echo "📥 Pulling latest changes from repository..."
git fetch origin
git reset --hard origin/main

# Activate virtual environment
echo "🐍 Activating virtual environment..."
source venv/bin/activate

# Update dependencies
echo "📦 Updating Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install additional PWA dependencies
echo "📱 Installing PWA dependencies..."
pip install Pillow

# Generate PWA icons
echo "🎨 Generating PWA icons..."
python3 generate_icons.py

# Create/update .env file
echo "⚙️  Updating environment configuration..."
cat > .env << EOF
# Google Gemini API Configuration
GEMINI_API_KEY=$GEMINI_API_KEY

# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False

# Server Configuration
PORT=5000
HOST=0.0.0.0
EOF

# Update systemd service with improved configuration
echo "🔧 Updating systemd service configuration..."
sudo tee /etc/systemd/system/greek-news-analyzer.service > /dev/null << EOF
[Unit]
Description=Greek News Analyzer
After=network.target

[Service]
User=$APP_USER
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
Environment=FLASK_ENV=production
ExecStart=$APP_DIR/venv/bin/gunicorn --bind 127.0.0.1:5000 --workers 3 --timeout 120 --max-requests 1000 --max-requests-jitter 100 app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Update Nginx configuration with improved settings
echo "🌐 Updating Nginx configuration..."

# Create rate limiting configuration
echo "🔧 Creating rate limiting configuration..."
sudo tee /etc/nginx/conf.d/rate-limiting.conf > /dev/null << 'EOF'
# Rate limiting zones
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/m;
limit_req_zone $binary_remote_addr zone=general:10m rate=100r/h;
EOF

if [ -f "/etc/nginx/sites-available/greek-news-analyzer" ]; then
    # Ubuntu/Debian style
    sudo tee /etc/nginx/sites-available/greek-news-analyzer > /dev/null << EOF
server {
    listen 80;
    server_name _;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # PWA headers
    add_header Cache-Control "public, max-age=31536000" always;
    add_header Cross-Origin-Embedder-Policy "require-corp" always;
    add_header Cross-Origin-Opener-Policy "same-origin" always;

    location / {
        limit_req zone=general burst=20 nodelay;
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    location /analyze {
        limit_req zone=api burst=5 nodelay;
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # PWA static files
    location /static/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        add_header Cross-Origin-Embedder-Policy "require-corp";
        add_header Cross-Origin-Opener-Policy "same-origin";
    }

    # Service Worker
    location /static/sw.js {
        expires 0;
        add_header Cache-Control "no-cache, no-store, must-revalidate";
        add_header Cross-Origin-Embedder-Policy "require-corp";
        add_header Cross-Origin-Opener-Policy "same-origin";
    }

    # Manifest
    location /static/manifest.json {
        expires 1d;
        add_header Content-Type "application/manifest+json";
        add_header Cross-Origin-Embedder-Policy "require-corp";
        add_header Cross-Origin-Opener-Policy "same-origin";
    }
}
EOF
else
    # Amazon Linux style
    sudo tee /etc/nginx/conf.d/greek-news-analyzer.conf > /dev/null << EOF
server {
    listen 80;
    server_name _;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # PWA headers
    add_header Cache-Control "public, max-age=31536000" always;
    add_header Cross-Origin-Embedder-Policy "require-corp" always;
    add_header Cross-Origin-Opener-Policy "same-origin" always;

    location / {
        limit_req zone=general burst=20 nodelay;
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    location /analyze {
        limit_req zone=api burst=5 nodelay;
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # PWA static files
    location /static/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        add_header Cross-Origin-Embedder-Policy "require-corp";
        add_header Cross-Origin-Opener-Policy "same-origin";
    }

    # Service Worker
    location /static/sw.js {
        expires 0;
        add_header Cache-Control "no-cache, no-store, must-revalidate";
        add_header Cross-Origin-Embedder-Policy "require-corp";
        add_header Cross-Origin-Opener-Policy "same-origin";
    }

    # Manifest
    location /static/manifest.json {
        expires 1d;
        add_header Content-Type "application/manifest+json";
        add_header Cross-Origin-Embedder-Policy "require-corp";
        add_header Cross-Origin-Opener-Policy "same-origin";
    }
}
EOF
fi

# Test configurations
echo "🧪 Testing configurations..."
sudo nginx -t
if [ $? -ne 0 ]; then
    echo "❌ Nginx configuration test failed"
    exit 1
fi

# Reload systemd and restart services
echo "🔄 Reloading systemd and restarting services..."
sudo systemctl daemon-reload
sudo systemctl enable greek-news-analyzer
sudo systemctl start greek-news-analyzer
sudo systemctl restart nginx

# Wait a moment for services to start
sleep 5

# Check service status
echo "📊 Checking service status..."
if sudo systemctl is-active --quiet greek-news-analyzer; then
    echo "✅ Greek News Analyzer service is running"
else
    echo "❌ Greek News Analyzer service failed to start"
    echo "📝 Check logs: sudo journalctl -u greek-news-analyzer -f"
    exit 1
fi

if sudo systemctl is-active --quiet nginx; then
    echo "✅ Nginx service is running"
else
    echo "❌ Nginx service failed to start"
    echo "📝 Check logs: sudo systemctl status nginx"
    exit 1
fi

# Test the application
echo "🧪 Testing application endpoints..."
PUBLIC_IP=$(curl -s ifconfig.me)
if curl -s "http://localhost:5000/health" | grep -q "healthy"; then
    echo "✅ Health check passed"
else
    echo "⚠️  Health check failed - application may not be fully ready yet"
fi

# Display final information
echo ""
echo "🎉 Update completed successfully!"
echo "🌐 Your app is available at: http://$PUBLIC_IP"
echo "🏥 Health check: http://$PUBLIC_IP/health"
echo "📊 Status info: http://$PUBLIC_IP/status"
echo ""
echo "📋 Service management commands:"
echo "   Status: sudo systemctl status greek-news-analyzer"
echo "   Logs:   sudo journalctl -u greek-news-analyzer -f"
echo "   Restart: sudo systemctl restart greek-news-analyzer"
echo ""
echo "🔧 New features included:"
echo "   ✅ Rate limiting (5 requests/minute for analysis)"
echo "   ✅ Caching system for faster responses"
echo "   ✅ Enhanced error handling and logging"
echo "   ✅ Health and status monitoring endpoints"
echo "   ✅ Improved text extraction"
echo "   ✅ Security headers"
echo "   ✅ Progressive Web App (PWA) support"
echo "   ✅ Mobile app installation"
echo "   ✅ Deep linking for news URLs"
echo "   ✅ Share target integration"
echo "   ✅ Offline functionality"
echo ""
echo "💾 Backup created: $APP_DIR/.env.backup.*"
