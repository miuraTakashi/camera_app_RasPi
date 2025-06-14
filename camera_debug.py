#!/usr/bin/env python3
"""
Raspberry Pi Camera Module Debug Script
Checks camera module status and provides troubleshooting information
"""

import subprocess
import os
import sys
from pathlib import Path

def run_command(cmd, description):
    """Run a command and return the result"""
    print(f"\n{'='*50}")
    print(f"Checking: {description}")
    print(f"Command: {cmd}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        print(f"Exit code: {result.returncode}")
        if result.stdout:
            print(f"Output:\n{result.stdout}")
        if result.stderr:
            print(f"Error:\n{result.stderr}")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("Command timed out (10 seconds)")
        return False
    except Exception as e:
        print(f"Error running command: {e}")
        return False

def check_file_exists(filepath, description):
    """Check if a file exists"""
    print(f"\n{'='*50}")
    print(f"Checking: {description}")
    print(f"File: {filepath}")
    print(f"{'='*50}")
    
    if os.path.exists(filepath):
        print(f"✓ File exists: {filepath}")
        try:
            with open(filepath, 'r') as f:
                content = f.read()
                print(f"Content:\n{content}")
        except Exception as e:
            print(f"Error reading file: {e}")
        return True
    else:
        print(f"✗ File not found: {filepath}")
        return False

def main():
    print("Raspberry Pi Camera Module Debug Tool")
    print("=====================================")
    
    # Check if running on Raspberry Pi
    print("\n1. System Information")
    run_command("uname -a", "System information")
    run_command("cat /proc/cpuinfo | grep Model", "Raspberry Pi model")
    
    # Check camera interface status
    print("\n2. Camera Interface Configuration")
    run_command("sudo raspi-config nonint get_camera", "Camera interface status (0=enabled, 1=disabled)")
    
    # Check boot config
    print("\n3. Boot Configuration")
    check_file_exists("/boot/config.txt", "Boot configuration file")
    run_command("grep -i camera /boot/config.txt", "Camera settings in boot config")
    run_command("grep -i start_x /boot/config.txt", "GPU memory settings")
    run_command("grep -i gpu_mem /boot/config.txt", "GPU memory allocation")
    
    # Check for camera device files
    print("\n4. Camera Device Files")
    check_file_exists("/dev/video0", "Video device 0")
    check_file_exists("/dev/video10", "Video device 10 (Pi Camera)")
    check_file_exists("/dev/video11", "Video device 11 (Pi Camera)")
    check_file_exists("/dev/video12", "Video device 12 (Pi Camera)")
    
    # Check camera modules
    print("\n5. Kernel Modules")
    run_command("lsmod | grep bcm2835", "BCM2835 camera module")
    run_command("lsmod | grep v4l2", "V4L2 modules")
    
    # Check camera detection
    print("\n6. Camera Detection")
    run_command("vcgencmd get_camera", "Camera detection status")
    run_command("libcamera-hello --list-cameras", "libcamera camera list")
    run_command("v4l2-ctl --list-devices", "V4L2 devices")
    
    # Check dmesg for camera-related messages
    print("\n7. System Messages")
    run_command("dmesg | grep -i camera", "Camera-related system messages")
    run_command("dmesg | grep -i bcm2835", "BCM2835-related messages")
    
    # Python camera library tests
    print("\n8. Python Library Tests")
    
    # Test picamera2
    print("\nTesting picamera2...")
    try:
        from picamera2 import Picamera2
        picam2 = Picamera2()
        cameras = Picamera2.global_camera_info()
        print(f"✓ picamera2 available, found {len(cameras)} cameras")
        for i, cam in enumerate(cameras):
            print(f"  Camera {i}: {cam}")
        picam2.close()
    except ImportError:
        print("✗ picamera2 not installed")
    except Exception as e:
        print(f"✗ picamera2 error: {e}")
    
    # Test OpenCV
    print("\nTesting OpenCV...")
    try:
        import cv2
        print(f"✓ OpenCV version: {cv2.__version__}")
        
        # Try to open camera
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("✓ OpenCV can open camera device 0")
            cap.release()
        else:
            print("✗ OpenCV cannot open camera device 0")
    except ImportError:
        print("✗ OpenCV not installed")
    except Exception as e:
        print(f"✗ OpenCV error: {e}")
    
    print("\n" + "="*50)
    print("TROUBLESHOOTING RECOMMENDATIONS")
    print("="*50)
    print("""
1. Enable camera interface:
   sudo raspi-config
   → Interface Options → Camera → Enable

2. Check/add to /boot/config.txt:
   start_x=1
   gpu_mem=128
   camera_auto_detect=1

3. Reboot after changes:
   sudo reboot

4. Install required packages:
   sudo apt update
   sudo apt install python3-picamera2 python3-opencv

5. Check camera connection:
   - Ensure ribbon cable is properly connected
   - Check cable orientation (blue side toward board)
   - Try different camera module if available

6. For libcamera (newer method):
   libcamera-hello --list-cameras
   libcamera-still -o test.jpg

7. For legacy camera (older method):
   raspistill -o test.jpg
""")

if __name__ == "__main__":
    main() 