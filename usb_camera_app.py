#!/usr/bin/env python3
"""
USB Camera Application
専用のカメラアプリケーション - USBカメラ用
"""

import cv2
import time
import datetime
import os
import json
from pathlib import Path

class USBCameraApp:
    def __init__(self, config_file="camera_config.json", camera_index=0):
        """Initialize the USB Camera application"""
        self.camera = None
        self.camera_index = camera_index
        self.is_recording = False
        self.recording_start_time = 0
        self.video_writer = None
        
        # Load configuration
        self.config = self.load_config(config_file)
        
        # Create save directories
        self.create_directories()
        
        print("USB Camera Application initialized")

    def load_config(self, config_file):
        """Load configuration from JSON file"""
        default_config = {
            "camera": {
                "width": 640,
                "height": 480,
                "fps": 30
            },
            "save_paths": {
                "images": str(Path.home() / "Pictures"),
                "videos": str(Path.home() / "Movies")
            },
            "video": {
                "codec": "MJPG",
                "fps": 30
            }
        }
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
                # Merge with default config
                for key in default_config:
                    if key not in config:
                        config[key] = default_config[key]
                return config
            else:
                # Create default config file
                with open(config_file, 'w') as f:
                    json.dump(default_config, f, indent=4)
                return default_config
        except Exception as e:
            print(f"Error loading config: {e}")
            return default_config

    def create_directories(self):
        """Create necessary directories"""
        for name, path in self.config["save_paths"].items():
            try:
                Path(path).mkdir(parents=True, exist_ok=True)
                print(f"Directory created/verified: {path}")
            except PermissionError:
                # Fallback to current directory if home directory is not accessible
                folder_name = "Movies" if name == "videos" else "Pictures"
                fallback_path = Path.cwd() / folder_name
                fallback_path.mkdir(parents=True, exist_ok=True)
                self.config["save_paths"][name] = str(fallback_path)
                print(f"Permission denied for {path}, using fallback: {fallback_path}")
            except Exception as e:
                print(f"Error creating directory {path}: {e}")
                # Use current directory as last resort
                folder_name = "Movies" if name == "videos" else "Pictures"
                fallback_path = Path.cwd() / folder_name
                fallback_path.mkdir(parents=True, exist_ok=True)
                self.config["save_paths"][name] = str(fallback_path)
                print(f"Using fallback directory: {fallback_path}")

    def detect_usb_camera(self):
        """Detect available USB cameras"""
        print("Detecting USB cameras...")
        for i in range(5):  # Check first 5 indices
            print(f"  Checking camera index {i}...")
            try:
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        print(f"  USB camera found at index {i}")
                        cap.release()
                        return i
                cap.release()
            except Exception as e:
                print(f"  Error checking camera {i}: {e}")
                continue
        
        print("No USB cameras detected")
        return None

    def initialize_camera(self):
        """Initialize USB Camera"""
        # First detect available cameras
        detected_index = self.detect_usb_camera()
        if detected_index is not None:
            self.camera_index = detected_index
        
        try:
            print(f"Initializing USB camera at index {self.camera_index}...")
            self.camera = cv2.VideoCapture(self.camera_index)
            
            if not self.camera.isOpened():
                print("Failed to open USB camera")
                return False
            
            # Set camera properties
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.config["camera"]["width"])
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config["camera"]["height"])
            self.camera.set(cv2.CAP_PROP_FPS, self.config["camera"]["fps"])
            
            # Verify settings
            actual_width = int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
            actual_fps = self.camera.get(cv2.CAP_PROP_FPS)
            
            print(f"USB Camera initialized: {actual_width}x{actual_height} @ {actual_fps} FPS")
            return True
            
        except Exception as e:
            print(f"Failed to initialize USB camera: {e}")
            return False

    def get_frame(self):
        """Capture frame from USB Camera"""
        try:
            if self.camera is not None and self.camera.isOpened():
                ret, frame = self.camera.read()
                if ret:
                    return frame
            return None
        except Exception as e:
            print(f"Error capturing frame: {e}")
            return None

    def save_image(self, frame):
        """Save current frame as image"""
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"USB_Image_{timestamp}.jpg"
            filepath = os.path.join(self.config["save_paths"]["images"], filename)
            
            cv2.imwrite(filepath, frame)
            print(f"Image saved: {filepath}")
        except Exception as e:
            print(f"Error saving image: {e}")

    def start_video_recording(self, frame):
        """Start video recording"""
        if self.is_recording:
            return
        
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"USB_Video_{timestamp}.avi"
            filepath = os.path.join(self.config["save_paths"]["videos"], filename)
            
            # Get frame dimensions
            height, width = frame.shape[:2]
            
            # Define codec and create VideoWriter
            fourcc = cv2.VideoWriter_fourcc(*self.config["video"]["codec"])
            self.video_writer = cv2.VideoWriter(
                filepath, fourcc, self.config["video"]["fps"], (width, height)
            )
            
            if self.video_writer.isOpened():
                self.is_recording = True
                self.recording_start_time = time.time()
                print(f"Video recording started: {filepath}")
            else:
                print("Error: Could not start video recording")
                self.video_writer = None
                
        except Exception as e:
            print(f"Error starting video recording: {e}")

    def stop_video_recording(self):
        """Stop video recording"""
        if not self.is_recording:
            return
        
        try:
            if self.video_writer:
                self.video_writer.release()
                self.video_writer = None
            
            self.is_recording = False
            duration = time.time() - self.recording_start_time
            print(f"Video recording stopped. Duration: {duration:.1f} seconds")
        except Exception as e:
            print(f"Error stopping video recording: {e}")

    def draw_overlay_info(self, frame):
        """Draw overlay information on frame"""
        height, width = frame.shape[:2]
        padding = 10
        y_position = height - padding
        
        controls = [
            "SPACEBAR: save image",
            "V: toggle video recording", 
            "Q: quit application"
        ]
        
        for control in reversed(controls):
            cv2.putText(frame, control, (padding, y_position), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            y_position -= 30
        
        # Show recording status
        if self.is_recording:
            duration = time.time() - self.recording_start_time
            recording_text = f"Recording: {duration:.1f}s"
            cv2.putText(frame, recording_text, (padding, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        return frame

    def run(self):
        """Main application loop"""
        if not self.initialize_camera():
            print("Failed to initialize camera. Exiting...")
            return
        
        print("USB Camera Application started")
        print("Controls:")
        print("  SPACEBAR - Save image")
        print("  V - Start/Stop video recording")
        print("  Q - Quit")
        
        try:
            while True:
                frame = self.get_frame()
                if frame is None:
                    print("Failed to capture frame")
                    time.sleep(0.1)
                    continue
                
                # Add overlay information
                frame = self.draw_overlay_info(frame)
                
                # Write frame to video if recording
                if self.is_recording and self.video_writer:
                    self.video_writer.write(frame)
                
                # Display frame
                cv2.imshow('USB Camera', frame)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("Quitting...")
                    break
                elif key == ord(' '):
                    self.save_image(frame)
                elif key == ord('v'):
                    if self.is_recording:
                        self.stop_video_recording()
                    else:
                        self.start_video_recording(frame)
        
        except KeyboardInterrupt:
            print("\nApplication interrupted by user")
        except Exception as e:
            print(f"Error in main loop: {e}")
        finally:
            self.cleanup()

    def cleanup(self):
        """Clean up resources"""
        print("Cleaning up resources...")
        if self.is_recording:
            self.stop_video_recording()
        
        if self.camera:
            self.camera.release()
        
        cv2.destroyAllWindows()
        print("Cleanup completed")

def main():
    import sys
    camera_index = 0
    if len(sys.argv) > 1:
        try:
            camera_index = int(sys.argv[1])
        except ValueError:
            print("Invalid camera index. Using default (0)")
    
    app = USBCameraApp(camera_index=camera_index)
    app.run()

if __name__ == "__main__":
    main() 