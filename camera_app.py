#!/usr/bin/env python3
"""
Raspberry Pi Camera Application
- Supports both USB cameras and Raspberry Pi Camera Module
- Compatible with Raspberry Pi 2 and newer models
- Full screen camera display
- Save images with spacebar (Image+datetime.jpg)
- Record video with 'v' key toggle
- Red recording indicator
- Auto camera detection
- Status display with FPS counter
- Configurable settings
"""

import sys
import cv2
import numpy as np
import datetime
import os
import threading
import time
import json
import psutil
from picamera import PiCamera
from picamera.array import PiRGBArray
from pathlib import Path

# Check Python version
if sys.version_info[0] < 3:
    print("This script requires Python 3. Please run with python3.")
    sys.exit(1)

class CameraApp:
    def __init__(self, config_file="camera_config.json"):
        self.cap = None
        self.picam = None
        self.raw_capture = None
        self.is_recording = False
        self.video_writer = None
        self.recording_start_time = None
        self.frame_width = 640
        self.frame_height = 480
        self.fps_counter = 0
        self.fps_start_time = time.time()
        self.current_fps = 0
        self.camera_type = None  # 'usb' or 'picam'
        
        # Get user's home directory
        self.home_dir = str(Path.home())
        
        # Load configuration
        self.config = self.load_config(config_file)
        
        # Create directories if they don't exist
        os.makedirs(self.config["save_paths"]["images"], exist_ok=True)
        os.makedirs(self.config["save_paths"]["videos"], exist_ok=True)
        
        # Set permissions (755 = rwxr-xr-x)
        for path in [self.config["save_paths"]["images"],
                    self.config["save_paths"]["videos"]]:
            os.chmod(path, 0o755)
    
    def load_config(self, config_file):
        """Load configuration from JSON file or create default"""
        default_config = {
            "camera": {
                "width": 1280,
                "height": 720,
                "fps": 30,
                "auto_detect": True,
                "preferred_index": 0,
                "preferred_type": "auto"  # 'auto', 'usb', or 'picam'
            },
            "video": {
                "codec": "mp4v",
                "quality": "high",
                "fps": 30
            },
            "save_paths": {
                "images": os.path.join(self.home_dir, "Pictures"),
                "videos": os.path.join(self.home_dir, "Movies")
            },
            "display": {
                "show_fps": True,
                "show_status": True,
                "show_timestamp": True
            }
        }
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    # Update default config with any existing settings
                    for key in default_config:
                        if key in config:
                            if isinstance(default_config[key], dict):
                                default_config[key].update(config[key])
                            else:
                                default_config[key] = config[key]
                    return default_config
        except Exception as e:
            print("Error loading config: {}. Using defaults.".format(e))
        
        return default_config
    
    def detect_cameras(self):
        """Detect available cameras (both USB and Pi Camera)"""
        available_cameras = []
        print("Detecting cameras...")
        
        # Check for Pi Camera
        try:
            picam = PiCamera()
            available_cameras.append("picam")
            print("Raspberry Pi Camera Module: Available")
            picam.close()
        except Exception as e:
            print("Raspberry Pi Camera Module: Not available")
        
        # Check for USB cameras
        for i in range(10):  # Check first 10 indices
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    available_cameras.append(f"usb_{i}")
                    print(f"USB Camera {i}: Available")
                cap.release()
            else:
                break
                
        return available_cameras
    
    def initialize_camera(self, camera_type=None):
        """Initialize either USB camera or Pi Camera"""
        if camera_type is None:
            camera_type = self.config["camera"]["preferred_type"]
        
        # Clean up existing camera
        self.cleanup_camera()
        
        if camera_type == "picam" or (camera_type == "auto" and "picam" in self.detect_cameras()):
            try:
                self.picam = PiCamera()
                self.picam.resolution = (self.config["camera"]["width"], self.config["camera"]["height"])
                self.picam.framerate = self.config["camera"]["fps"]
                self.raw_capture = PiRGBArray(self.picam, size=(self.config["camera"]["width"], self.config["camera"]["height"]))
                self.camera_type = "picam"
                print("Initialized Raspberry Pi Camera Module")
                return True
            except Exception as e:
                print(f"Error initializing Pi Camera: {e}")
                return False
        else:
            # Try USB camera
            cameras = self.detect_cameras()
            usb_cameras = [cam for cam in cameras if cam.startswith("usb_")]
            
            if usb_cameras:
                camera_index = int(usb_cameras[0].split("_")[1])
                self.cap = cv2.VideoCapture(camera_index)
                
                if not self.cap.isOpened():
                    print(f"Error: Cannot access USB camera {camera_index}")
                    return False
                
                # Set camera properties
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config["camera"]["width"])
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config["camera"]["height"])
                self.cap.set(cv2.CAP_PROP_FPS, self.config["camera"]["fps"])
                
                self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                self.camera_type = "usb"
                print(f"Initialized USB camera: {self.frame_width}x{self.frame_height}")
                return True
            
            print("No cameras available")
            return False
    
    def get_frame(self):
        """Get frame from either USB camera or Pi Camera"""
        if self.camera_type == "picam":
            self.raw_capture.truncate(0)
            self.picam.capture(self.raw_capture, format="bgr")
            frame = self.raw_capture.array
        else:  # USB camera
            ret, frame = self.cap.read()
            if not ret:
                return None
        return frame
    
    def cleanup_camera(self):
        """Clean up camera resources"""
        if self.cap:
            self.cap.release()
            self.cap = None
        if self.picam:
            self.picam.close()
            self.picam = None
        if self.raw_capture:
            self.raw_capture = None
        self.camera_type = None
    
    def check_disk_space(self, path=".", min_gb=1):
        """Check available disk space"""
        try:
            disk_usage = psutil.disk_usage(path)
            free_gb = disk_usage.free / (1024**3)
            return free_gb > min_gb, free_gb
        except:
            return True, 0  # Assume OK if can't check
    
    def save_image(self, frame):
        """Save current frame as image with timestamp"""
        # Check disk space
        space_ok, free_gb = self.check_disk_space()
        if not space_ok:
            print(f"Warning: Low disk space ({free_gb:.1f} GB)")
            
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.config['save_paths']['images']}/Image{timestamp}.jpg"
        
        # Save with high quality
        encode_params = [cv2.IMWRITE_JPEG_QUALITY, 95]
        success = cv2.imwrite(filename, frame, encode_params)
        
        if success:
            file_size = os.path.getsize(filename) / 1024  # KB
            print(f"Image saved: {filename} ({file_size:.1f} KB)")
        else:
            print("Error saving image")
    
    def start_video_recording(self, frame):
        """Start video recording"""
        if self.is_recording:
            return
            
        # Check disk space
        space_ok, free_gb = self.check_disk_space()
        if not space_ok:
            print(f"Warning: Low disk space ({free_gb:.1f} GB) - recording may fail")
            
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.config['save_paths']['videos']}/Video{timestamp}.h264"
        
        if self.camera_type == "picam":
            # Use Pi Camera's native H264 recording
            self.picam.start_recording(filename)
            self.video_writer = True  # Just a flag for Pi Camera
        else:
            # Use OpenCV's VideoWriter for USB camera
            filename = filename.replace('.h264', '.mp4')
            fourcc = cv2.VideoWriter_fourcc(*self.config["video"]["codec"])
            fps = self.config["video"]["fps"]
            self.video_writer = cv2.VideoWriter(filename, fourcc, fps, 
                                              (self.frame_width, self.frame_height))
        
        if self.video_writer:
            self.is_recording = True
            self.recording_start_time = time.time()
            print(f"Video recording started: {filename}")
        else:
            print("Error: Could not start video recording")
    
    def stop_video_recording(self):
        """Stop video recording"""
        if not self.is_recording:
            return
            
        self.is_recording = False
        if self.camera_type == "picam":
            self.picam.stop_recording()
        elif self.video_writer:
            self.video_writer.release()
        self.video_writer = None
            
        duration = time.time() - self.recording_start_time
        print(f"Video recording stopped. Duration: {duration:.1f} seconds")
    
    def update_fps(self):
        """Update FPS counter"""
        self.fps_counter += 1
        current_time = time.time()
        if current_time - self.fps_start_time >= 1.0:
            self.current_fps = self.fps_counter
            self.fps_counter = 0
            self.fps_start_time = current_time
    
    def draw_status(self, frame):
        """Draw status information on the frame"""
        if not self.config["display"]["show_status"]:
            return frame
            
        # Get frame dimensions
        height, width = frame.shape[:2]
        
        # Calculate text position (bottom left with padding)
        padding = 10
        y_position = height - padding
        
        # Draw FPS counter
        if self.config["display"]["show_fps"]:
            fps_text = f"FPS: {self.current_fps:.1f}"
            cv2.putText(frame, fps_text, (padding, y_position), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            y_position -= 30  # Move up for next line
        
        # Draw timestamp
        if self.config["display"]["show_timestamp"]:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cv2.putText(frame, timestamp, (padding, y_position), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            y_position -= 30  # Move up for next line
        
        # Draw recording status
        if self.is_recording:
            duration = time.time() - self.recording_start_time
            recording_text = f"Recording: {duration:.1f}s"
            cv2.putText(frame, recording_text, (padding, y_position), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        return frame
    
    def draw_overlay_info(self, frame):
        """Draw overlay information on frame"""
        # Get frame dimensions
        height, width = frame.shape[:2]
        
        # Calculate text position (bottom left with padding)
        padding = 10
        y_position = height - padding
        
        # Draw controls information
        controls = [
            "SPACEBAR: save image",
            "V: toggle video recording",
            "Q: quit application"
        ]
        
        # Draw each line from bottom to top
        for control in reversed(controls):
            cv2.putText(frame, control, (padding, y_position), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            y_position -= 30  # Move up for next line
        
        return frame
    
    def switch_camera(self):
        """Switch between USB and Pi Camera"""
        if self.is_recording:
            print("Cannot switch camera while recording")
            return False
            
        current_type = self.camera_type
        if current_type == "picam":
            # Try switching to USB camera
            return self.initialize_camera("usb")
        else:
            # Try switching to Pi Camera
            return self.initialize_camera("picam")
    
    def run(self):
        """Main application loop"""
        if not self.initialize_camera():
            return
        
        # Create full screen window
        cv2.namedWindow("Camera", cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("Camera", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        
        print("Camera Application Started")
        print("Controls:")
        print("  SPACEBAR - Save image")
        print("  V - Start/Stop video recording")
        print("  T - Toggle overlay display")
        print("  C - Switch camera")
        print("  ESC or Q - Quit")
        
        try:
            while True:
                frame = self.get_frame()
                if frame is None:
                    print("Error: Failed to capture frame")
                    break
                
                # Update FPS counter
                self.update_fps()
                
                # Draw overlay information
                self.draw_overlay_info(frame)
                
                # Write frame to video if recording (for USB camera)
                if self.is_recording and self.camera_type == "usb" and self.video_writer:
                    self.video_writer.write(frame)
                
                # Display frame
                cv2.imshow("Camera", frame)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord(' '):  # Spacebar - save image
                    self.save_image(frame)
                elif key == ord('v') or key == ord('V'):  # V key - toggle recording
                    if self.is_recording:
                        self.stop_video_recording()
                    else:
                        self.start_video_recording(frame)
                elif key == ord('t') or key == ord('T'):  # T key - toggle overlay
                    self.config["display"]["show_status"] = not self.config["display"]["show_status"]
                    print(f"Overlay display: {'ON' if self.config['display']['show_status'] else 'OFF'}")
                elif key == ord('c') or key == ord('C'):  # C key - switch camera
                    self.switch_camera()
                elif key == 27 or key == ord('q') or key == ord('Q'):  # ESC or Q - quit
                    break
                    
        except KeyboardInterrupt:
            print("\nApplication interrupted by user")
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        if self.is_recording:
            self.stop_video_recording()
        
        self.cleanup_camera()
        cv2.destroyAllWindows()
        print("Application closed")

def main():
    app = CameraApp()
    app.run()

if __name__ == "__main__":
    main() 