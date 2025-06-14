# Raspberry Pi Camera Application

A full-featured camera application for Raspberry Pi that supports both USB cameras and the Raspberry Pi Camera Module.

## Features

- Support for both USB cameras and Raspberry Pi Camera Module
- Compatible with Raspberry Pi 2 and newer models
- Full screen camera display
- Save images with spacebar (Image+datetime.jpg)
- Record video with 'v' key toggle
- Red recording indicator
- Auto camera detection
- Status display with FPS counter
- Configurable settings
- Automatic startup on boot

## Quick Installation

1. Clone the repository:
```bash
git clone https://github.com/miuraTakashi/camera_app_RasPi.git
cd camera_app_RasPi
```

2. Run the installation script:
```bash
chmod +x install.sh
./install.sh
```

3. Reboot your Raspberry Pi:
```bash
sudo reboot
```

The application will start automatically after reboot (if auto-startup was selected during installation).

## Application Files

This repository contains separate applications for different camera types to avoid compatibility issues:

- **`camera_launcher.py`** - Main launcher that detects available cameras and starts the appropriate application
- **`pi_camera_app.py`** - Dedicated application for Raspberry Pi Camera Module
- **`usb_camera_app.py`** - Dedicated application for USB cameras

## Manual Installation

1. Install Python dependencies:
```bash
pip3 install -r camera_requirements.txt
```

2. Run the appropriate application:
```bash
# Use the launcher to auto-detect and select camera
python3 camera_launcher.py

# Or run specific applications directly:
python3 pi_camera_app.py      # For Pi Camera Module
python3 usb_camera_app.py     # For USB cameras
python3 usb_camera_app.py 1   # For USB camera at index 1
```

## Camera Support

The application automatically detects and supports:
- USB cameras (plug and play)
- Raspberry Pi Camera Module (via picamera library)

## File Locations

Images and videos are saved in your user's home directory:
- Images: `~/Pictures/`
- Videos: `~/Movies/`

## Controls

- Spacebar: Save image
- 'v' key: Toggle video recording
- 'q' key: Quit application

## Configuration

The application uses a configuration file (`camera_config.json`) for settings:
- Camera resolution and FPS
- Video codec and quality
- Save paths
- Display options

## Troubleshooting

### Raspberry Pi Camera Module Not Detected

If your Raspberry Pi camera module is not being recognized, follow these steps:

#### 1. Quick Diagnosis
Run the camera debug script to check your system configuration:
```bash
python3 camera_debug.py
```

#### 2. Automatic Fix
Use the automatic fix script to configure camera settings:
```bash
sudo bash fix_camera.sh
sudo reboot
```

#### 3. Manual Configuration

**Enable Camera Interface:**
```bash
sudo raspi-config
# Navigate to: Interface Options → Camera → Enable
```

**Check/Edit Boot Configuration:**
```bash
sudo nano /boot/config.txt
```

Add or ensure these lines are present and uncommented:
```
start_x=1
gpu_mem=128
camera_auto_detect=1
```

**Reboot after changes:**
```bash
sudo reboot
```

#### 4. Test Camera Detection

After reboot, test camera detection:
```bash
# Check camera status
vcgencmd get_camera

# List available cameras (newer method)
libcamera-hello --list-cameras

# Take a test photo
libcamera-still -o test.jpg

# For older systems
raspistill -o test.jpg
```

#### 5. Hardware Check

- Ensure the camera ribbon cable is properly connected
- Check cable orientation (blue side should face the board)
- Try a different camera module if available
- Verify the camera connector is not damaged

### General Camera Issues

If any camera doesn't work:
1. Check camera connection
2. Verify camera permissions:
```bash
groups
```
You should see 'video' in the output. If not:
```bash
sudo usermod -a -G video $USER
```
Then log out and log back in.

### Common Error Messages

**"Camera not detected" error:**
- Camera interface not enabled in raspi-config
- Insufficient GPU memory allocation
- Faulty ribbon cable connection

**"Permission denied" errors:**
- User not in video group
- Incorrect device permissions

**"Module not found" errors:**
- Missing packages: `sudo apt install python3-picamera2 python3-opencv`

## License

This project is licensed under the MIT License - see the LICENSE file for details. 