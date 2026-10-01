"""
ImageGuard - Image Conversion & Utility Functions
"""

import io
from typing import Tuple, Union
import cv2
import numpy as np
from PIL import Image

from config.settings import MAX_IMAGE_DIMENSION


def load_pil_image(file_bytes: bytes) -> Image.Image:
    """Load binary bytes into a RGB PIL Image."""
    img = Image.open(io.BytesIO(file_bytes))
    if img.mode != "RGB":
        img = img.convert("RGB")
    return img


def pil_to_cv2(pil_img: Image.Image) -> np.ndarray:
    """Convert PIL Image (RGB) to OpenCV NumPy array (BGR)."""
    rgb_arr = np.array(pil_img)
    return cv2.cvtColor(rgb_arr, cv2.COLOR_RGB2BGR)


def cv2_to_pil(cv2_img: np.ndarray) -> Image.Image:
    """Convert OpenCV NumPy array (BGR or Grayscale) to PIL Image (RGB)."""
    if len(cv2_img.shape) == 2:  # Grayscale
        return Image.fromarray(cv2_img).convert("RGB")
    rgb_arr = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb_arr)


def resize_for_processing(
    cv2_img: np.ndarray, max_dim: int = MAX_IMAGE_DIMENSION
) -> Tuple[np.ndarray, bool]:
    """
    Resize large images to maintain responsive performance while preserving aspect ratio.
    Returns (resized_image, was_resized).
    """
    h, w = cv2_img.shape[:2]
    if max(h, w) <= max_dim:
        return cv2_img, False

    scale = max_dim / float(max(h, w))
    new_w = int(w * scale)
    new_h = int(h * scale)
    resized = cv2.resize(cv2_img, (new_w, new_h), interpolation=cv2.INTER_AREA)
    return resized, True


def pil_to_bytes(pil_img: Image.Image, format: str = "PNG") -> bytes:
    """Convert PIL Image to byte buffer."""
    buf = io.BytesIO()
    pil_img.save(buf, format=format)
    return buf.getvalue()
