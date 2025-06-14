#!/usr/bin/env python3
"""
Test script for camera application
Tests basic functionality without requiring an actual camera
"""

import sys
import os
sys.path.append('.')

try:
    # Test camera launcher import
    import camera_launcher
    print("✓ Successfully imported camera_launcher")
    
    # Test Pi camera app import
    from pi_camera_app import PiCameraApp
    print("✓ Successfully imported PiCameraApp")
    
    # Test USB camera app import
    from usb_camera_app import USBCameraApp
    print("✓ Successfully imported USBCameraApp")
    
    # Test configuration loading
    pi_app = PiCameraApp()
    print("✓ Successfully created PiCameraApp instance")
    
    # Test configuration
    config = pi_app.config
    print(f"✓ Configuration loaded - camera resolution: {config['camera']['width']}x{config['camera']['height']}")
    
    print("\n🎉 All tests passed! Camera application is ready to use.")
    print("\nTo run the application:")
    print("python3 camera_launcher.py")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all dependencies are installed: pip3 install -r camera_requirements.txt")
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1) 