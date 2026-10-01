"""
ImageGuard - Error Level Analysis (ELA) Module
"""

import io
from dataclasses import dataclass
from typing import Tuple
import numpy as np
from PIL import Image, ImageChops, ImageEnhance

from config.settings import DEFAULT_ELA_QUALITY, DEFAULT_ELA_SCALE


@dataclass
class ELAResult:
    ela_pil_image: Image.Image
    ela_np_array: np.ndarray
    mean_difference: float
    max_difference: float
    std_difference: float
    is_anomalous: bool
    summary_notes: str


def perform_ela(
    pil_img: Image.Image,
    quality: int = DEFAULT_ELA_QUALITY,
    scale: int = DEFAULT_ELA_SCALE,
    is_jpeg: bool = True
) -> ELAResult:
    """
    Perform Error Level Analysis (ELA) on input PIL image.
    
    Process:
    1. Re-save image as JPEG at specified quality in-memory.
    2. Compute absolute difference between original and recompressed image.
    3. Scale residual brightness for visual inspection.
    4. Compute regional error distribution statistics.
    """
    # Ensure RGB mode
    if pil_img.mode != "RGB":
        pil_img = pil_img.convert("RGB")

    # Re-save to JPEG buffer
    buffer = io.BytesIO()
    pil_img.save(buffer, format="JPEG", quality=quality)
    buffer.seek(0)
    recompressed = Image.open(buffer)

    # Calculate absolute difference
    diff = ImageChops.difference(pil_img, recompressed)
    
    # Scale difference image for visual enhancement
    extrema = diff.getextrema()
    max_diff_channel = max([ex[1] for ex in extrema]) if extrema else 1
    if max_diff_channel == 0:
        max_diff_channel = 1

    # Enhance difference contrast
    enhancer = ImageEnhance.Brightness(diff)
    ela_img = enhancer.enhance(scale)

    # Convert difference to numpy array for statistics
    diff_arr = np.array(diff, dtype=np.float32)
    mean_diff = float(np.mean(diff_arr))
    max_diff = float(np.max(diff_arr))
    std_diff = float(np.std(diff_arr))

    # Heuristic check for high local standard deviation / high residual variance
    is_anomalous = std_diff > 12.0 or mean_diff > 15.0

    notes = ""
    if not is_jpeg:
        notes += (
            "Note: The uploaded image is non-JPEG (e.g. PNG/WEBP). Conventional ELA is calculated by re-compressing "
            "the image to JPEG format. Higher uniform residuals may occur across the whole canvas due to lossy conversion.\n\n"
        )
    
    if is_anomalous:
        notes += (
            "High variance or non-uniform brightness residuals detected in ELA visualization. "
            "Uneven patterns may indicate regions with differing JPEG compression histories."
        )
    else:
        notes += (
            "ELA residual distribution appears consistent across the image layout. "
            "No obvious localized re-compression variance detected."
        )

    ela_np = np.array(ela_img)

    return ELAResult(
        ela_pil_image=ela_img,
        ela_np_array=ela_np,
        mean_difference=round(mean_diff, 2),
        max_difference=round(max_diff, 2),
        std_difference=round(std_diff, 2),
        is_anomalous=is_anomalous,
        summary_notes=notes
    )
