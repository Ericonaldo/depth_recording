import os
import argparse


def delete_files(directory, idx=None, min_idx=None, max_idx=None):
    # Validate input
    if (min_idx is not None and max_idx is None) or (
        min_idx is None and max_idx is not None
    ):
        print("Both min_idx and max_idx should be provided together.")
        return

    # List all files in the given directory
    for filename in os.listdir(directory):
        # Check if the file matches the 'depth_idx.png' or 'color_idx.png' pattern
        if filename.endswith(".png") or filename.endswith(".npy"):
            # Extract the idx from the filename (depth_idx.png or color_idx.png)
            try:
                file_name_split = filename.split("_")
                prefix, file_idx_str = "_".join(file_name_split[0]), file_name_split[-1]
                file_idx = int(file_idx_str.split(".")[0])
            except ValueError:
                continue  # Skip files that don't match the expected pattern

            # Check if idx or the range of idx is valid
            if idx is not None and file_idx == idx:
                print(f"Deleting file: {filename}")
                os.remove(os.path.join(directory, filename))

            elif min_idx is not None and max_idx is not None:
                if min_idx <= file_idx <= max_idx:
                    print(f"Deleting file: {filename}")
                    os.remove(os.path.join(directory, filename))


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Delete files based on index or range of indices."
    )
    parser.add_argument("directory", type=str, help="Directory containing the files.")
    parser.add_argument("--idx", type=int, help="Delete files with a specific index.")
    parser.add_argument(
        "--min_idx", type=int, help="Minimum index for range of files to delete."
    )
    parser.add_argument(
        "--max_idx", type=int, help="Maximum index for range of files to delete."
    )

    args = parser.parse_args()

    # Check if only idx is provided or both min_idx and max_idx
    if args.idx is not None:
        delete_files(args.directory, idx=args.idx)
    if args.min_idx is not None and args.max_idx is not None:
        delete_files(args.directory, min_idx=args.min_idx, max_idx=args.max_idx)
    if args.idx is None and (args.min_idx is None or args.max_idx is None):
        print("You must specify either --idx or both --min_idx and --max_idx.")


if __name__ == "__main__":
    main()
