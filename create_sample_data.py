"""
ImageGuard - Utility Script to Generate Controlled Synthetic Demonstration Images
"""

import cv2
import numpy as np

from config.settings import SAMPLE_IMAGES_DIR


def generate_sample_dataset():
    """
    Generate synthetic test images for demonstration:
    1. sample_original.jpg - Pristine image with distinct shapes and textures.
    2. sample_copy_move.jpg - Controlled copy-move image (circle object cloned to another position).
    3. sample_recompressed.jpg - Low quality re-compressed image.
    4. sample_resized.jpg - Rescaled image.
    """
    SAMPLE_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Generating synthetic sample images in: {SAMPLE_IMAGES_DIR}")

    # Canvas dimensions
    w, h = 800, 600
    canvas = np.zeros((h, w, 3), dtype=np.uint8)

    # Gradient background
    for y in range(h):
        canvas[y, :, 0] = int(y / h * 180)  # Blue
        canvas[y, :, 1] = int(y / h * 120)  # Green
        canvas[y, :, 2] = 200               # Red

    # Add background noise/texture
    noise = np.random.normal(0, 10, (h, w, 3)).astype(np.int16)
    canvas = np.clip(canvas.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    # Draw distinct shape (Star / Sun circle)
    cv2.circle(canvas, (200, 200), 50, (0, 255, 255), -1)
    cv2.rectangle(canvas, (400, 350), (550, 500), (255, 100, 0), -1)
    cv2.putText(canvas, "ImageGuard Forensics", (50, 550), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)

    # 1. Save Pristine Original
    orig_path = SAMPLE_IMAGES_DIR / "sample_original.jpg"
    cv2.imwrite(str(orig_path), canvas, [cv2.IMWRITE_JPEG_QUALITY, 95])
    print(f"Created: {orig_path}")

    # 2. Save Copy-Move Manipulation (clone circle from 200,200 to 600,200)
    copy_move_img = canvas.copy()
    circle_patch = copy_move_img[140:260, 140:260].copy()
    copy_move_img[140:260, 540:660] = circle_patch

    cm_path = SAMPLE_IMAGES_DIR / "sample_copy_move.jpg"
    cv2.imwrite(str(cm_path), copy_move_img, [cv2.IMWRITE_JPEG_QUALITY, 95])
    print(f"Created: {cm_path}")

    # 3. Save Recompressed Image (Low quality 30%)
    recomp_path = SAMPLE_IMAGES_DIR / "sample_recompressed.jpg"
    cv2.imwrite(str(recomp_path), canvas, [cv2.IMWRITE_JPEG_QUALITY, 30])
    print(f"Created: {recomp_path}")

    # 4. Save Resized Image
    small = cv2.resize(canvas, (400, 300), interpolation=cv2.INTER_AREA)
    resized_img = cv2.resize(small, (800, 600), interpolation=cv2.INTER_CUBIC)
    resized_path = SAMPLE_IMAGES_DIR / "sample_resized.jpg"
    cv2.imwrite(str(resized_path), resized_img, [cv2.IMWRITE_JPEG_QUALITY, 95])
    print(f"Created: {resized_path}")

    print("Sample dataset generation complete.")


if __name__ == "__main__":
    generate_sample_dataset()
