from multiprocessing import Process
import pyrealsense2 as rs
from pathlib import Path
import argparse

try:
    from realsense import RealSenseRecorder
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
    def __init__(self):
        super(KinectRecordProcess, self).__init__()

    def run(self):
        recorder = KinectRecorder()
        recorder.initialize_camera()
        recorder.record_frames()

class RealsenseRecordProcess(Process):
    def __init__(self, device):
        super(RealsenseRecordProcess, self).__init__()
        self.device = device

    def run(self):
        recorder = RealSenseRecorder(self.device)
        recorder.initialize_camera()
        recorder.record_frames()

class ZedRecordProcess(Process):
    def __init__(self):
        super(ZedRecordProcess, self).__init__()

    def run(self):
        recorder = ZedRecorder()
        recorder.initialize_camera()
        svo_dir = Path('./tmp/')
        svo_dir.mkdir(exist_ok=True)
        recorder.record_frames(str(svo_dir))

def main(args):
    if args.rs:
        ctx = rs.context()
        devices = ctx.query_devices()
        print(f"Found {len(devices)} RealSense devices")

        processes = []
        
        for device in devices:
            serial_number = device.get_info(rs.camera_info.serial_number)
            p = RealsenseRecordProcess(serial_number)
            p.start()
            processes.append(p)

    if args.zed:
        p = ZedRecordProcess()
        p.start()
        processes.append(p)

    if args.kn:
        p = KinectRecordProcess()
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
        return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if not (args.rs or args.zed or args.azure):
        print("Please specify at least one camera type (--rs or --zed)")
        exit(1)
    main(args)