import pyzed.sl as sl
import numpy as np
import time
from pathlib import Path
from datetime import datetime
from multiprocessing import Process
import cv2

ZED_FPS = 60
camera_kwargs = {
    # "VIDEO_ID": VIDEO_ID,
    "camera_scale": 1,
    "fps": 30,
}

def save_data(depth, color_image, pcd, camera_dir, frame_count):
    # np.save(str(camera_dir / f"depth_{frame_count}.npy"), depth) # 32-bit float array
    cv2.imwrite(str(camera_dir / f"depth_{frame_count}.png"), (depth*1000).astype()) # 16-bit uint array
    cv2.imwrite(str(camera_dir / f"color_{frame_count}.png"), color_image)
    np.save(str(camera_dir / f"pcd_{frame_count}.npy"), pcd) # 32-bit float array

def init_zed(fps=60, svo_file=None, 
             async_mode=False, svo_real_time=False):
    zed = sl.Camera()
    # NOTE: see https://www.stereolabs.com/docs/api/python/classpyzed_1_1sl_1_1InitParameters.html
    init_params = sl.InitParameters(svo_real_time_mode=svo_real_time and (svo_file is not None),
                                    async_image_retrieval=async_mode)
    if svo_file is not None:
        init_params.set_from_svo_file(svo_file)

    init_params.camera_resolution = sl.RESOLUTION.HD720  
    init_params.coordinate_units = sl.UNIT.METER
    # init_params.depth_mode = sl.DEPTH_MODE.PERFORMANCE
    # init_params.depth_mode = sl.DEPTH_MODE.ULTRA
    init_params.depth_mode = sl.DEPTH_MODE.NEURAL
    # init_params.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP
    init_params.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Z_UP_X_FWD

    init_params.camera_fps = fps  # Set fps at 60
    # init_params.async_image = async_mode
    # init_params.depth_mode = sl.DEPTH_MODE.PERFORMANCE

    # NOTE: see https://www.stereolabs.com/docs/api/python/classpyzed_1_1sl_1_1RuntimeParameters.html
    runtime_params = sl.RuntimeParameters()

    # Open the camera
    err = zed.open(init_params)
    if err != sl.ERROR_CODE.SUCCESS:
        print("Camera Open : " + repr(err) + ". Exit program.")
        exit()
    return zed, runtime_params

class ZedRecorder:
    def __init__(self, svo_file=None, async_mode=True, svo_real_time=False, output_path="./recorded_data"):
        self.svo_file = svo_file
        self.async_mode = async_mode
        self.svo_real_time = svo_real_time

        self.camera_name = "Zed2i"
        
        # Create output directory
        output_path = Path(output_path)
        output_path.mkdir(exist_ok=True)
        
        # Create timestamp-based directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_dir = output_path / timestamp

        # Create camera directory
        self.camera_dir = session_dir / f"camera_{self.camera_name}"
        self.camera_dir.mkdir(parents=True, exist_ok=True)

    def initialize_camera(self):
        print(f"Initializing device: {self.camera_name}")
        
        # Setup pipeline and config for each camera
        self.zed, self.runtime_param = init_zed(svo_file=self.svo_file, async_mode=self.async_mode, 
                                                svo_real_time=self.svo_real_time)
        
        camera_info = self.zed.get_camera_information()
        display_resolution = sl.Resolution(min(camera_info.camera_configuration.resolution.width, 1920), min(camera_info.camera_configuration.resolution.height, 1080))
        self.camera_info = camera_info
        self.display_resolution = display_resolution
        self.image_scale = [display_resolution.width / camera_info.camera_configuration.resolution.width
                    , display_resolution.height / camera_info.camera_configuration.resolution.height]
        # cv_viewer.render_2D(image_left_ocv,image_scale, bodies.body_list, body_param.enable_tracking, body_param.body_format)
        self.image = sl.Mat()
        self.image_R = sl.Mat()
        self.ptcloud = sl.Mat()
        self.depth_img = sl.Mat()
        self.depth = sl.Mat()
        self.normal_map = sl.Mat()
        
        self.frame_count = 0

    def record_frames(self, record_path):
        start_time = time.time()
        print(f"CAM {self.camera_name}: Starting recording...")

        svo_filename = record_path + "zed" + ".svo"
        recording_param = sl.RecordingParameters(
            svo_filename, sl.SVO_COMPRESSION_MODE.H264
        )
        err = self.zed.enable_recording(recording_param)

        if err != sl.ERROR_CODE.SUCCESS:
            print("Recording ZED : ", err)
            exit(1)

        print("SVO is Recording, use Ctrl-C to stop.") # Start recording SVO, stop with Ctrl-C command
        frames_recorded = 0

        while True:
            if self.zed.grab(self.runtime_param) == sl.ERROR_CODE.SUCCESS : # Check that a new image is successfully acquired
                # Retrieve left image
                self.zed.retrieve_image(self.image, sl.VIEW.LEFT, sl.MEM.CPU, self.display_resolution)
                self.zed.retrieve_image(self.image_R, sl.VIEW.RIGHT, sl.MEM.CPU, self.display_resolution)

                # self.zed.retrieve_image(self.depth_img, sl.VIEW.DEPTH, ) # uint8
                # depth_img_np = np.array(self.depth_img.get_data())
                self.zed.retrieve_measure(self.depth, sl.MEASURE.DEPTH, ) # uint32, aligned to the left image
                self.zed.retrieve_measure(self.ptcloud, sl.MEASURE.XYZ, )
                self.zed.retrieve_measure(self.normal_map, sl.MEASURE.NORMALS)

                ptcloud_np = np.array(self.ptcloud.get_data())
                depth_np = np.array(self.depth.get_data())
                normal_map_np = np.array(self.normal_map.get_data())

                # Save frames
                # Create a process to save data asynchronously
                save_process = Process(
                    target=save_data,
                    args=(depth_np.copy(), normal_map_np.copy(), ptcloud_np.copy(), self.camera_dir, self.frame_count)
                )
                save_process.start()

                self.frame_count += 1

                # Display progress
                if self.frame_count % 30 == 0:
                    print(f"CAM {self.camera_name}: Recorded... {int(time.time() - start_time)} seconds, {self.frame_count} frames")
        
    def stop_record(self):
        self.zed.disable_recording()

    def __del__(self):
        self.image.free(sl.MEM.CPU)
        self.image_R.free(sl.MEM.CPU)
        self.ptcloud.free(sl.MEM.CPU)
        # self.depth_img.free(sl.MEM.CPU)
        self.depth.free(sl.MEM.CPU)
        self.normal_map.free(sl.MEM.CPU)

        self.zed.disable_body_tracking()
        self.zed.disable_positional_tracking()
        self.zed.close()

if __name__ == "__main__":
    recorder = ZedRecorder()
    recorder.initialize_camera()
    recorder.record_frames()