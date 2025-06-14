#!/bin/bash

# Raspberry Pi Camera Fix Script
# Automatically configures camera settings

echo "Raspberry Pi Camera Configuration Fix Script"
echo "============================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "This script needs to be run with sudo privileges"
    echo "Usage: sudo bash fix_camera.sh"
    exit 1
fi

# Backup original config
echo "Creating backup of /boot/config.txt..."
cp /boot/config.txt /boot/config.txt.backup.$(date +%Y%m%d_%H%M%S)

# Enable camera interface using raspi-config
echo "Enabling camera interface..."
raspi-config nonint do_camera 0

# Check and modify /boot/config.txt
echo "Configuring /boot/config.txt..."

CONFIG_FILE="/boot/config.txt"

# Function to add or update config line
add_or_update_config() {
    local key=$1
    local value=$2
    local file=$3
    
    if grep -q "^${key}=" "$file"; then
        # Update existing line
        sed -i "s/^${key}=.*/${key}=${value}/" "$file"
        echo "Updated: ${key}=${value}"
    elif grep -q "^#${key}=" "$file"; then
        # Uncomment and update
        sed -i "s/^#${key}=.*/${key}=${value}/" "$file"
        echo "Uncommented and updated: ${key}=${value}"
    else
        # Add new line
        echo "${key}=${value}" >> "$file"
        echo "Added: ${key}=${value}"
    fi
}

# Configure camera settings
echo "Setting camera configuration..."
add_or_update_config "start_x" "1" "$CONFIG_FILE"
add_or_update_config "gpu_mem" "128" "$CONFIG_FILE"
add_or_update_config "camera_auto_detect" "1" "$CONFIG_FILE"

# For older Pi models, ensure legacy camera support
if grep -q "Pi 3" /proc/cpuinfo || grep -q "Pi 2" /proc/cpuinfo || grep -q "Pi 1" /proc/cpuinfo; then
    echo "Detected older Pi model, adding legacy camera support..."
    add_or_update_config "disable_camera_led" "1" "$CONFIG_FILE"
fi

# Install required packages
echo "Installing required packages..."
apt update
apt install -y python3-picamera2 python3-opencv v4l-utils

# Load camera modules
echo "Loading camera modules..."
modprobe bcm2835-v4l2

# Add module to load at boot
if ! grep -q "bcm2835-v4l2" /etc/modules; then
    echo "bcm2835-v4l2" >> /etc/modules
    echo "Added bcm2835-v4l2 to /etc/modules"
fi

# Set permissions for camera devices
echo "Setting camera device permissions..."
if [ -e /dev/video0 ]; then
    chmod 666 /dev/video0
fi

# Create udev rule for camera permissions
cat > /etc/udev/rules.d/99-camera.rules << EOF
SUBSYSTEM=="video4linux", GROUP="video", MODE="0664"
KERNEL=="video[0-9]*", GROUP="video", MODE="0664"
EOF

# Add user to video group
if [ -n "$SUDO_USER" ]; then
    usermod -a -G video "$SUDO_USER"
    echo "Added $SUDO_USER to video group"
fi

echo ""
echo "Configuration complete!"
echo "======================"
echo ""
echo "Changes made:"
echo "- Enabled camera interface"
echo "- Set start_x=1 (enable camera)"
echo "- Set gpu_mem=128 (allocate GPU memory)"
echo "- Set camera_auto_detect=1 (auto-detect camera)"
echo "- Installed python3-picamera2 and python3-opencv"
echo "- Added bcm2835-v4l2 module to load at boot"
echo "- Set camera device permissions"
echo "- Added user to video group"
echo ""
echo "IMPORTANT: You must reboot for changes to take effect!"
echo "Run: sudo reboot"
echo ""
echo "After reboot, test with:"
echo "- python3 camera_debug.py"
echo "- libcamera-hello --list-cameras"
echo "- libcamera-still -o test.jpg" 