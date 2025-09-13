#!/bin/bash

# Simple AWS EC2 Deployment Script for Greek News Analyzer (Amazon Linux)
# This script uses the system Python and avoids package conflicts
# Usage: ./aws-deploy-simple.sh <GEMINI_API_KEY>

# Check if API key is provided
if [ -z "$1" ]; then
    echo "❌ Error: Gemini API key is required"
    echo "Usage: $0 <GEMINI_API_KEY>"
    echo "Example: $0 your_gemini_api_key_here"
    exit 1
fi

GEMINI_API_KEY="$1"
echo "🚀 Setting up Greek News Analyzer on AWS EC2 (Amazon Linux)..."

# Update system
sudo yum update -y

# Install basic dependencies
sudo yum install -y git python3 python3-pip python3-devel nginx

# Create application directory
sudo mkdir -p /var/www/greek-news-analyzer
sudo chown ec2-user:ec2-user /var/www/greek-news-analyzer
cd /var/www/greek-news-analyzer

# Clone repository (remove existing if present)
if [ -d ".git" ]; then
    echo "Repository already exists. Pulling latest changes..."
    git pull origin main
else
    echo "Cloning repository..."
    git clone https://github.com/ntufar/greek-news-analyzer.git .
fi

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
User=ec2-user
WorkingDirectory=/var/www/greek-news-analyzer
Environment=PATH=/var/www/greek-news-analyzer/venv/bin
ExecStart=/var/www/greek-news-analyzer/venv/bin/gunicorn --bind 127.0.0.1:5000 --workers 2 --timeout 120 app:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Configure Nginx
sudo tee /etc/nginx/conf.d/greek-news-analyzer.conf > /dev/null << EOF
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

# Remove default nginx config
sudo rm -f /etc/nginx/conf.d/default.conf

# Test nginx configuration
sudo nginx -t

# Start services
sudo systemctl daemon-reload
sudo systemctl enable greek-news-analyzer
sudo systemctl start greek-news-analyzer
sudo systemctl enable nginx
sudo systemctl start nginx

echo "✅ Setup complete!"
echo "🌐 Your app should be available at: http://$(curl -s ifconfig.me)"
echo "📊 Check status: sudo systemctl status greek-news-analyzer"
echo "📝 View logs: sudo journalctl -u greek-news-analyzer -f"