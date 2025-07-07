import cv2
import os
import sys
import numpy as np


def visualize_image_sequences(directories_paths, fps):
    # List all PNG files in each directory, grouped by cameras
    image_files_per_camera = []

    for directory_path in directories_paths:
        image_files = [
            f
            for f in os.listdir(directory_path)
            if f.endswith(".png") and f.startswith("color_")
        ]
        image_files = [
            f
            for f in sorted(
                image_files, key=lambda x: int(x.replace(".png", "").split("_")[-1])
            )
        ]

        if not image_files:
            print(f"No PNG images found in directory {directory_path}.")
            return
        image_files_per_camera.append(image_files)

    # Create a window to display images for each camera
    windows = [name.split("/")[-1] for name in directories_paths]
    for window in windows:
        cv2.namedWindow(window, cv2.WINDOW_NORMAL)

    # Move windows to different positions on the screen to avoid overlap
    window_positions = [
        (0, 0),
        (500, 0),
        (1000, 0),
        (1500, 0),
        (0, 500),
        (500, 500),
        (1000, 500),
        (1500, 500),
        (0, 1000),
        (500, 1000),
        (1000, 1000),
        (1500, 1000),
    ]  # Adjust positions as necessary
    for i, window in enumerate(windows):
        if i < len(window_positions):
            cv2.moveWindow(window, *window_positions[i])

    # Read and display images in sequence for each camera
    # Determine the maximum number of frames (longest sequence length)
    num_frames = max(len(image_files) for image_files in image_files_per_camera)

    # Read and display images in sequence for each camera
    for i in range(num_frames):
        images = []
        # For each camera, load the corresponding image if it exists
        for idx, directory_path in enumerate(directories_paths):
            # Check if the current camera has a frame for this index
            if i < len(image_files_per_camera[idx]):
                image_file = image_files_per_camera[idx][i]
                image_path = os.path.join(directory_path, image_file)
                print(f"Displaying {image_path}")

                # Read the image
                image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
                if image is None:
                    print(
                        f"Error reading image {image_file} for camera {idx+1}. Skipping."
                    )
                    continue

                images.append(image)
            else:
                # If the camera doesn't have more frames, append a black image (or leave it empty)
                images.append(
                    np.zeros_like(images[0])
                    if images
                    else np.zeros((480, 640, 3), dtype=np.uint8)
                )  # Modify size as necessary

        # Show the image in each window
        for idx, image in enumerate(images):
            cv2.imshow(windows[idx], image)

        # Wait for the appropriate amount of time based on the FPS
        key = cv2.waitKey(int(1000 / fps))  # Convert FPS to milliseconds
        if key == 27:  # Escape key to stop early
            break

    # Close all OpenCV windows
    cv2.destroyAllWindows()


def save_videos(directories_paths, fps, output_prefix="output"):
    """
    Save image sequences as videos for each camera.

    Args:
        directories_paths (list): List of directory paths containing image sequences
        fps (int): Frames per second for the output video
        output_prefix (str): Prefix for output video filenames
    """
    for idx, directory_path in enumerate(directories_paths):
        image_files = [
            f
            for f in os.listdir(directory_path)
            if f.endswith(".png") and f.startswith("color_")
        ]
        image_files = sorted(
            image_files, key=lambda x: int(x.replace(".png", "").split("_")[-1])
        )

        if not image_files:
            print(f"No PNG images found in directory {directory_path}")
            continue

        # Read first image to get dimensions
        first_image = cv2.imread(os.path.join(directory_path, image_files[0]))
        height, width = first_image.shape[:2]

        # Create video writer
        output_path = f"{output_prefix}_{idx}.mp4"
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        for image_file in image_files:
            image_path = os.path.join(directory_path, image_file)
            frame = cv2.imread(image_path)
            if frame is not None:
                out.write(frame)

        out.release()
        print(f"Saved video for camera {idx} to {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(
            "Usage: python visualize_image_sequence.py <directory_path_1> <directory_path_2> ... <fps>"
        )
        sys.exit(1)

    # Get the directory paths and FPS from command-line arguments
    directories_paths = [os.path.join("recorded_data", arg) for arg in sys.argv[1:-1]]
    fps = int(sys.argv[-1])

    # Check if the directories exist
    for directory_path in directories_paths:
        if not os.path.isdir(directory_path):
            print(f"The directory '{directory_path}' does not exist.")
            sys.exit(1)

    # Call the function to visualize image sequences
    visualize_image_sequences(directories_paths, fps)
    # save_videos(directories_paths, fps)
