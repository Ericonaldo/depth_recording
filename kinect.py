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

RECORD_FPS = 5

def save_data(color, depth, ir, camera_dir, frame_count):
    cv2.imwrite(str(camera_dir / f"color_{frame_count}.png"), color)
    # Convert depth to uint16 and save
    cv2.imwrite(str(camera_dir / f"depth_{frame_count}.png"), depth.astype(np.uint16))
    cv2.imwrite(str(camera_dir / f"ir_{frame_count}.png"), ir)

def init_kinect(fps=15):
    # config = k4a.K4A_DEVICE_CONFIG_INIT_DISABLE_ALL
    config = Config(
        color_resolution=pyk4a.ColorResolution.RES_1080P,
        depth_mode=pyk4a.DepthMode.WFOV_UNBINNED,
        synchronized_images_only=True,
        camera_fps=fps_dict[fps],
    )
    
    device = PyK4A(config=config)
    device.start()
    return device

class KinectRecorder:
    def __init__(self, vis, output_path="./recorded_data"):
        self.camera_name = "kinect"
        self.vis = vis
        
        # Create output directory
        output_path = Path(output_path)
        output_path.mkdir(exist_ok=True)
        
        # Create timestamp-based directory
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        session_dir = output_path / self.timestamp

        # Create camera directory
        self.camera_dir = session_dir / f"camera_{self.camera_name}"
        self.camera_dir.mkdir(parents=True, exist_ok=True)
        
        self.frame_count = 0

    def initialize_camera(self):
        print(f"Initializing device: {self.camera_name}")
        self.device = init_kinect()
        
        # Wait for the first frame to ensure camera is running
        self.device.get_capture()
        print("Kinect Kinect initialized successfully")

    def record_frames(self):
        start_time = time.time()
        print(f"CAM {self.camera_name}: Starting recording...")

        try:
            while True:
                record_time_start = time.time()
                # Get capture
                capture = self.device.get_capture()
                
                if capture.color is not None and capture.depth is not None:
                    # Get color, depth, and IR images
                    color = capture.color
                    depth = capture.depth
                    ir = capture.ir

                    # Align depth to color
                    transformed_depth = pyk4a.depth_image_to_color_camera(depth, self.device.calibration, thread_safe=True)
                    # transformed_color = pyk4a.color_image_to_depth_camera(color, depth, self.device.calibration, thread_safe=True) # Not good

                    # Save frames asynchronously
                    save_process = Process(
                        target=save_data,
                        args=(color.copy(), transformed_depth.copy(), ir.copy(), 
                              self.camera_dir, self.frame_count)
                    )
                    save_process.start()

                    if self.vis:
                        cv2.imshow(f"{self.camera_name} Visualization", color)
                        cv2.waitKey(1)

                    self.frame_count += 1

                    # Display progress
                    if self.frame_count % 30 == 0:
                        print(f"CAM {self.camera_name}: Recorded... {int(time.time() - start_time)} seconds, {self.frame_count} frames")
                    
                    time.sleep(max(0, 1/RECORD_FPS - (time.time()-record_time_start))) # fps = RECORD_FPS

        except KeyboardInterrupt:
            print("\nRecording stopped by user")
            self.stop_record()

    def stop_record(self):
        if hasattr(self, 'device'):
            self.device.stop()

    def __del__(self):
        self.stop_record()

if __name__ == "__main__":
    recorder = KinectRecorder()
    recorder.initialize_camera()
    recorder.record_frames()
