import sys
import subprocess
import os


def main():
    if len(sys.argv) != 3:
        print("Usage: python translate_bash.py <timestep> <fps>")
        sys.exit(1)

    # Get the base directory (the equivalent of $1 in the bash script)
    base_directory = os.path.join("recorded_data", sys.argv[1])

    # List of camera directories
    camera_directories = os.listdir(base_directory)
    camera_directories = [
        os.path.join(sys.argv[1], directory) for directory in camera_directories
    ]

    # FPS value
    fps = int(sys.argv[2])

    # Create the command to run visualize_depth.py with the constructed arguments
    command = (
        ["python", "visualization/visualize_depth.py"] + camera_directories + [str(fps)]
    )

    # Run the command
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running the command: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
