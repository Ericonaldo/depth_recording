import cv2
import os
import sys

def visualize_image_sequence(directory_path, fps):
    # List all PNG files in the directory
    image_files = [f for f in sorted(os.listdir(directory_path), key=lambda x:int(x.replace('.png','').split("_")[-1])) if f.endswith('.png') and f.startswith('color_')]
    
    if not image_files:
        print("No PNG images found in the directory.")
        return

    # Create a window to display images
    cv2.namedWindow('Image Sequence', cv2.WINDOW_NORMAL)
    
    # Read and display images in sequence
    for image_file in image_files:
        image_path = os.path.join(directory_path, image_file)
        
        # Read the image
        image = cv2.imread(image_path)
        
        if image is None:
            print(f"Error reading image {image_file}. Skipping.")
            continue

        # Show the image
        cv2.imshow('Image Sequence', image)

        # Wait for the appropriate amount of time based on the FPS
        key = cv2.waitKey(int(1000 / fps))  # Convert FPS to milliseconds
        if key == 27:  # Escape key to stop early
            break
    
    # Close all OpenCV windows
    cv2.destroyAllWindows()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python visualize_image_sequence.py <directory_path> <fps>")
        sys.exit(1)
    
    # Get the directory path and FPS from command-line arguments
    directory_path = os.path.join('recorded_data', sys.argv[1])
    fps = int(sys.argv[2])

    # Check if the directory exists
    if not os.path.isdir(directory_path):
        print(f"The directory '{directory_path}' does not exist.")
        sys.exit(1)
    
    # Call the function to visualize image sequence
    visualize_image_sequence(directory_path, fps)
