"""
ImageGuard - PDF Forensic Report Generator Module (ReportLab)
"""

import io
import os
from typing import Dict, Any, Optional
from PIL import Image

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from config.settings import REPORTS_DIR
from modules.clone_detector import CloneResult
from modules.compression_analyzer import CompressionResult
from modules.edge_analyzer import EdgeResult
from modules.ela_analyzer import ELAResult
from modules.evidence_engine import EvidenceSummary
from modules.metadata_analyzer import MetadataResult
from modules.noise_analyzer import NoiseResult
from utils.formatting import get_current_timestamp


def generate_pdf_report(
    case_id: str,
    filename: str,
    sha256_hash: str,
    metadata_res: MetadataResult,
    ela_res: ELAResult,
    noise_res: NoiseResult,
    edge_res: EdgeResult,
    clone_res: CloneResult,
    comp_res: CompressionResult,
    evidence_sum: EvidenceSummary,
    histogram_fig_bytes: Optional[bytes] = None,
    output_path: Optional[str] = None
) -> str:
    """
    Generate a professional multi-page PDF forensic investigation report using ReportLab.
    
    Returns:
        Absolute path to generated PDF report.
    """
    if output_path is None:
        output_filename = f"Forensic_Report_{case_id}_{filename}.pdf".replace(" ", "_")
        output_path = os.path.join(REPORTS_DIR, output_filename)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom Report Styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=26,
        textColor=colors.HexColor("#1E293B"),
        alignment=TA_LEFT
    )
    
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#64748B"),
        alignment=TA_LEFT
    )

    h2_style = ParagraphStyle(
        "SectionH2",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=12,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        "BodyTextCustom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155")
    )

    badge_style = ParagraphStyle(
        "BadgeStyle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=14,
        alignment=TA_CENTER
    )

    story = []

    # Header Title Banner
    story.append(Paragraph("IMAGEGUARD", title_style))
    story.append(Paragraph("DIGITAL IMAGE FORENSICS & TAMPERING ANALYSIS REPORT", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#2563EB"), spaceAfter=12))

    # Case Summary Header Table
    level_color = "#16A34A" if evidence_sum.indicator_level == "LOW" else "#D97706" if evidence_sum.indicator_level == "MODERATE" else "#DC2626"
    badge_text = f"<font color='{level_color}'>INDICATOR LEVEL: {evidence_sum.indicator_level}</font>"

    header_data = [
        [Paragraph("<b>Case ID:</b>", body_style), Paragraph(case_id, body_style), Paragraph("<b>Analysis Timestamp:</b>", body_style), Paragraph(get_current_timestamp(), body_style)],
        [Paragraph("<b>Target Filename:</b>", body_style), Paragraph(filename, body_style), Paragraph("<b>Image Format / Mode:</b>", body_style), Paragraph(f"{metadata_res.file_format} ({metadata_res.color_mode})", body_style)],
        [Paragraph("<b>Dimensions:</b>", body_style), Paragraph(metadata_res.dimensions, body_style), Paragraph("<b>File Hash (SHA-256):</b>", body_style), Paragraph(f"<font size=7>{sha256_hash[:32]}...</font>", body_style)],
    ]

    header_table = Table(header_data, colWidths=[100, 170, 120, 150])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#E2E8F0')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 10))

    # Executive Summary Card
    story.append(Paragraph("1. Executive Evidence Summary", h2_style))
    summary_box_data = [
        [Paragraph(badge_text, badge_style)],
        [Paragraph(f"<b>Overall Finding:</b> {evidence_sum.overall_interpretation}", body_style)]
    ]
    summary_table = Table(summary_box_data, colWidths=[540])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FEF3C7') if evidence_sum.indicator_level == 'MODERATE' else colors.HexColor('#FEE2E2') if evidence_sum.indicator_level == 'HIGH' else colors.HexColor('#DCFCE7')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor(level_color)),
        ('ALIGN', (0,0), (0,0), 'CENTER'),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 10))

    # Evidence Breakdown Table
    story.append(Paragraph("2. Forensic Techniques & Indicator Breakdown", h2_style))
    table_data = [["Forensic Technique", "Result / Finding", "Weight", "Interpretation"]]
    for item in evidence_sum.evidence_items:
        table_data.append([
            Paragraph(f"<b>{item.technique}</b>", body_style),
            Paragraph(item.result_status, body_style),
            Paragraph(f"+{item.weight}", body_style),
            Paragraph(item.interpretation, body_style)
        ])

    evidence_table = Table(table_data, colWidths=[120, 160, 45, 215])
    evidence_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(evidence_table)
    story.append(Spacer(1, 12))

    # Helper function to convert PIL Image to ReportLab Image
    def save_temp_img(pil_img: Image.Image, prefix: str) -> str:
        temp_path = os.path.join(REPORTS_DIR, f"temp_{case_id}_{prefix}.png")
        pil_img.save(temp_path, format="PNG")
        return temp_path

    temp_files = []

    # Visual Evidence Panel
    story.append(Paragraph("3. Forensic Visual Evidence", h2_style))
    
    ela_temp = save_temp_img(ela_res.ela_pil_image, "ela")
    temp_files.append(ela_temp)
    
    noise_temp = save_temp_img(noise_res.noise_map_pil, "noise")
    temp_files.append(noise_temp)

    clone_temp = save_temp_img(clone_res.visualization_pil, "clone")
    temp_files.append(clone_temp)

    edge_temp = save_temp_img(edge_res.edge_map_pil, "edge")
    temp_files.append(edge_temp)

    img_grid_data = [
        [Paragraph("<b>Error Level Analysis (ELA)</b>", body_style), Paragraph("<b>Noise Residual Map</b>", body_style)],
        [RLImage(ela_temp, width=250, height=180), RLImage(noise_temp, width=250, height=180)],
        [Paragraph("<b>Copy-Move Detection Matches</b>", body_style), Paragraph("<b>Canny Edge Map</b>", body_style)],
        [RLImage(clone_temp, width=250, height=180), RLImage(edge_temp, width=250, height=180)],
    ]

    img_table = Table(img_grid_data, colWidths=[270, 270])
    img_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(KeepTogether(img_table))
    story.append(Spacer(1, 12))

    # Metadata & EXIF Table
    story.append(Paragraph("4. Key Technical Metadata", h2_style))
    meta_table_data = [
        [Paragraph("<b>Property</b>", body_style), Paragraph("<b>Extracted Value</b>", body_style)],
        [Paragraph("Camera Make", body_style), Paragraph(metadata_res.camera_make, body_style)],
        [Paragraph("Camera Model", body_style), Paragraph(metadata_res.camera_model, body_style)],
        [Paragraph("Date / Time Original", body_style), Paragraph(metadata_res.datetime_original, body_style)],
        [Paragraph("Software Tag", body_style), Paragraph(metadata_res.software, body_style)],
        [Paragraph("Editing Software Flag", body_style), Paragraph("YES" if metadata_res.editing_software_detected else "NO", body_style)],
    ]
    meta_table = Table(meta_table_data, colWidths=[180, 360])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#E2E8F0')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 14))

    # Legal / Academic Disclaimer
    story.append(Paragraph("5. Forensic Disclaimer & Limitations", h2_style))
    story.append(Paragraph(evidence_sum.disclaimer, body_style))

    # Build Document
    doc.build(story)

    # Cleanup temporary images
    for tf in temp_files:
        try:
            if os.path.exists(tf):
                os.remove(tf)
        except Exception:
            pass

    return output_path
