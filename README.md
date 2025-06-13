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
- **`camera_app_pi.py`** - Dedicated application for Raspberry Pi Camera Module
- **`camera_app_usb.py`** - Dedicated application for USB cameras

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
python3 camera_app_pi.py      # For Pi Camera Module
python3 camera_app_usb.py     # For USB cameras
python3 camera_app_usb.py 1   # For USB camera at index 1
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

If the camera doesn't work:
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

## License

This project is licensed under the MIT License - see the LICENSE file for details. 