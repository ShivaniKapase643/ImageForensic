"""
Unit Tests for Heuristic Evidence Aggregation Engine
"""

import pytest
from PIL import Image
import numpy as np

from modules.clone_detector import CloneResult
from modules.compression_analyzer import CompressionResult
from modules.ela_analyzer import ELAResult
from modules.evidence_engine import aggregate_evidence
from modules.metadata_analyzer import MetadataResult
from modules.noise_analyzer import NoiseResult


def test_evidence_aggregation_low():
    meta = MetadataResult(has_exif=True, editing_software_detected=False)
    ela = ELAResult(ela_pil_image=Image.new("RGB", (10, 10)), ela_np_array=np.zeros((10, 10)), mean_difference=1.0, max_difference=5.0, std_difference=2.0, is_anomalous=False, summary_notes="")
    noise = NoiseResult(noise_map_pil=Image.new("RGB", (10, 10)), noise_map_np=np.zeros((10, 10)), mean_noise=1.0, std_noise=1.0, regional_variances=[1.0, 1.0, 1.0, 1.0], variance_ratio=1.0, is_non_uniform=False, summary_notes="")
    clone = CloneResult(visualization_pil=Image.new("RGB", (10, 10)), keypoints_count=50, matched_pairs_count=0, ransac_inliers_count=0, is_clone_detected=False, summary_notes="")
    comp = CompressionResult(image_format="JPEG", is_jpeg=True, estimated_jpeg_quality=90, blockiness_score=1.0, recompression_anomalous=False, summary_notes="")

    summary = aggregate_evidence(meta, ela, noise, clone, comp)

    assert summary.indicator_level == "LOW"
    assert summary.total_score == 0.0


def test_evidence_aggregation_high():
    meta = MetadataResult(has_exif=True, editing_software_detected=True, detected_software_name="Adobe Photoshop")
    ela = ELAResult(ela_pil_image=Image.new("RGB", (10, 10)), ela_np_array=np.zeros((10, 10)), mean_difference=15.0, max_difference=50.0, std_difference=14.0, is_anomalous=True, summary_notes="")
    noise = NoiseResult(noise_map_pil=Image.new("RGB", (10, 10)), noise_map_np=np.zeros((10, 10)), mean_noise=10.0, std_noise=8.0, regional_variances=[1.0, 5.0, 2.0, 8.0], variance_ratio=3.5, is_non_uniform=True, summary_notes="")
    clone = CloneResult(visualization_pil=Image.new("RGB", (10, 10)), keypoints_count=500, matched_pairs_count=25, ransac_inliers_count=12, is_clone_detected=True, summary_notes="")
    comp = CompressionResult(image_format="JPEG", is_jpeg=True, estimated_jpeg_quality=60, blockiness_score=1.8, recompression_anomalous=True, summary_notes="")

    summary = aggregate_evidence(meta, ela, noise, clone, comp)

    assert summary.indicator_level == "HIGH"
    assert summary.total_score >= 6.0
