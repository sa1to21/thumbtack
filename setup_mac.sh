#!/bin/bash
# Setup script for Mac installation

set -e

echo "🚀 Setting up Thumbtack Auto-Responder on Mac..."
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    echo "Please install Python 3 from https://www.python.org/downloads/"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed"
    echo "Installing pip..."
    python3 -m ensurepip --upgrade
fi

echo "✅ pip3 found"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "1. Copy .env.example to .env and fill in your credentials:"
echo "   cp .env.example .env"
echo "   nano .env"
echo ""
echo "2. Run the bot manually first time to login to Thumbtack:"
echo "   source venv/bin/activate"
echo "   python main.py"
echo ""
echo "3. After successful login, setup autostart:"
echo "   ./install_service_mac.sh"
