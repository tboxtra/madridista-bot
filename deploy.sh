#!/bin/bash

# MadridistaAI Bot Deployment Script
# Run this on your VPS after cloning the repository

set -e  # Exit on any error

echo "🚀 MadridistaAI Bot Deployment Script"
echo "======================================"

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "❌ This script should not be run as root"
   echo "Please run as a regular user (e.g., ubuntu)"
   exit 1
fi

# Get current directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

echo "📁 Working directory: $SCRIPT_DIR"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    if [ -f "env.example" ]; then
        cp env.example .env
        echo "✅ Created .env from template"
        echo "⚠️  Please edit .env with your real tokens before continuing"
        echo "   nano .env"
        read -p "Press Enter after editing .env file..."
    else
        echo "❌ env.example not found. Please create .env manually"
        exit 1
    fi
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Dependencies installed"

# Test the bot
echo "🧪 Testing bot setup..."
python3 test_telegram.py
if [ $? -eq 0 ]; then
    echo "✅ Bot test passed"
else
    echo "❌ Bot test failed. Please check your configuration"
    exit 1
fi

# Set up systemd service
echo "⚙️  Setting up systemd service..."

# Get current user
CURRENT_USER=$(whoami)
echo "👤 Current user: $CURRENT_USER"

# Update service file with current user and paths
sed -i "s|User=ubuntu|User=$CURRENT_USER|g" madridista-bot.service
sed -i "s|WorkingDirectory=/home/ubuntu/madridista-bot|WorkingDirectory=$SCRIPT_DIR|g" madridista-bot.service
sed -i "s|Environment=PATH=/home/ubuntu/madridista-bot/venv/bin|Environment=PATH=$SCRIPT_DIR/venv/bin|g" madridista-bot.service
sed -i "s|ExecStart=/home/ubuntu/madridista-bot/venv/bin/python3|ExecStart=$SCRIPT_DIR/venv/bin/python3|g" madridista-bot.service

# Copy service file to systemd
sudo cp madridista-bot.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable madridista-bot

echo "✅ Systemd service configured"

# Start the service
echo "🚀 Starting MadridistaAI bot service..."
sudo systemctl start madridista-bot

# Check status
echo "📊 Service status:"
sudo systemctl status madridista-bot --no-pager -l

echo ""
echo "🎉 Deployment complete!"
echo ""
echo "📋 Useful commands:"
echo "   View logs:     sudo journalctl -u madridista-bot -f"
echo "   Restart bot:   sudo systemctl restart madridista-bot"
echo "   Stop bot:      sudo systemctl stop madridista-bot"
echo "   Check status:  sudo systemctl status madridista-bot"
echo ""
echo "🤖 Your MadridistaAI bot should now be running 24/7!"
echo "   Test it by messaging your bot on Telegram"
echo ""
echo "¡Hala Madrid! 🤍⚽"
