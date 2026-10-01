"""
Unit Tests for Noise Analysis Module
"""

import numpy as np
import pytest
from modules.noise_analyzer import analyze_noise


def test_noise_analysis():
    # Synthetic random noise image (BGR)
    np.random.seed(42)
    bgr = np.random.randint(0, 256, (200, 200, 3), dtype=np.uint8)

    noise_res = analyze_noise(bgr, kernel_size=7)

    assert noise_res.noise_map_pil is not None
    assert noise_res.mean_noise > 0.0
    assert noise_res.std_noise > 0.0
    assert len(noise_res.regional_variances) == 4
