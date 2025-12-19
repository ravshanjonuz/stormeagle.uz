#!/bin/bash
# Storm Eagle Deployment Script
# Run this on the server after SSH login

set -e

echo "=== Storm Eagle Deployment ==="

# Clone or pull repository
if [ -d "/var/www/stormeagle" ]; then
    echo "Updating existing installation..."
    cd /var/www/stormeagle
    git pull origin main
else
    echo "Cloning repository..."
    cd /var/www
    git clone https://github.com/ravshanjonuz/stormeagle.uz.git stormeagle
    cd /var/www/stormeagle
fi

# Create virtual environment
echo "Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Run migration for profile_image column
echo "Running database migration..."
python migrate_profile_image.py || echo "Migration may already exist"

echo "=== Deployment complete! ==="
echo "Now run the app in tmux:"
echo "  tmux new -s strom"
echo "  cd /var/www/stormeagle && source venv/bin/activate"
echo "  uvicorn main:app --host 127.0.0.1 --port 8000"
