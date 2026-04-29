#!/bin/bash
# Bash Setup Script for Telegram Automation Bot
# Run this script to create the project structure and install dependencies

echo "========================================"
echo "Telegram Automation Bot - Setup Script"
echo "========================================"
echo ""

# Check if Python is installed
echo "Checking Python installation..."
python3 --version
if [ $? -ne 0 ]; then
    echo "Python 3 is not installed or not in PATH"
    exit 1
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "Failed to create virtual environment"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
python -m pip install --upgrade pip

# Install requirements
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Failed to install dependencies"
    exit 1
fi

# Create .env file if it doesn't exist
echo ""
echo "Checking environment configuration..."
if [ ! -f ".env" ]; then
    echo ".env file not found, creating from template..."
    cp .env.example .env
    echo ".env file created. Please update with your credentials."
else
    echo ".env file already exists"
fi

# Create logs directory if it doesn't exist
if [ ! -d "logs" ]; then
    mkdir -p logs
    echo "Created logs directory"
fi

echo ""
echo "========================================"
echo "Setup completed successfully!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your credentials"
echo "2. Run: python main.py"
echo "3. For tests: pytest"
