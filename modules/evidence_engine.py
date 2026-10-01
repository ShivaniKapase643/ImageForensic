"""
ImageGuard - Heuristic Evidence Aggregation Engine
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any

from config.settings import HEURISTIC_WEIGHTS, INDICATOR_LEVELS
from modules.clone_detector import CloneResult
from modules.compression_analyzer import CompressionResult
from modules.ela_analyzer import ELAResult
from modules.metadata_analyzer import MetadataResult
from modules.noise_analyzer import NoiseResult


@dataclass
class EvidenceItem:
    technique: str
    result_status: str
    weight: float
    interpretation: str


@dataclass
class EvidenceSummary:
    indicator_level: str  # LOW, MODERATE, HIGH
    total_score: float
    evidence_items: List[EvidenceItem]
    overall_interpretation: str
    disclaimer: str = (
        "IMPORTANT FORENSIC NOTICE: The Analysis Indicator Level is a project-specific heuristic score "
        "based on non-destructive spatial, statistical, and metadata indicators. It is NOT a statistical "
        "probability of forgery. Forensic indicators can yield false positives (e.g. from social media re-saving, "
        "camera compression, repetitive natural textures) and false negatives. Human analyst review is required."
    )


def aggregate_evidence(
    metadata_res: MetadataResult,
    ela_res: ELAResult,
    noise_res: NoiseResult,
    clone_res: CloneResult,
    comp_res: CompressionResult
) -> EvidenceSummary:
    """
    Consolidate quantitative findings across forensic modules into an overall
    Analysis Indicator Level using transparent, documented heuristic rules.
    """
    items = []
    total_score = 0.0

    # 1. Metadata Check
    if metadata_res.editing_software_detected:
        w = HEURISTIC_WEIGHTS["software_metadata"]
        total_score += w
        items.append(EvidenceItem(
            technique="Metadata Analysis",
            result_status=f"Editing software signature detected ({metadata_res.detected_software_name})",
            weight=w,
            interpretation="Review recommended: Image header specifies digital manipulation or editing software."
        ))
    elif not metadata_res.has_exif:
        items.append(EvidenceItem(
            technique="Metadata Analysis",
            result_status="EXIF metadata stripped / unavailable",
            weight=0.0,
            interpretation="Informational: EXIF data absent. Common in web exports; not proof of tampering."
        ))
    else:
        items.append(EvidenceItem(
            technique="Metadata Analysis",
            result_status="Original camera / standard metadata present",
            weight=0.0,
            interpretation="No software editing markers found in file header."
        ))

    # 2. ELA Check
    if ela_res.is_anomalous:
        w = HEURISTIC_WEIGHTS["ela_anomalous"]
        total_score += w
        items.append(EvidenceItem(
            technique="Error Level Analysis (ELA)",
            result_status=f"Localized residual variance (Std Dev: {ela_res.std_difference})",
            weight=w,
            interpretation="Review recommended: Uneven response to JPEG recompression detected across canvas."
        ))
    else:
        items.append(EvidenceItem(
            technique="Error Level Analysis (ELA)",
            result_status=f"Uniform ELA response (Std Dev: {ela_res.std_difference})",
            weight=0.0,
            interpretation="No strong localized ELA variance detected."
        ))

    # 3. Noise Analysis Check
    if noise_res.is_non_uniform:
        w = HEURISTIC_WEIGHTS["noise_non_uniform"]
        total_score += w
        items.append(EvidenceItem(
            technique="Noise Residual Analysis",
            result_status=f"Regional noise mismatch (Variance Ratio: {noise_res.variance_ratio})",
            weight=w,
            interpretation="Review recommended: Inconsistent grain/noise profile observed across quadrants."
        ))
    else:
        items.append(EvidenceItem(
            technique="Noise Residual Analysis",
            result_status=f"Uniform noise profile (Variance Ratio: {noise_res.variance_ratio})",
            weight=0.0,
            interpretation="Noise distribution is consistent across canvas."
        ))

    # 4. Clone / Copy-Move Check
    if clone_res.is_clone_detected:
        w = HEURISTIC_WEIGHTS["clone_detected"]
        total_score += w
        items.append(EvidenceItem(
            technique="Copy-Move Detection",
            result_status=f"Potential duplicated regions ({clone_res.matched_pairs_count} matches, {clone_res.ransac_inliers_count} RANSAC inliers)",
            weight=w,
            interpretation="Review recommended: Multiple spatially separated keypoints exhibit identical descriptor profiles."
        ))
    else:
        items.append(EvidenceItem(
            technique="Copy-Move Detection",
            result_status=f"No strong matches ({clone_res.matched_pairs_count} candidate matches)",
            weight=0.0,
            interpretation="No strong intra-image duplication patterns detected."
        ))

    # 5. Compression Check
    if comp_res.recompression_anomalous:
        w = HEURISTIC_WEIGHTS["compression_anomaly"]
        total_score += w
        items.append(EvidenceItem(
            technique="Compression Analysis",
            result_status=f"Elevated grid blockiness (Score: {comp_res.blockiness_score})",
            weight=w,
            interpretation="Informational: Recompression or block quantization artifacts observed."
        ))
    else:
        items.append(EvidenceItem(
            technique="Compression Analysis",
            result_status=f"Normal compression boundary transitions (Score: {comp_res.blockiness_score})",
            weight=0.0,
            interpretation="Standard compression boundaries."
        ))

    # Categorize Indicator Level
    if total_score <= 2.5:
        level = "LOW"
        overall_interp = (
            "No strong manipulation indicators detected. The image exhibits consistent structural, "
            "noise, and compression characteristics across evaluated modules."
        )
    elif total_score <= 5.5:
        level = "MODERATE"
        overall_interp = (
            "Several image characteristics warrant further examination. Isolated forensic indicators "
            "(e.g. metadata software tags or localized ELA variance) were detected."
        )
    else:
        level = "HIGH"
        overall_interp = (
            "Multiple potential manipulation indicators detected across distinct forensic techniques "
            "(e.g. copy-move matches, ELA variance, or editing software metadata). Detailed manual investigation recommended."
        )

    return EvidenceSummary(
        indicator_level=level,
        total_score=round(total_score, 1),
        evidence_items=items,
        overall_interpretation=overall_interp
    )
