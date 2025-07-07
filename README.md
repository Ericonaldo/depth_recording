# Depth Recording

A multi-camera depth recording system for simultaneous data capture from various 3D cameras. This system enables researchers to collect synchronized depth, color, and point cloud data from Intel RealSense, Stereolabs ZED, Azure Kinect, and Mechmind cameras.

## Features

- **Multi-camera synchronization**: Record from multiple cameras simultaneously using multiprocessing
- **Diverse camera support**: Intel RealSense (L515, D405, D415, D435, D455), Stereolabs ZED2i, Azure Kinect, and Mechmind industrial cameras
- **Rich data capture**: Depth maps, color images, point clouds, surface normals, and IR data
- **Real-time visualization**: Live preview capabilities for each camera stream
- **Batch processing**: Tools for processing and visualizing large datasets
- **Flexible configuration**: Configurable frame rates, resolutions, and camera-specific settings
- **Data management**: Organized file structure with cleanup utilities

## Requirements

### Software Dependencies
```
opencv-python
```

### Camera SDKs
- **Intel RealSense**: pyrealsense2 SDK
- **Stereolabs ZED**: ZED SDK with Python bindings
- **Azure Kinect**: pyk4a Python wrapper
- **Mechmind**: MechEye SDK

### System Requirements
- Python 3.7+
- USB 3.0+ ports for camera connections
- Sufficient disk space for data storage

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd depth_recording
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Install camera-specific SDKs according to manufacturer documentation.

## Project Structure

```
depth_recording/
├── main.py                    # Main entry point for multi-camera recording
├── cameras/                   # Camera implementations
│   ├── realsense.py          # Intel RealSense cameras
│   ├── zed.py                # Stereolabs ZED cameras
│   ├── kinect.py             # Azure Kinect cameras
│   └── mechmind.py           # Mechmind industrial cameras
├── utils/                     # Utility functions
│   ├── delete.py             # File deletion and cleanup
│   ├── read_depth.py         # Depth data reading utilities
│   └── monitor_usb.py        # USB bandwidth monitoring
├── visualization/             # Visualization tools
│   ├── visualize_depth.py    # Single-session depth visualization
│   ├── visualize_color.py    # Single-session color visualization
│   ├── batch_visualize_depth.py  # Batch depth visualization
│   └── batch_visualize_color.py  # Batch color visualization
└── scripts/                   # Shell scripts for batch operations
    ├── delete_zed_frames.sh   # ZED data cleanup
    └── generate_zed_all_modes.sh  # ZED multi-mode processing
```

## Usage

### Basic Recording

Record from all connected RealSense cameras:
```bash
python main.py --rs
```

Record from ZED camera:
```bash
python main.py --zed
```

Record from Azure Kinect:
```bash
python main.py --kn
```

Record from multiple camera types simultaneously:
```bash
python main.py --rs --zed --kn
```

### Visualization During Recording

Enable visualization for specific cameras:
```bash
python main.py --rs --zed --vis "455,zed"
```

### Individual Camera Operation

Run cameras independently for testing or specific configurations:
```bash
python cameras/realsense.py
python cameras/zed.py --depth_mode quality
python cameras/kinect.py
python cameras/mechmind.py --interval 2.0
```

### Data Visualization

Visualize recorded sessions:
```bash
python visualization/visualize_depth.py <session_folder> <fps>
python visualization/batch_visualize_depth.py <timestamp> <fps>
```

## Supported Cameras

### Intel RealSense
- **Models**: L515, D405, D415, D435, D455
- **Depth Resolution**: 1024×768 (L515), 1280×720 (others)
- **Color Resolution**: Up to 1920×1080
- **Frame Rate**: 30 FPS (configurable)
- **Features**: Hardware-accelerated depth processing, multiple stream alignment

### Stereolabs ZED2i
- **Depth Resolution**: 1280×720
- **Depth Modes**: Performance, Quality, Ultra, Neural
- **Frame Rate**: 30 FPS
- **Features**: Stereo depth estimation, SVO recording, point cloud generation

### Azure Kinect
- **Depth Resolution**: Wide FOV unbinned
- **Color Resolution**: 1920×1080
- **Frame Rate**: 5-30 FPS
- **Features**: Time-of-flight depth sensing, synchronized color and depth

### Mechmind Industrial Cameras
- **Models**: Configurable via IP address
- **Features**: High-precision industrial 3D imaging, textured point clouds
- **Data Output**: Raw depth, point clouds, surface normals

## Data Output

### File Organization
```
recorded_data/
└── YYYYMMDD_HHMM/              # Timestamp-based session folder
    ├── camera_realsense_455/    # Per-camera directories
    │   ├── depth_000.png        # 16-bit depth images
    │   ├── color_000.png        # 8-bit color images
    │   └── ...
    ├── camera_zed2i_quality/
    │   ├── raw_depth_000.npy    # 32-bit float depth arrays
    │   ├── depth_000.png        # 16-bit depth images
    │   ├── color_000.png        # Color images
    │   ├── pcd_000.npy          # Point cloud data
    │   └── normal_000.npy       # Surface normals
    └── ...
```

### Data Formats
- **Depth**: PNG (16-bit) and NPY (32-bit float)
- **Color**: PNG (8-bit RGB/BGR)
- **Point Clouds**: NPY arrays (X, Y, Z coordinates)
- **Normals**: NPY arrays (surface normal vectors)
- **IR**: PNG (infrared images where available)

## Utilities and Tools

### Visualization Tools
- **Real-time preview**: Live camera feeds during recording
- **Batch visualization**: Process multiple sessions efficiently
- **Depth colorization**: False-color depth map visualization
- **Multi-camera sync**: Synchronized playback of multiple camera streams

### Data Management
- **Selective deletion**: Remove specific frame ranges or indices
- **Batch processing**: Process multiple recording sessions
- **USB monitoring**: Track bandwidth usage during recording
- **Storage optimization**: Efficient file organization and cleanup

## Contributing

We welcome contributions to extend camera support and add new features!

### Adding New Cameras
1. Create a new camera implementation in `cameras/`
2. Follow the existing pattern: `initialize_camera()`, `record_frames()`, `stop_recording()`
3. Add multiprocessing support in `main.py`
4. Update this README with camera specifications

### Code Style
- Follow existing code organization and naming conventions
- Use type hints where appropriate
- Add docstrings for new functions and classes
- Test with actual hardware when possible

### Development Setup
```bash
# Create development environment
pip install -r requirements.txt

# Run individual camera modules for testing
python cameras/your_camera.py
```

## Research Applications

This system has been designed for research applications requiring:
- **Multi-modal sensing**: Combining different depth sensing technologies
- **Temporal synchronization**: Capturing data from multiple viewpoints simultaneously  
- **Dataset creation**: Building large-scale 3D vision datasets
- **Sensor fusion**: Comparing and combining data from different camera types
- **Real-time processing**: Live depth and color stream analysis

## License

This project is open source and available under the MIT License.

## Citation

If you use this system in your research, please cite:
```bibtex
@software{depth_recording,
  title={Multi-Camera Depth Recording System},
  author={Minghuan Liu},
  year={2025},
  url={https://github.com/Ericonaldo/depth_recording}
}
```
