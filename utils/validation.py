"""
ImageGuard - Image Ingestion Validation Module
"""

import io
from typing import Tuple
from PIL import Image

from config.settings import ALLOWED_EXTENSIONS, MAX_FILE_SIZE_MB, MAX_IMAGE_PIXELS


def validate_image_file(file_bytes: bytes, filename: str) -> Tuple[bool, str]:
    """
    Validate uploaded image bytes against format, size, and corruption constraints.
    
    Returns:
        (is_valid, error_message)
    """
    if not file_bytes or len(file_bytes) == 0:
        return False, "File is empty."

    # Size check
    size_mb = len(file_bytes) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        return False, f"File size ({size_mb:.1f} MB) exceeds maximum allowed limit of {MAX_FILE_SIZE_MB} MB."

    # Extension check
    ext = filename.split(".")[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"Unsupported file extension '.{ext}'. Supported extensions: {', '.join(sorted(ALLOWED_EXTENSIONS))}."

    # Image corruption / readability check
    try:
        with Image.open(io.BytesIO(file_bytes)) as img:
            image_format = (img.format or "").upper()
            width, height = img.size
            img.verify()
        if width * height > MAX_IMAGE_PIXELS:
            return False, (
                f"Image dimensions ({width} x {height}) exceed the maximum allowed "
                f"pixel count of {MAX_IMAGE_PIXELS:,}."
            )
        expected_formats = {
            "jpg": {"JPEG"}, "jpeg": {"JPEG"}, "png": {"PNG"},
            "webp": {"WEBP"}, "tif": {"TIFF"}, "tiff": {"TIFF"},
        }
        if image_format not in expected_formats.get(ext, set()):
            return False, "Image content does not match its file extension."
    except Exception as e:
        return False, f"Corrupted or invalid image file. Detailed error: {str(e)}"

    return True, "Valid image file."
