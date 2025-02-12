import numpy as np
import time
from pathlib import Path
from datetime import datetime
from multiprocessing import Process
import cv2
import pyk4a
from pyk4a import Config, PyK4A

fps_dict = {
    5: pyk4a.FPS.FPS_5,
    15: pyk4a.FPS.FPS_15,
    30: pyk4a.FPS.FPS_30,
}

def save_data(color, depth, ir, camera_dir, frame_count):
    cv2.imwrite(str(camera_dir / f"color_{frame_count}.png"), color)
    # Convert depth to uint16 and save
    cv2.imwrite(str(camera_dir / f"depth_{frame_count}.png"), depth.astype(np.uint16))
    cv2.imwrite(str(camera_dir / f"ir_{frame_count}.png"), ir)
    np.save(str(camera_dir / f"raw_depth_{frame_count}.npy"), depth)

def init_azure(fps=5):
    # config = k4a.K4A_DEVICE_CONFIG_INIT_DISABLE_ALL
    config = Config(
        color_resolution=pyk4a.ColorResolution.RES_1080P,
        depth_mode=pyk4a.DepthMode.NFOV_UNBINNED,
        synchronized_images_only=True,
        camera_fps=fps_dict[fps],
    )
    
    device = PyK4A(config=config)
    device.start()
    return device

class AzureRecorder:
    def __init__(self, output_path="./recorded_data"):
        self.camera_name = "Azure"
        
        # Create output directory
        output_path = Path(output_path)
        output_path.mkdir(exist_ok=True)
        
        # Create timestamp-based directory
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_dir = output_path / self.timestamp

        # Create camera directory
        self.camera_dir = session_dir / f"camera_{self.camera_name}"
        self.camera_dir.mkdir(parents=True, exist_ok=True)
        
        self.frame_count = 0

    def initialize_camera(self):
        print(f"Initializing device: {self.camera_name}")
        self.device = init_azure()
        
        # Wait for the first frame to ensure camera is running
        self.device.get_capture()
        print("Azure Kinect initialized successfully")

    def record_frames(self):
        start_time = time.time()
        print(f"CAM {self.camera_name}: Starting recording...")

        try:
            while True:
                # Get capture
                capture = self.device.get_capture()
                
                if capture.color is not None and capture.depth is not None:
                    # Get color, depth, and IR images
                    color = capture.color
                    depth = capture.depth
                    ir = capture.ir

                    # Save frames asynchronously
                    save_process = Process(
                        target=save_data,
                        args=(color.copy(), depth.copy(), ir.copy(), 
                              self.camera_dir, self.frame_count)
                    )
                    save_process.start()

                    self.frame_count += 1

                    # Display progress
                    if self.frame_count % 30 == 0:
                        print(f"CAM {self.camera_name}: Recorded... {int(time.time() - start_time)} seconds, {self.frame_count} frames")

        except KeyboardInterrupt:
            print("\nRecording stopped by user")
            self.stop_record()

    def stop_record(self):
        if hasattr(self, 'device'):
            self.device.stop()

    def __del__(self):
        self.stop_record()

if __name__ == "__main__":
    recorder = AzureRecorder()
    recorder.initialize_camera()
    recorder.record_frames()
