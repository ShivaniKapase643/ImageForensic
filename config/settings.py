"""
ImageGuard - Configuration and Global Settings
"""

from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
SAMPLE_IMAGES_DIR = ASSETS_DIR / "sample_images"
REPORTS_DIR = BASE_DIR / "reports"

# Ensure essential directories exist
SAMPLE_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Application Information
APP_NAME = "ImageGuard"
APP_SUBTITLE = "Digital Image Forensics & Tampering Analysis"
APP_TAGLINE = "Analyze. Investigate. Verify."
APP_VERSION = "1.0.0"

# File Upload Settings
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "tiff", "tif"}
MAX_FILE_SIZE_MB = 25
MAX_IMAGE_PIXELS = 20_000_000
MAX_IMAGE_DIMENSION = 2000  # Max width/height for heavy processing copy

# ELA Default Settings
DEFAULT_ELA_QUALITY = 90
DEFAULT_ELA_SCALE = 15

# Noise Analysis Defaults
DEFAULT_NOISE_KERNEL_SIZE = 7

# Edge Analysis Defaults
DEFAULT_CANNY_LOW = 100
DEFAULT_CANNY_HIGH = 200

# Clone Detection Defaults
DEFAULT_ORB_NFEATURES = 2500
DEFAULT_LOWE_RATIO = 0.75
DEFAULT_SPATIAL_THRESHOLD = 30.0  # Min pixel distance between matched keypoints
DEFAULT_MIN_MATCHES = 10

# Evidence Scoring Thresholds
HEURISTIC_WEIGHTS = {
    "software_metadata": 2.0,
    "ela_anomalous": 2.0,
    "noise_non_uniform": 1.5,
    "clone_detected": 3.0,
    "compression_anomaly": 1.0,
}

INDICATOR_LEVELS = {
    "LOW": (0.0, 2.5),
    "MODERATE": (2.6, 5.5),
    "HIGH": (5.6, 10.0),
}
