from mecheye.shared import *
from mecheye.area_scan_3d_camera import *
from mecheye.area_scan_3d_camera_utils import *

from multiprocessing import Process
from pathlib import Path
import argparse
import numpy as np
import cv2
import time
from datetime import datetime
import imageio

from visualize_depth import colorize_depth_map

CAM_LIST = {'192.168.23.100': 'lsr-s',
            # '192.168.23.101': 'welding', 
            # '192.168.23.102': 'None', 
}


def save_data(color, depth, pcd, normal, camera_dir, frame_count):
    cv2.imwrite(str(camera_dir / f"color_{frame_count}.png"), color)
    np.save(str(camera_dir / f"raw_depth_{frame_count}.npy"), depth) # 32-bit float array

    # depth_img = depth * 1000
    # depth_img = np.nan_to_num(depth_img, 0)
    # depth_img[depth_img > 65535] = 65535
    # depth_img[depth_img < 1e-5] = 0
    
    # Convert depth to uint16 and save
    # cv2.imwrite(str(camera_dir / f"depth_{frame_count}.png"), depth_img.astype(np.uint16)) # 16-bit uint array
    cv2.imwrite(str(camera_dir / f"depth_{frame_count}.png"), depth) # 16-bit uint array
    np.save(str(camera_dir / f"pcd_{frame_count}.npy"), pcd) # 32-bit float array
    np.save(str(camera_dir / f"normal_{frame_count}.npy"), normal) # 32-bit float array

def init_mecheye(ip):
    camera = Camera()
    camera.connect(ip)

    return camera

def align_depth_to_color(camera, depth, color):
    intrinsic = CameraIntrinsics()
    camera.get_camera_intrinsics(intrinsic)
    depth_matrix = np.zeros((3, 3))
    depth_matrix[0, 0] = intrinsic.depth.camera_matrix.fx
    depth_matrix[1, 1] = intrinsic.depth.camera_matrix.fy
    depth_matrix[0, 2] = intrinsic.depth.camera_matrix.cx
    depth_matrix[1, 2] = intrinsic.depth.camera_matrix.cy
    depth_matrix[2, 2] = 1.0

    texture_matrix = np.zeros((3, 3))
    texture_matrix[0, 0] = intrinsic.texture.camera_matrix.fx
    texture_matrix[1, 1] = intrinsic.texture.camera_matrix.fy
    texture_matrix[0, 2] = intrinsic.texture.camera_matrix.cx
    texture_matrix[1, 2] = intrinsic.texture.camera_matrix.cy
    texture_matrix[2, 2] = 1.0

    translation = np.array(intrinsic.depth_to_texture.translation)
    rotation = np.array(intrinsic.depth_to_texture.rotation)

    # Get image dimensions
    height, width = depth.shape
    height_color, width_color = color.shape[:2]
    
    # Create output mapped image
    mapped_image = np.zeros((height_color, width_color))

    for y in range(height):
        for x in range(width):
            if depth[y, x] > 0:  # Only process valid depth points
                # Convert depth point to 3D coordinates
                depth_point = np.array([
                    (x - depth_matrix[0,2]) / depth_matrix[0,0],
                    (y - depth_matrix[1,2]) / depth_matrix[1,1],
                    1.0
                ]) * depth[y, x]

                # Transform point to texture space
                texture_point = np.dot(rotation, depth_point) + translation
                
                # Project to texture image coordinates
                texture_image_point = np.dot(texture_matrix, texture_point)
                
                # Perspective division
                if texture_image_point[2] != 0:
                    texture_x = int(texture_image_point[0] / texture_image_point[2])
                    texture_y = int(texture_image_point[1] / texture_image_point[2])
                    
                    # Check if point is within image bounds
                    if 0 <= texture_x < width_color and 0 <= texture_y < height_color:
                        mapped_image[texture_y, texture_x] = depth[y, x]

    return mapped_image

class MecheyeRecorder:
    def __init__(self, ip, interval, vis=False, output_path="./mech_data"):
        self.ip = ip
        self.camera_name = CAM_LIST[ip]
        self.vis = vis
        self.interval = interval
        
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
        self.device = init_mecheye(self.ip)
        print(f"{self.camera_name} initialized successfully")

    def record_frames(self):
        start_time = time.time()
        print(f"CAM {self.camera_name}: Starting recording...")

        try:
            while True:
                frame2d_and_3d = Frame2DAnd3D()
                self.device.capture_2d_and_3d(frame2d_and_3d)

                textured_pcd = frame2d_and_3d.get_textured_point_cloud_with_normals()
                depth_map = frame2d_and_3d.frame_3d().get_depth_map()
                rgb_map = frame2d_and_3d.frame_2d().get_color_image()
                depth = depth_map.data()
                depth = np.nan_to_num(depth, 0)
                color = rgb_map.data()
                depth = align_depth_to_color(self.device, depth, color)
                # print(depth.shape, depth.min(), depth.max())
                # depth = colorize_depth_map(depth, min_value=0, max_value=2000)

                depth = cv2.normalize(depth, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
                depth = cv2.applyColorMap(depth, cv2.COLORMAP_JET)

                pcd = textured_pcd.vertices()
                pcd_color = textured_pcd.colors()
                pcds = np.concatenate((pcd, pcd_color), axis=-1)
                normals = textured_pcd.normals()

                # Save frames asynchronously
                save_process = Process(
                    target=save_data,
                    args=(color.copy(), depth.copy(), pcds.copy(), normals.copy(),
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
                
                time.sleep(self.interval)

        except KeyboardInterrupt:
            print("\nRecording stopped by user")
            self.stop_record()

    def stop_record(self):
        self.device.disconnect()

    def __del__(self):
        self.stop_record()

class MecheyeRecordProcess(Process):
    def __init__(self, ip, interval, vis=False):
        super(MecheyeRecordProcess, self).__init__()
        self.vis = vis
        self.ip = ip
        self.interval = interval

    def run(self):
        recorder = MecheyeRecorder(self.ip, self.interval, self.vis)
        recorder.initialize_camera()
        recorder.record_frames()

def main(args):
    processes = []
        
    for ip in CAM_LIST.keys():
        p = MecheyeRecordProcess(ip, interval=args.interval, vis=str.lower(args.vis) in CAM_LIST[ip])
        p.start()
        processes.append(p)
        # time.sleep(1)
    
    # Wait for all processes to complete
    for p in processes:
        p.join()


def parse_args():
        parser = argparse.ArgumentParser(description='Record from MechMind cameras')
        parser.add_argument('--interval', type=float, help='Interval time', default=4)
        parser.add_argument('--vis', type=str, help='Visualization', default="none")
        return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(args)
