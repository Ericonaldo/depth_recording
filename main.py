from multiprocessing import Process
import pyrealsense2 as rs

from realsense import RealSenseRecorder
# from zed_recorder import ZEDRecorder

class RealsenseRecordProcess(Process):
    def __init__(self, device):
        super(RealsenseRecordProcess, self).__init__()
        self.device = device

    def run(self):
        recorder = RealSenseRecorder(self.device)
        recorder.initialize_camera()
        recorder.record_frames()

def main():
    ctx = rs.context()
    devices = ctx.query_devices()
    print(f"Found {len(devices)} RealSense devices")

    processes = []
    
    for device in devices:
        serial_number = device.get_info(rs.camera_info.serial_number)
        p = RealsenseRecordProcess(serial_number)
        p.start()
        processes.append(p)
    
    # Wait for all processes to complete
    for p in processes:
        p.join()

if __name__ == "__main__":
    main()