"""
ImageGuard - Utility Functions for Formatting
"""

import datetime
import random
import re
import string


def format_file_size(size_bytes: int) -> str:
    """Format file size in bytes to human-readable string (KB/MB)."""
    if size_bytes < 1024:
        return f"{size_bytes} Bytes"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} MB"


def generate_case_id() -> str:
    """Generate a unique forensic investigation case ID (e.g. CASE-2026-8A3F)."""
    year = datetime.datetime.now().year
    rand_str = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"CASE-{year}-{rand_str}"


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal or unsafe file characters."""
    filename = re.sub(r"[^\w\.-]", "_", filename)
    return filename if filename else "unnamed_image"


def get_current_timestamp() -> str:
    """Return current timestamp formatted for forensic logging."""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
