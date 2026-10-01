"""
Unit Tests for Image Validation Module
"""

import pytest
from utils.validation import validate_image_file


def test_validate_empty_bytes():
    is_valid, msg = validate_image_file(b"", "test.jpg")
    assert not is_valid
    assert "empty" in msg.lower()


def test_validate_unsupported_extension():
    is_valid, msg = validate_image_file(b"dummy_bytes", "document.pdf")
    assert not is_valid
    assert "unsupported" in msg.lower()


def test_validate_corrupted_image():
    is_valid, msg = validate_image_file(b"not_an_image_header_bytes", "test.jpg")
    assert not is_valid
    assert "corrupted" in msg.lower() or "invalid" in msg.lower()
