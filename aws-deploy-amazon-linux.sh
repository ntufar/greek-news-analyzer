#!/bin/bash

# AWS EC2 Deployment Script for ΕΠΑΠ (Amazon Linux)
# Run this on your EC2 instance after initial setup
# Usage: ./aws-deploy-amazon-linux.sh <GEMINI_API_KEY>

# Check if API key is provided
if [ -z "$1" ]; then
    echo "❌ Error: Gemini API key is required"
    echo "Usage: $0 <GEMINI_API_KEY>"
    echo "Example: $0 your_gemini_api_key_here"
    exit 1
fi

GEMINI_API_KEY="$1"
echo "🚀 Setting up ΕΠΑΠ on AWS EC2 (Amazon Linux)..."

# Update system
sudo yum update -y

# Install development tools and git
sudo yum groupinstall -y "Development Tools"
sudo yum install -y git wget

# Install Python 3 (Amazon Linux 2023 has Python 3.9 by default)
sudo yum install -y python3 python3-pip python3-devel

# Install system dependencies
sudo yum install -y nginx

# Install supervisor via pip
sudo pip3 install supervisor

# Create application directory
sudo mkdir -p /var/www/epap
sudo chown ec2-user:ec2-user /var/www/epap
cd /var/www/epap

# Clone repository
git clone https://github.com/ntufar/epap.git .

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
sudo tee /etc/systemd/system/epap.service > /dev/null << EOF
[Unit]
Description=ΕΠΑΠ
After=network.target

[Service]
User=ec2-user
WorkingDirectory=/var/www/epap
Environment=PATH=/var/www/epap/venv/bin
ExecStart=/var/www/epap/venv/bin/gunicorn --bind 127.0.0.1:5000 --workers 2 --timeout 120 app:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Configure Nginx
sudo tee /etc/nginx/conf.d/epap.conf > /dev/null << EOF
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
sudo systemctl enable epap
sudo systemctl start epap
sudo systemctl enable nginx
sudo systemctl start nginx

echo "✅ Setup complete!"
echo "🌐 Your app should be available at: http://$(curl -s ifconfig.me)"
echo "📊 Check status: sudo systemctl status epap"
echo "📝 View logs: sudo journalctl -u epap -f"