#!/bin/bash

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo "Please do not run as root"
    exit 1
fi

# Check Python version
python3 --version >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Python 3 is not installed. Installing..."
    sudo apt-get update
    sudo apt-get install -y python3
fi

# Update system
echo "Updating system..."
sudo apt-get update
sudo apt-get upgrade -y

# Install required system packages
echo "Installing required system packages..."
sudo apt-get install -y python3-pip python3-opencv python3-dev python3-setuptools python3-wheel build-essential

# Install numpy first (it's a dependency for other packages)
echo "Installing numpy..."
python3 -m pip install --no-cache-dir numpy

# Install other Python dependencies
echo "Installing other Python dependencies..."
python3 -m pip install --no-cache-dir -r camera_requirements.txt

# Get current user
CURRENT_USER=$(whoami)

# Setup systemd service
echo "Setting up automatic startup..."
sudo tee /etc/systemd/system/camera-app.service << EOF
[Unit]
Description=Camera Application
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$(pwd)
ExecStart=/usr/bin/python3 $(pwd)/camera_app.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable camera-app

# Add user to video group for camera access
echo "Setting up camera permissions..."
sudo usermod -a -G video $CURRENT_USER

echo "Installation complete!"
echo "The application will start automatically after reboot."
echo "To start manually, run: python3 camera_app.py"
echo ""
echo "Manual controls:"
echo "- Start: sudo systemctl start camera-app"
echo "- Stop: sudo systemctl stop camera-app"
echo "- Status: sudo systemctl status camera-app"
echo "- Logs: sudo journalctl -u camera-app -f" 