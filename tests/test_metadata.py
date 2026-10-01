"""
Unit Tests for Metadata & EXIF Analyzer
"""

import io
import pytest
from PIL import Image
from modules.metadata_analyzer import analyze_metadata


def test_metadata_basic_image():
    # Create a simple synthetic PIL image
    img = Image.new("RGB", (300, 200), color="blue")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    bytes_data = buf.getvalue()

    result = analyze_metadata(bytes_data, "test.jpg")
    
    assert result.width == 300
    assert result.height == 200
    assert result.file_format == "JPEG"
    assert result.color_mode == "RGB"
    assert not result.editing_software_detected
