try:
    import pyrealsense2.pyrealsense2 as rs
except ImportError:
    import pyrealsense2 as rs
import numpy as np
import time
from pathlib import Path
from datetime import datetime
from multiprocessing import Process
import cv2

serial_number_dict = {
    "f0221682": "l515",
    "419122270011": "d405",
    "332122060387": "d415",
    "242322077064": "d435",
    "043422252251": "d455",
}

depth_resolution_dict = {
    "l515": (1024, 768),
    "d405": (1280, 720),
    "d415": (1280, 720),
    "d435": (1280, 720),
    "d455": (1280, 720),
}

color_resolution_dict = {
    "l515": (1920, 1080),
    "d405": (1280, 720),
    "d415": (1920, 1080),
    "d435": (1920, 1080),
    "d455": (1280, 800),
}

# Minimum FPS for each camera
# fps_dict = {
#     "l515": 30,
#     "d405": 5,
#     "d415": 15,
#     "d435": 15,
#     "d455": 5,
# }
fps_dict = {
    "l515": 30,
    "d405": 30,
    "d415": 30,
    "d435": 30,
    "d455": 5,
}

RECORD_FPS = 5

def save_data(depth_image, color_image, camera_dir, frame_count):
    cv2.imwrite(str(camera_dir / f"depth_{frame_count}.png"), depth_image)
    cv2.imwrite(str(camera_dir / f"color_{frame_count}.png"), color_image)

def get_depth_filter():
    # filter stuff
    depth_to_disparity = rs.disparity_transform(True)
    disparity_to_depth = rs.disparity_transform(False)
    decimation = rs.decimation_filter()
    decimation.set_option(rs.option.filter_magnitude, 4)
    spatial = rs.spatial_filter()
    spatial.set_option(rs.option.filter_magnitude, 5)
    spatial.set_option(rs.option.filter_smooth_alpha, 1)
    spatial.set_option(rs.option.filter_smooth_delta, 50)
    spatial.set_option(rs.option.holes_fill, 3)
    temporal = rs.temporal_filter()
    hole_filling = rs.hole_filling_filter(mode=2)

    return depth_to_disparity, disparity_to_depth, decimation, spatial, temporal, hole_filling

def depth_process(frame, depth_to_disparity=None, disparity_to_depth=None, decimation=None, spatial=None, temporal=None, hole_filling=None):
    # if decimation is not None:
    #     frame = decimation.process(frame)
    # if depth_to_disparity is not None:
    #     frame = depth_to_disparity.process(frame)

    # if disparity_to_depth is not None:
    #     frame = disparity_to_depth.process(frame)
    if hole_filling is not None:
        frame = hole_filling.process(frame)
    # if spatial is not None:
    #     frame = spatial.process(frame)
    # if temporal is not None:
    #     frame = temporal.process(frame)

    return frame

class RealSenseRecorder:
    def __init__(self, serial_number, vis, output_path="./recorded_data"):
        self.pipeline = None
        self.config = None

        self.serial_number = serial_number
        self.camera_name = serial_number_dict.get(serial_number, "unknown")

        self.vis = vis
        
        # Create output directory
        output_path = Path(output_path)
        output_path.mkdir(exist_ok=True)
        
        # Create timestamp-based directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        session_dir = output_path / timestamp

        # Create camera directory
        self.camera_dir = session_dir / f"camera_{self.camera_name}"
        self.camera_dir.mkdir(parents=True, exist_ok=True)

    def initialize_camera(self):
        print(f"Initializing device: {self.serial_number} {self.camera_name}")
        
        # Setup pipeline and config for each camera
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        # self.depth_filters = get_depth_filter()

        self.config.enable_device(self.serial_number)
        
        # Enable streams
        self.config.enable_stream(rs.stream.depth, *depth_resolution_dict[self.camera_name], rs.format.z16, fps_dict[self.camera_name])
        self.config.enable_stream(rs.stream.color, *color_resolution_dict[self.camera_name], rs.format.bgr8, fps_dict[self.camera_name])
        # Create alignment primitive with color as its target stream
        self.align = rs.align(rs.stream.color)
        # self.align = rs.align(rs.stream.depth)

        # Start streaming
        profile = self.pipeline.start(self.config)

        depth_scale = profile.get_device().first_depth_sensor().get_depth_scale()
        sensor_dep = profile.get_device().first_depth_sensor()

        # print(f"Depth Scale is: {depth_scale}") # Should be 0.001
        # print("Trying to set Exposure")
        # exp = sensor_dep.get_option(rs.option.exposure)
        # print("exposure =  ", exp)
        # print("Setting exposure to new value")
        # exp = sensor_dep.set_option(rs.option.exposure, 10000)
        # exp = sensor_dep.get_option(rs.option.exposure)
        # print("New exposure = ", exp)
        
        self.frame_count = 0

    def record_frames(self):
        start_time = time.time()
        print(f"CAM {self.serial_number} {self.camera_name}: Starting recording...")

        while True:
            try:
                self.frame_count += 1
                record_time_start = time.time()
                # Wait for frames
                frames = self.pipeline.wait_for_frames()
                aligned_frames = self.align.process(frames)
                depth_frame = aligned_frames.get_depth_frame()
                color_frame = aligned_frames.get_color_frame()

                # Convert frames to numpy arrays
                depth_image = np.asanyarray(depth_frame.get_data())
                color_image = np.asanyarray(color_frame.get_data())
                # print(depth_image.shape, color_image.shape)

                # Save frames
                # Create a process to save data asynchronously
                save_process = Process(
                    target=save_data,
                    args=(depth_image.copy(), color_image.copy(), self.camera_dir, self.frame_count)
                )
                save_process.start()

                if self.vis:
                    cv2.imshow(f"{self.camera_name} Visualization", color_image)
                    cv2.waitKey(1)

                # depth_frame = depth_process(depth_frame, *self.depth_filters)
                
                if not depth_frame or not color_frame:
                    raise Exception("Failed to acquire frames")

                # Display progress
                if self.frame_count % 30 == 0:
                    print(f"CAM {self.serial_number}: Recorded... {int(time.time() - start_time)} seconds, {self.frame_count} frames")

                time.sleep(max(0, 1/RECORD_FPS - (time.time()-record_time_start))) # fps = RECORD_FPS

            except KeyboardInterrupt:
                print(f"CAM {self.camera_name}: Stopping recording...")
                self.pipeline.stop()

            except Exception as e:
                print(f"CAM {self.camera_name}: Error - {e}")
                break
        
    def stop_recording(self):
        self.pipeline.stop()
        self.frame_count = 0

if __name__ == "__main__":
    ctx = rs.context()
    devices = ctx.query_devices()
    print(f"Found {len(devices)} RealSense device(s)")

    for device in devices:
        serial_number = device.get_info(rs.camera_info.serial_number)
        print(f"Device: {serial_number}")
    device = devices[0]
    print("Testing device: ", device)
    # exit(0)
    
    recorder = RealSenseRecorder( device.get_info(rs.camera_info.serial_number))
    recorder.initialize_camera()
    recorder.record_frames()
