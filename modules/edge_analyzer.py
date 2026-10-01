"""
ImageGuard - Canny Edge Detection & Boundary Analysis Module
"""

from dataclasses import dataclass
import cv2
import numpy as np
from PIL import Image

from config.settings import DEFAULT_CANNY_HIGH, DEFAULT_CANNY_LOW


@dataclass
class EdgeResult:
    edge_map_pil: Image.Image
    edge_map_np: np.ndarray
    edge_density_pct: float
    low_threshold: int
    high_threshold: int
    summary_notes: str


def detect_edges(
    cv2_bgr: np.ndarray,
    low_threshold: int = DEFAULT_CANNY_LOW,
    high_threshold: int = DEFAULT_CANNY_HIGH
) -> EdgeResult:
    """
    Perform Canny Edge Detection to highlight spatial boundaries and structural anomalies.
    """
    gray = cv2.cvtColor(cv2_bgr, cv2.COLOR_BGR2GRAY)
    
    # Slight Gaussian smoothing to reduce high-frequency noise prior to edge detection
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    
    edges = cv2.Canny(blurred, low_threshold, high_threshold)

    # Calculate edge pixel density
    total_pixels = edges.size
    edge_pixels = np.count_nonzero(edges)
    edge_density_pct = (edge_pixels / total_pixels) * 100.0

    # Invert edge map for clean display (black edges on white or white on dark)
    edge_rgb = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
    edge_pil = Image.fromarray(edge_rgb)

    notes = (
        f"Canny edge detection completed (Thresholds: Low={low_threshold}, High={high_threshold}). "
        f"Detected spatial edge density: {edge_density_pct:.2f}% of total pixels. "
        "Edge maps assist in inspecting sharp boundary discontinuities along object outlines."
    )

    return EdgeResult(
        edge_map_pil=edge_pil,
        edge_map_np=edges,
        edge_density_pct=round(edge_density_pct, 2),
        low_threshold=low_threshold,
        high_threshold=high_threshold,
        summary_notes=notes
    )
