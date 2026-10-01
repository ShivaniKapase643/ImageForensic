"""
Unit Tests for Error Level Analysis (ELA) Module
"""

import pytest
from PIL import Image
from modules.ela_analyzer import perform_ela


def test_perform_ela():
    img = Image.new("RGB", (200, 200), color="red")
    ela_res = perform_ela(img, quality=90, scale=15, is_jpeg=True)

    assert ela_res.ela_pil_image is not None
    assert ela_res.mean_difference >= 0.0
    assert ela_res.max_difference >= 0.0
    assert ela_res.std_difference >= 0.0
