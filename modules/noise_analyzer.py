"""
ImageGuard - Image Noise & High-Frequency Residual Analysis Module
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple
import cv2
import numpy as np
from PIL import Image

from config.settings import DEFAULT_NOISE_KERNEL_SIZE


@dataclass
class NoiseResult:
    noise_map_pil: Image.Image
    noise_map_np: np.ndarray
    mean_noise: float
    std_noise: float
    regional_variances: List[float]
    variance_ratio: float
    is_non_uniform: bool
    summary_notes: str


def analyze_noise(
    cv2_bgr: np.ndarray,
    kernel_size: int = DEFAULT_NOISE_KERNEL_SIZE
) -> NoiseResult:
    """
    Extract noise residual map by subtracting Gaussian blurred image from original grayscale.
    Compute regional noise statistics across grid quadrants to evaluate noise uniformity.
    """
    # Convert to grayscale
    gray = cv2.cvtColor(cv2_bgr, cv2.COLOR_BGR2GRAY)
    
    # Ensure kernel_size is odd
    if kernel_size % 2 == 0:
        kernel_size += 1

    # Gaussian low-pass filter
    blurred = cv2.GaussianBlur(gray, (kernel_size, kernel_size), 0)

    # Noise residual: high-frequency details and grain
    noise_residual = cv2.absdiff(gray, blurred)

    # Compute overall noise statistics
    mean_noise = float(np.mean(noise_residual))
    std_noise = float(np.std(noise_residual))

    # Divide image into 2x2 spatial quadrants and measure noise variance in each
    h, w = noise_residual.shape
    mid_h, mid_w = h // 2, w // 2

    q1 = noise_residual[0:mid_h, 0:mid_w]
    q2 = noise_residual[0:mid_h, mid_w:w]
    q3 = noise_residual[mid_h:h, 0:mid_w]
    q4 = noise_residual[mid_h:h, mid_w:w]

    quadrants = [q1, q2, q3, q4]
    regional_variances = [float(np.var(q)) for q in quadrants]

    min_var = min(regional_variances) if min(regional_variances) > 1e-5 else 1e-5
    max_var = max(regional_variances)
    variance_ratio = max_var / min_var

    # Heuristic check for non-uniform noise (spliced images often have mismatched noise profiles)
    is_non_uniform = variance_ratio > 2.5 and std_noise > 4.0

    # Colorize residual map for clear UI visualization
    noise_normalized = cv2.normalize(noise_residual, None, 0, 255, cv2.NORM_MINMAX)
    noise_color = cv2.applyColorMap(noise_normalized, cv2.COLORMAP_JET)
    noise_rgb = cv2.cvtColor(noise_color, cv2.COLOR_BGR2RGB)
    noise_pil = Image.fromarray(noise_rgb)

    if is_non_uniform:
        notes = (
            f"Noticeable regional noise variance detected (Variance Ratio: {variance_ratio:.2f}). "
            "Inconsistent noise grain across quadrants may indicate compositing, local smoothing, or spliced regions."
        )
    else:
        notes = (
            f"Noise distribution appears uniform across quadrants (Variance Ratio: {variance_ratio:.2f}). "
            "No strong regional noise mismatches detected."
        )

    return NoiseResult(
        noise_map_pil=noise_pil,
        noise_map_np=noise_normalized,
        mean_noise=round(mean_noise, 2),
        std_noise=round(std_noise, 2),
        regional_variances=[round(v, 2) for v in regional_variances],
        variance_ratio=round(variance_ratio, 2),
        is_non_uniform=is_non_uniform,
        summary_notes=notes
    )
