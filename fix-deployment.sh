#!/bin/bash

# Quick fix script for deployment issues
# Usage: ./fix-deployment.sh <GEMINI_API_KEY>

# Check if API key is provided
if [ -z "$1" ]; then
    echo "❌ Error: Gemini API key is required"
    echo "Usage: $0 <GEMINI_API_KEY>"
    echo "Example: $0 your_gemini_api_key_here"
    exit 1
fi

GEMINI_API_KEY="$1"
echo "🔧 Fixing deployment issues..."

# Navigate to the application directory
cd /var/www/epap

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found. Let's fix this..."
    
    # Remove everything and start fresh
    cd /var/www
    sudo rm -rf epap
    sudo mkdir -p epap
    sudo chown ec2-user:ec2-user epap
    cd epap
    
    # Clone the repository properly
    git clone https://github.com/ntufar/epap.git .
    
    echo "✅ Repository cloned successfully"
fi

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Create .env file with the provided API key
cat > .env << EOF
GEMINI_API_KEY=$GEMINI_API_KEY
FLASK_ENV=production
FLASK_DEBUG=False
EOF

echo "✅ Fixed! Environment file created with provided API key"
echo "Now run: sudo systemctl start epap"
