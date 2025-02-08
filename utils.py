import cv2


def save_data(depth_image, color_image, camera_dir, frame_count):
    cv2.imwrite(str(camera_dir / f"depth_{frame_count}.png"), depth_image)
    cv2.imwrite(str(camera_dir / f"color_{frame_count}.png"), color_image)