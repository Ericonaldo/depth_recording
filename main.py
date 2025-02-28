from multiprocessing import Process
from pathlib import Path
import argparse
import time

try:
    from realsense import RealSenseRecorder, serial_number_dict
except ImportError:
    pass

try:
    from zed import ZedRecorder
except ImportError:
    pass

try:
    from kinect import KinectRecorder
except ImportError:
    pass

class KinectRecordProcess(Process):
    def __init__(self, vis=False):
        super(KinectRecordProcess, self).__init__()
        self.vis = vis

    def run(self):
        recorder = KinectRecorder(self.vis)
        recorder.initialize_camera()
        recorder.record_frames()

class RealsenseRecordProcess(Process):
    def __init__(self, device, vis=False):
        super(RealsenseRecordProcess, self).__init__()
        self.device = device
        self.vis = vis

    def run(self):
        recorder = RealSenseRecorder(self.device, self.vis)
        recorder.initialize_camera()
        recorder.record_frames()

class ZedRecordProcess(Process):
    def __init__(self, vis=False):
        super(ZedRecordProcess, self).__init__()
        self.vis = vis

    def run(self):
        recorder = ZedRecorder(self.vis)
        recorder.initialize_camera()
        svo_dir = Path('./tmp/')
        svo_dir.mkdir(exist_ok=True)
        recorder.record_frames(str(svo_dir))

def main(args):
    processes = []
    if args.rs:
        try:
            import pyrealsense2.pyrealsense2 as rs
        except ImportError:
            import pyrealsense2 as rs
        ctx = rs.context()
        devices = ctx.query_devices()
        print(f"Found {len(devices)} RealSense devices")
        
        for device in devices:
            serial_number = device.get_info(rs.camera_info.serial_number)
            p = RealsenseRecordProcess(serial_number, vis=str.lower(args.vis) in serial_number_dict[serial_number])
            p.start()
            processes.append(p)
            time.sleep(1)

    if args.zed:
        p = ZedRecordProcess(str.lower(args.vis) in "zed")
        p.start()
        processes.append(p)
        time.sleep(0.8)

    if args.kn:
        p = KinectRecordProcess(str.lower(args.vis) in "kn")
        p.start()
        processes.append(p)
    
    # Wait for all processes to complete
    for p in processes:
        p.join()


def parse_args():
        parser = argparse.ArgumentParser(description='Record from RealSense and ZED cameras')
        parser.add_argument('--rs', action='store_true', help='Record from RealSense cameras')
        parser.add_argument('--zed', action='store_true', help='Record from ZED camera')
        parser.add_argument('--kn', action='store_true', help='Record from Azure Kinect camera')
        parser.add_argument('--vis', type=str, help='Visualization, default using 455', default="455")
        return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if not (args.rs or args.zed or args.kn):
        print("Please specify at least one camera type (--rs or --zed)")
        exit(1)
    main(args)
