"""
ImageGuard - Cryptographic Hash Generator Module
"""

import hashlib
from typing import Dict


def generate_image_hashes(file_bytes: bytes) -> Dict[str, str]:
    """
    Generate SHA-256 and MD5 cryptographic hashes for input image bytes.
    
    Returns:
        Dict with keys 'sha256' and 'md5' containing hexadecimal hash strings.
    """
    if not file_bytes:
        return {"sha256": "N/A", "md5": "N/A"}

    sha256_hash = hashlib.sha256(file_bytes).hexdigest()
    md5_hash = hashlib.md5(file_bytes).hexdigest()

    return {
        "sha256": sha256_hash,
        "md5": md5_hash
    }
