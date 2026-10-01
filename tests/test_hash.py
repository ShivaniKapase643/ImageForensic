"""
Unit Tests for Cryptographic Hash Generator
"""

import hashlib
import pytest
from modules.hash_generator import generate_image_hashes


def test_hash_generation():
    test_bytes = b"ImageGuard Forensic Test Bytes"
    hashes = generate_image_hashes(test_bytes)
    
    expected_sha256 = hashlib.sha256(test_bytes).hexdigest()
    expected_md5 = hashlib.md5(test_bytes).hexdigest()

    assert hashes["sha256"] == expected_sha256
    assert hashes["md5"] == expected_md5


def test_hash_empty_input():
    hashes = generate_image_hashes(b"")
    assert hashes["sha256"] == "N/A"
    assert hashes["md5"] == "N/A"
