"""
ImageGuard - Image Histogram & Channel Statistical Analysis Module
"""

from dataclasses import dataclass
from typing import Dict, Tuple
import matplotlib.pyplot as plt
import numpy as np
import cv2


@dataclass
class ChannelStats:
    mean: float
    median: float
    std_dev: float
    min_val: int
    max_val: int


@dataclass
class HistogramResult:
    stats_gray: ChannelStats
    stats_red: ChannelStats
    stats_green: ChannelStats
    stats_blue: ChannelStats
    histogram_figure: plt.Figure
    summary_notes: str


def analyze_histograms(cv2_bgr: np.ndarray) -> HistogramResult:
    """
    Generate Grayscale and RGB channel histograms and statistical metrics.
    """
    gray = cv2.cvtColor(cv2_bgr, cv2.COLOR_BGR2GRAY)
    b, g, r = cv2.split(cv2_bgr)

    def calc_stats(arr: np.ndarray) -> ChannelStats:
        return ChannelStats(
            mean=round(float(np.mean(arr)), 2),
            median=round(float(np.median(arr)), 2),
            std_dev=round(float(np.std(arr)), 2),
            min_val=int(np.min(arr)),
            max_val=int(np.max(arr))
        )

    stats_gray = calc_stats(gray)
    stats_r = calc_stats(r)
    stats_g = calc_stats(g)
    stats_b = calc_stats(b)

    # Plot Matplotlib Figure
    fig, axes = plt.subplots(2, 2, figsize=(10, 7))
    fig.patch.set_facecolor("#0E1117")

    colors = [("Grayscale", gray, "gray", axes[0, 0]),
              ("Red Channel", r, "red", axes[0, 1]),
              ("Green Channel", g, "green", axes[1, 0]),
              ("Blue Channel", b, "blue", axes[1, 1])]

    for title, channel, color, ax in colors:
        ax.set_facecolor("#1E222A")
        hist, bins = np.histogram(channel, bins=256, range=(0, 256))
        ax.plot(hist, color=color, alpha=0.9, linewidth=1.5)
        ax.fill_between(range(256), hist, color=color, alpha=0.3)
        ax.set_title(title, color="white", fontsize=11, fontweight="bold")
        ax.set_xlim([0, 256])
        ax.tick_params(colors="white")
        ax.grid(True, color="#2D323E", linestyle="--", alpha=0.5)

    plt.tight_layout()

    notes = (
        f"Grayscale Mean: {stats_gray.mean}, Std Dev: {stats_gray.std_dev}. "
        "Histogram distributions show luminance dynamic range across channels."
    )

    return HistogramResult(
        stats_gray=stats_gray,
        stats_red=stats_r,
        stats_green=stats_g,
        stats_blue=stats_b,
        histogram_figure=fig,
        summary_notes=notes
    )
