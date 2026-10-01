"""
ImageGuard - EXIF & Technical Metadata Analysis Module
"""

import io
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from PIL import Image, ExifTags


KNOWN_EDITING_SOFTWARE = [
    "photoshop", "gimp", "canva", "paint.net", "lightroom",
    "pixlr", "snapseed", "affinity", "pixelmator", "coreldraw",
    "picasa", "fotor", "photoscape", "darktable", "rawtherapee"
]


@dataclass
class MetadataResult:
    has_exif: bool = False
    file_format: str = "Unknown"
    mime_type: str = "Unknown"
    dimensions: str = "Unknown"
    width: int = 0
    height: int = 0
    color_mode: str = "Unknown"
    camera_make: str = "N/A"
    camera_model: str = "N/A"
    datetime_original: str = "N/A"
    software: str = "N/A"
    editing_software_detected: bool = False
    detected_software_name: str = ""
    gps_info: Optional[Dict[str, Any]] = None
    exif_raw: Dict[str, Any] = field(default_factory=dict)
    summary_notes: str = ""


def analyze_metadata(file_bytes: bytes, filename: str) -> MetadataResult:
    """
    Extract technical image properties and parse EXIF metadata.
    Detect potential signatures of digital editing software.
    """
    result = MetadataResult()
    
    try:
        img = Image.open(io.BytesIO(file_bytes))
        result.file_format = img.format if img.format else "Unknown"
        result.mime_type = Image.MIME.get(img.format, f"image/{img.format.lower()}" if img.format else "unknown")
        result.width, result.height = img.size
        result.dimensions = f"{result.width} x {result.height} px"
        result.color_mode = img.mode

        # Check EXIF data
        raw_exif = img._getexif()
        if raw_exif:
            result.has_exif = True
            exif_dict = {}
            for tag_id, value in raw_exif.items():
                tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
                
                # Sanitize non-serializable byte strings
                if isinstance(value, bytes):
                    try:
                        value = value.decode("utf-8", errors="ignore").strip("\x00")
                    except Exception:
                        value = str(value)
                
                exif_dict[tag_name] = str(value)

            result.exif_raw = exif_dict
            result.camera_make = exif_dict.get("Make", "N/A")
            result.camera_model = exif_dict.get("Model", "N/A")
            result.datetime_original = exif_dict.get("DateTimeOriginal", exif_dict.get("DateTime", "N/A"))
            result.software = exif_dict.get("Software", "N/A")

            # Check for editing software signatures
            if result.software != "N/A":
                soft_lower = result.software.lower()
                for kw in KNOWN_EDITING_SOFTWARE:
                    if kw in soft_lower:
                        result.editing_software_detected = True
                        result.detected_software_name = result.software
                        break

            # Parse GPS metadata if available
            gps_info = {}
            for k, v in exif_dict.items():
                if "GPS" in k:
                    gps_info[k] = v
            if gps_info:
                result.gps_info = gps_info

        # Generate summary rationale
        if result.editing_software_detected:
            result.summary_notes = (
                f"Editing software metadata detected ('{result.detected_software_name}'). "
                "This is an indicator requiring further examination, not proof of manipulation."
            )
        elif not result.has_exif:
            result.summary_notes = (
                "EXIF metadata is absent or stripped. This can occur during web upload, social media re-saving, "
                "or export actions, and does not automatically imply tampering."
            )
        else:
            result.summary_notes = "Standard EXIF metadata extracted without obvious editing software markers."

    except Exception as e:
        result.summary_notes = f"Metadata extraction encountered an issue: {str(e)}"

    return result
