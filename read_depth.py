import cv2
import numpy as np

def read_depth_image(filepath):
    # Read the depth image
    depth_img = cv2.imread(filepath, cv2.IMREAD_UNCHANGED)
    
    # Check if image was successfully loaded
    if depth_img is None:
        raise ValueError(f"Failed to load depth image from {filepath}")
    
    import ipdb; ipdb.set_trace()
    
    # If the image is 16-bit, convert to float for better visualization
    if depth_img.dtype == np.uint16:
        # Convert to float and scale to meters (assuming depth is in millimeters)
        depth_img = depth_img.astype(float) / 1000.0
    
    return depth_img

# Example usage
if __name__ == "__main__":
    # Replace with your depth image path
    depth_image_path = "/home/mhliu/depth_recording/recorded_data/20250208_155511/camera_242322077064/depth_72.png"
    depth_data = read_depth_image(depth_image_path)
    
    # Print shape and depth range
    print(f"Depth image shape: {depth_data.shape}")
    print(f"Depth range: {depth_data.min():.2f}m to {depth_data.max():.2f}m")