#!/usr/bin/env python3
"""
Camera Application Launcher
カメラアプリケーションランチャー - カメラタイプを選択
"""

import os
import sys
import subprocess

def check_pi_camera():
    """Check if Pi Camera is available"""
    try:
        from picamera2 import Picamera2
        camera = Picamera2()
        camera.close()  # Close immediately after test
        return True
    except Exception:
        return False

def check_usb_camera():
    """Check if USB Camera is available"""
    try:
        import cv2
        for i in range(3):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, frame = cap.read()
                cap.release()
                if ret and frame is not None:
                    return True, i
        return False, None
    except Exception:
        return False, None

def main():
    print("Camera Application Launcher")
    print("=" * 40)
    
    # Check available cameras
    pi_camera_available = check_pi_camera()
    usb_camera_available, usb_index = check_usb_camera()
    
    print("Available cameras:")
    if pi_camera_available:
        print("  1. Raspberry Pi Camera Module")
    if usb_camera_available:
        print(f"  2. USB Camera (index: {usb_index})")
    
    if not pi_camera_available and not usb_camera_available:
        print("No cameras detected!")
        return
    
    # Auto-select if only one camera is available
    if pi_camera_available and not usb_camera_available:
        print("\nOnly Pi Camera detected. Starting Pi Camera application...")
        subprocess.run([sys.executable, "pi_camera_app.py"])
        return
    elif usb_camera_available and not pi_camera_available:
        print(f"\nOnly USB Camera detected. Starting USB Camera application...")
        subprocess.run([sys.executable, "usb_camera_app.py", str(usb_index)])
        return
    
    # Both cameras available - let user choose
    print("\nMultiple cameras detected.")
    while True:
        try:
            choice = input("Select camera (1 for Pi Camera, 2 for USB Camera): ")
            if choice == "1":
                print("Starting Pi Camera application...")
                subprocess.run([sys.executable, "pi_camera_app.py"])
                break
            elif choice == "2":
                print("Starting USB Camera application...")
                subprocess.run([sys.executable, "usb_camera_app.py", str(usb_index)])
                break
            else:
                print("Invalid choice. Please enter 1 or 2.")
        except KeyboardInterrupt:
            print("\nExiting...")
            break

if __name__ == "__main__":
    main() 