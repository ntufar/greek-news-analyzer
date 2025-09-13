#!/bin/bash

# AWS EC2 Deployment Script for Greek News Analyzer
# Run this on your EC2 instance after initial setup
# Usage: ./aws-deploy.sh <GEMINI_API_KEY>

# Check if API key is provided
if [ -z "$1" ]; then
    echo "❌ Error: Gemini API key is required"
    echo "Usage: $0 <GEMINI_API_KEY>"
    echo "Example: $0 your_gemini_api_key_here"
    exit 1
fi

GEMINI_API_KEY="$1"
echo "🚀 Setting up Greek News Analyzer on AWS EC2..."

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3
sudo apt install -y python3 python3-venv python3-dev python3-pip

# Install system dependencies
sudo apt install -y nginx supervisor git curl

# Create application directory
sudo mkdir -p /var/www/greek-news-analyzer
sudo chown $USER:$USER /var/www/greek-news-analyzer
cd /var/www/greek-news-analyzer

# Clone repository
git clone https://github.com/ntufar/greek-news-analyzer.git .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with the provided API key
cat > .env << EOF
GEMINI_API_KEY=$GEMINI_API_KEY
FLASK_ENV=production
FLASK_DEBUG=False
EOF

echo "✅ Environment file created with provided API key"

# Create systemd service
sudo tee /etc/systemd/system/greek-news-analyzer.service > /dev/null << EOF
[Unit]
Description=Greek News Analyzer
After=network.target

[Service]
User=$USER
WorkingDirectory=/var/www/greek-news-analyzer
Environment=PATH=/var/www/greek-news-analyzer/venv/bin
ExecStart=/var/www/greek-news-analyzer/venv/bin/gunicorn --bind 127.0.0.1:5000 --workers 2 --timeout 120 app:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Configure Nginx
sudo tee /etc/nginx/sites-available/greek-news-analyzer > /dev/null << EOF
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
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/greek-news-analyzer /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# Test nginx configuration
sudo nginx -t

# Start services
sudo systemctl daemon-reload
sudo systemctl enable greek-news-analyzer
sudo systemctl start greek-news-analyzer
sudo systemctl restart nginx

echo "✅ Setup complete!"
echo "🌐 Your app should be available at: http://$(curl -s ifconfig.me)"
echo "📊 Check status: sudo systemctl status greek-news-analyzer"
echo "📝 View logs: sudo journalctl -u greek-news-analyzer -f"