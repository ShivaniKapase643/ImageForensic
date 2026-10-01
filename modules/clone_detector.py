"""
ImageGuard - Copy-Move / Clone Forgery Detection Module (ORB + RANSAC)
"""

from dataclasses import dataclass, field
from typing import List, Tuple
import cv2
import numpy as np
from PIL import Image

from config.settings import (
    DEFAULT_LOWE_RATIO,
    DEFAULT_MIN_MATCHES,
    DEFAULT_ORB_NFEATURES,
    DEFAULT_SPATIAL_THRESHOLD,
)


@dataclass
class CloneResult:
    visualization_pil: Image.Image
    keypoints_count: int
    matched_pairs_count: int
    ransac_inliers_count: int
    is_clone_detected: bool
    bounding_boxes: List[Tuple[int, int, int, int]] = field(default_factory=list)
    summary_notes: str = ""


def detect_copy_move(
    cv2_bgr: np.ndarray,
    nfeatures: int = DEFAULT_ORB_NFEATURES,
    ratio_thresh: float = DEFAULT_LOWE_RATIO,
    min_spatial_dist: float = DEFAULT_SPATIAL_THRESHOLD,
    min_matches: int = DEFAULT_MIN_MATCHES
) -> CloneResult:
    """
    Detect potential intra-image copy-move (cloning) forgery using ORB feature descriptor matching
    with spatial proximity suppression and RANSAC geometric verification.
    """
    gray = cv2.cvtColor(cv2_bgr, cv2.COLOR_BGR2GRAY)
    
    # Initialize ORB detector
    orb = cv2.ORB_create(nfeatures=nfeatures)
    keypoints, descriptors = orb.detectAndCompute(gray, None)

    if descriptors is None or len(keypoints) < 10:
        vis_pil = Image.fromarray(cv2.cvtColor(cv2_bgr, cv2.COLOR_BGR2RGB))
        return CloneResult(
            visualization_pil=vis_pil,
            keypoints_count=len(keypoints) if keypoints else 0,
            matched_pairs_count=0,
            ransac_inliers_count=0,
            is_clone_detected=False,
            summary_notes="Insufficient distinct feature keypoints detected in the image for copy-move analysis."
        )

    # Brute-force matcher with Hamming distance k=2 for ratio test
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
    raw_matches = bf.knnMatch(descriptors, descriptors, k=2)

    valid_matches = []
    pt1_list = []
    pt2_list = []

    for match in raw_matches:
        if len(match) < 2:
            continue
        m, n = match[0], match[1]

        # Ignore self-matches (same keypoint index)
        if m.queryIdx == m.trainIdx:
            continue

        # Lowe's ratio test
        if m.distance < ratio_thresh * n.distance:
            p1 = np.array(keypoints[m.queryIdx].pt)
            p2 = np.array(keypoints[m.trainIdx].pt)

            # Spatial distance check: exclude adjacent keypoints belonging to same texture block
            spatial_dist = np.linalg.norm(p1 - p2)
            if spatial_dist >= min_spatial_dist:
                valid_matches.append(m)
                pt1_list.append(p1)
                pt2_list.append(p2)

    ransac_inliers = 0
    bounding_boxes = []

    # Perform RANSAC geometric affine check if enough candidate matches exist
    if len(pt1_list) >= 4:
        pts1 = np.float32(pt1_list).reshape(-1, 1, 2)
        pts2 = np.float32(pt2_list).reshape(-1, 1, 2)

        # Estimate Affine or Homography matrix with RANSAC
        H, mask = cv2.findHomography(pts1, pts2, cv2.RANSAC, 5.0)
        if mask is not None:
            ransac_inliers = int(np.sum(mask))

    # Render matches visualization
    canvas = cv2_bgr.copy()
    
    # Draw matched keypoint lines
    for i, m in enumerate(valid_matches):
        p1 = tuple(np.int32(keypoints[m.queryIdx].pt))
        p2 = tuple(np.int32(keypoints[m.trainIdx].pt))

        # Color code: cyan line, red keypoints
        cv2.line(canvas, p1, p2, (255, 255, 0), 1, cv2.LINE_AA)
        cv2.circle(canvas, p1, 3, (0, 0, 255), -1)
        cv2.circle(canvas, p2, 3, (0, 255, 0), -1)

    vis_rgb = cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB)
    vis_pil = Image.fromarray(vis_rgb)

    is_clone_detected = len(valid_matches) >= min_matches and ransac_inliers >= 4

    if is_clone_detected:
        notes = (
            f"Potential duplicated region detected. Found {len(valid_matches)} spatially separated feature matches "
            f"({ransac_inliers} RANSAC inliers). This indicates similar texture patches within the image, requiring review."
        )
    else:
        notes = (
            f"No strong copy-move evidence detected ({len(valid_matches)} candidate matches, threshold={min_matches}). "
            "Repetitive natural textures (e.g. foliage, architecture) can also generate weak matches."
        )

    return CloneResult(
        visualization_pil=vis_pil,
        keypoints_count=len(keypoints),
        matched_pairs_count=len(valid_matches),
        ransac_inliers_count=ransac_inliers,
        is_clone_detected=is_clone_detected,
        bounding_boxes=bounding_boxes,
        summary_notes=notes
    )
