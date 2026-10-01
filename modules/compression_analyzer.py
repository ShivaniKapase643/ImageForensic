"""
ImageGuard - Image Compression & Quantization Artifact Analysis Module
"""

import io
from dataclasses import dataclass
from typing import Optional
import cv2
import numpy as np
from PIL import Image


@dataclass
class CompressionResult:
    image_format: str
    is_jpeg: bool
    estimated_jpeg_quality: Optional[int]
    blockiness_score: float
    recompression_anomalous: bool
    summary_notes: str


def analyze_compression(
    file_bytes: bytes,
    cv2_bgr: np.ndarray,
    format_name: str
) -> CompressionResult:
    """
    Analyze image compression characteristics including 8x8 block boundary discontinuities
    and JPEG quantization characteristics.
    """
    is_jpeg = format_name.upper() in ["JPEG", "JPG"]
    estimated_quality = None

    # Calculate 8x8 DCT Blockiness Metric
    # Sum absolute difference along 8-pixel grid boundaries vs non-boundary pixels
    gray = cv2.cvtColor(cv2_bgr, cv2.COLOR_BGR2GRAY).astype(np.float32)
    h, w = gray.shape

    # Vertical boundary differences (columns x=8,16,24...)
    boundary_cols = np.abs(gray[:, 7:-1:8] - gray[:, 8::8])
    non_boundary_cols = np.abs(gray[:, 3:-1:8] - gray[:, 4::8])
    
    mean_boundary_diff = float(np.mean(boundary_cols)) if boundary_cols.size > 0 else 0.0
    mean_non_boundary_diff = float(np.mean(non_boundary_cols)) if non_boundary_cols.size > 0 else 1.0

    blockiness_score = mean_boundary_diff / (mean_non_boundary_diff + 1e-5)

    # Heuristic JPEG quality estimation from Pillow quantization tables if present
    if is_jpeg:
        try:
            with Image.open(io.BytesIO(file_bytes)) as img:
                qtables = getattr(img, "quant_tables", None)
                if qtables and len(qtables) > 0:
                    q_sum = float(np.sum(qtables[0]))
                    # Typical standard JPEG luminance table sums range from ~200 (100% quality) to ~2000 (50% quality)
                    est_q = max(1, min(100, int(100 - (q_sum - 192) / 30.0)))
                    estimated_quality = est_q
        except Exception:
            estimated_quality = None

    recompression_anomalous = blockiness_score > 1.45

    if is_jpeg:
        q_str = f"Estimated Quality: ~{estimated_quality}%" if estimated_quality else "Quantization tables non-standard or missing"
        notes = (
            f"JPEG Compression Analysis ({q_str}). "
            f"Grid Blockiness Metric: {blockiness_score:.2f}. "
        )
        if recompression_anomalous:
            notes += "Elevated 8x8 grid boundary discontinuity observed, indicating noticeable JPEG compression artifacts."
        else:
            notes += "Grid boundary transitions align smoothly without severe blocking artifacts."
    else:
        notes = (
            f"Format is {format_name} (Lossless / Non-JPEG). "
            f"Blockiness Metric: {blockiness_score:.2f}. Standard JPEG block quantization does not directly apply."
        )

    return CompressionResult(
        image_format=format_name,
        is_jpeg=is_jpeg,
        estimated_jpeg_quality=estimated_quality,
        blockiness_score=round(blockiness_score, 2),
        recompression_anomalous=recompression_anomalous,
        summary_notes=notes
    )
