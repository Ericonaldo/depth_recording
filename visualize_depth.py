import cv2
import os
import sys
import numpy as np
import matplotlib

def colorize_depth_map(depth_map, min_value=None, max_value=None, cmap='Spectral'):
    # Normalize the depth map to range [0, 1]
    if min_value is None:
        min_value = depth_map.min()
    if max_value is None:
        max_value = depth_map.max()
    depth = (depth_map - min_value) / (max_value - min_value)
    
    cm = matplotlib.cm.get_cmap(cmap)
    depth_map_color = cm(depth, bytes=False)[:, :, :3]
    
    return depth_map_color

def visualize_image_sequences(directories_paths, fps):
    # List all PNG files in each directory, grouped by cameras
    image_files_per_camera = []

    for directory_path in directories_paths:
        image_files = [f for f in os.listdir(directory_path) if f.endswith('.png') and f.startswith('depth_')]
        image_files = [f for f in sorted(image_files, key=lambda x:int(x.replace('.png','').split("_")[-1]))]
        
        if not image_files:
            print(f"No PNG images found in directory {directory_path}.")
            return
        image_files_per_camera.append(image_files)
    
    # Create a window to display images for each camera
    windows = [f'Camera {i+1}' for i in range(len(directories_paths))]
    for window in windows:
        cv2.namedWindow(window, cv2.WINDOW_NORMAL)

    # Move windows to different positions on the screen to avoid overlap
    window_positions = [(0, 0), (500, 0), (1000, 0), (1500, 0), (0, 500), (500, 500), (1000, 500)]  # Adjust positions as necessary
    for i, window in enumerate(windows):
        if i < len(window_positions):
            cv2.moveWindow(window, *window_positions[i])
    
    # Read and display images in sequence for each camera
    num_frames = min(image_files_per_camera)  # Assuming all cameras have the same number of frames
    
    for i in range(num_frames):
        # Read the image for each camera
        images = []
        for idx, directory_path in enumerate(directories_paths):
            image_file = image_files_per_camera[idx][i]
            image_path = os.path.join(directory_path, image_file)
            print(f"Displaying {image_path}")
            
            # Read the image
            image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
            if image is None:
                print(f"Error reading image {image_file} for camera {idx+1}. Skipping.")
                continue
            
            image = colorize_depth_map(image, min_value=0, max_value=2000)
            images.append(image)

        # Show the image in each window
        for idx, image in enumerate(images):
            cv2.imshow(windows[idx], image)

        # Wait for the appropriate amount of time based on the FPS
        key = cv2.waitKey(int(1000 / fps))  # Convert FPS to milliseconds
        if key == 27:  # Escape key to stop early
            break
    
    # Close all OpenCV windows
    cv2.destroyAllWindows()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python visualize_image_sequence.py <directory_path_1> <directory_path_2> ... <fps>")
        sys.exit(1)
    
    # Get the directory paths and FPS from command-line arguments
    directories_paths = [os.path.join('recorded_data', arg) for arg in sys.argv[1:-1]]
    fps = int(sys.argv[-1])

    # Check if the directories exist
    for directory_path in directories_paths:
        if not os.path.isdir(directory_path):
            print(f"The directory '{directory_path}' does not exist.")
            sys.exit(1)
    
    # Call the function to visualize image sequences
    visualize_image_sequences(directories_paths, fps)
