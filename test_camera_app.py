#!/usr/bin/env python3
"""
Test script for camera application
Tests basic functionality without requiring an actual camera
"""

import sys
import os
sys.path.append('.')

try:
    from camera_app import CameraApp
    print("✓ Successfully imported CameraApp")
    
    # Test configuration loading
    app = CameraApp()
    print("✓ Successfully created CameraApp instance")
    
    # Test camera detection (will fail gracefully without camera)
    cameras = app.detect_cameras()
    print(f"✓ Camera detection completed - found {len(cameras)} camera(s)")
    
    # Test configuration
    config = app.config
    print(f"✓ Configuration loaded - camera resolution: {config['camera']['width']}x{config['camera']['height']}")
    
    # Test utility functions
    space_ok, free_gb = app.check_disk_space()
    print(f"✓ Disk space check: {free_gb:.1f} GB free")
    
    print("\n🎉 All tests passed! Camera application is ready to use.")
    print("\nTo run the application with a USB camera:")
    print("python3 camera_app.py")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all dependencies are installed: pip3 install -r camera_requirements.txt")
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1) 