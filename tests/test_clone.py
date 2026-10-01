"""
Unit Tests for Copy-Move Clone Detection Module
"""

import cv2
import numpy as np
import pytest
from modules.clone_detector import detect_copy_move


def test_clone_detection_blank():
    # Blank solid color canvas has no keypoints
    blank_bgr = np.zeros((200, 200, 3), dtype=np.uint8)
    res = detect_copy_move(blank_bgr)

    assert not res.is_clone_detected
    assert res.matched_pairs_count == 0
    assert "insufficient" in res.summary_notes.lower() or "no strong" in res.summary_notes.lower()
