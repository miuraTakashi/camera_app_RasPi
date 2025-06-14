#!/usr/bin/env python3
"""
Raspberry Pi Camera Module Application
専用のカメラアプリケーション - Pi Camera Module用
"""

import cv2
import time
import datetime
import os
import json
from pathlib import Path
import picamera
from picamera.array import PiRGBArray

class PiCameraApp:
    def __init__(self, config_file="camera_config.json"):
        """Initialize the Pi Camera application"""
        self.camera = None
        self.is_recording = False
        self.recording_start_time = 0
        self.video_writer = None
        
        # Load configuration
        self.config = self.load_config(config_file)
        
        # Create save directories
        self.create_directories()
        
        print("Pi Camera Application initialized")

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
                "codec": "H264",
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
                # Ensure we're using the actual home directory
                home_dir = Path.home()
                if name == "images":
                    target_path = home_dir / "Pictures"
                else:  # videos
                    target_path = home_dir / "Movies"
                
                target_path.mkdir(parents=True, exist_ok=True)
                # Update config with the verified path
                self.config["save_paths"][name] = str(target_path)
                print(f"Directory created/verified: {target_path}")
                
            except PermissionError:
                # Fallback to Desktop if home Pictures/Movies not accessible
                try:
                    desktop_path = Path.home() / "Desktop"
                    folder_name = "Movies" if name == "videos" else "Pictures"
                    fallback_path = desktop_path / folder_name
                    fallback_path.mkdir(parents=True, exist_ok=True)
                    self.config["save_paths"][name] = str(fallback_path)
                    print(f"Permission denied for home {folder_name}, using Desktop: {fallback_path}")
                except:
                    # Last resort: current directory
                    folder_name = "Movies" if name == "videos" else "Pictures"
                    fallback_path = Path.cwd() / folder_name
                    fallback_path.mkdir(parents=True, exist_ok=True)
                    self.config["save_paths"][name] = str(fallback_path)
                    print(f"Using current directory fallback: {fallback_path}")
                    
            except Exception as e:
                print(f"Error creating directory {path}: {e}")
                # Use Desktop as fallback
                try:
                    desktop_path = Path.home() / "Desktop"
                    folder_name = "Movies" if name == "videos" else "Pictures"
                    fallback_path = desktop_path / folder_name
                    fallback_path.mkdir(parents=True, exist_ok=True)
                    self.config["save_paths"][name] = str(fallback_path)
                    print(f"Using Desktop fallback: {fallback_path}")
                except:
                    # Last resort: current directory
                    folder_name = "Movies" if name == "videos" else "Pictures"
                    fallback_path = Path.cwd() / folder_name
                    fallback_path.mkdir(parents=True, exist_ok=True)
                    self.config["save_paths"][name] = str(fallback_path)
                    print(f"Using current directory fallback: {fallback_path}")

    def initialize_camera(self):
        """Initialize Pi Camera"""
        try:
            print("Initializing Pi Camera...")
            self.camera = picamera.PiCamera()
            self.camera.resolution = (
                self.config["camera"]["width"], 
                self.config["camera"]["height"]
            )
            self.camera.framerate = self.config["camera"]["fps"]
            
            # Warm up camera
            time.sleep(2)
            print("Pi Camera initialized successfully")
            return True
        except Exception as e:
            print(f"Failed to initialize Pi Camera: {e}")
            return False

    def get_frame(self):
        """Capture frame from Pi Camera"""
        try:
            with PiRGBArray(self.camera) as output:
                self.camera.capture(output, format="bgr")
                return output.array.copy()
        except Exception as e:
            print(f"Error capturing frame: {e}")
            return None

    def save_image(self):
        """Save current frame as image"""
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"PiCam_Image_{timestamp}.jpg"
            filepath = os.path.join(self.config["save_paths"]["images"], filename)
            
            # Capture directly to file for better quality
            self.camera.capture(filepath)
            print(f"Image saved: {filepath}")
        except Exception as e:
            print(f"Error saving image: {e}")

    def start_video_recording(self):
        """Start video recording"""
        if self.is_recording:
            return
        
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"PiCam_Video_{timestamp}.h264"
            filepath = os.path.join(self.config["save_paths"]["videos"], filename)
            
            self.camera.start_recording(filepath)
            self.is_recording = True
            self.recording_start_time = time.time()
            print(f"Video recording started: {filepath}")
        except Exception as e:
            print(f"Error starting video recording: {e}")

    def stop_video_recording(self):
        """Stop video recording"""
        if not self.is_recording:
            return
        
        try:
            self.camera.stop_recording()
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
        
        print("Pi Camera Application started")
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
                
                # Display frame
                cv2.imshow('Pi Camera', frame)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("Quitting...")
                    break
                elif key == ord(' '):
                    self.save_image()
                elif key == ord('v'):
                    if self.is_recording:
                        self.stop_video_recording()
                    else:
                        self.start_video_recording()
        
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
            self.camera.close()
        
        cv2.destroyAllWindows()
        print("Cleanup completed")

def main():
    app = PiCameraApp()
    app.run()

if __name__ == "__main__":
    main() 