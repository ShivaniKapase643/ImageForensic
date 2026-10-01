"""
ImageGuard - Digital Image Forensics & Tampering Analysis Dashboard
Main Streamlit Application
"""

import os
import streamlit as st

from config.settings import (
    APP_NAME, APP_SUBTITLE, APP_TAGLINE, APP_VERSION,
    DEFAULT_CANNY_HIGH, DEFAULT_CANNY_LOW, DEFAULT_ELA_QUALITY, DEFAULT_ELA_SCALE,
    DEFAULT_LOWE_RATIO, DEFAULT_NOISE_KERNEL_SIZE, DEFAULT_ORB_NFEATURES,
)
from modules.clone_detector import detect_copy_move
from modules.compression_analyzer import CompressionResult, analyze_compression
from modules.edge_analyzer import detect_edges
from modules.ela_analyzer import perform_ela
from modules.evidence_engine import EvidenceSummary, aggregate_evidence
from modules.hash_generator import generate_image_hashes
from modules.histogram_analyzer import analyze_histograms
from modules.metadata_analyzer import MetadataResult, analyze_metadata
from modules.noise_analyzer import analyze_noise
from modules.report_generator import generate_pdf_report
from utils.formatting import format_file_size, generate_case_id, sanitize_filename
from utils.image_utils import cv2_to_pil, load_pil_image, pil_to_cv2, resize_for_processing
from utils.validation import validate_image_file


# Streamlit Page Configuration
st.set_page_config(
    page_title=f"{APP_NAME} - Digital Image Forensics",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS Theme
st.markdown("""
<style>
    /* Dark Professional Workstation Theme */
    .stApp {
        background-color: #0E1117;
        color: #E2E8F0;
    }
    .metric-card {
        background-color: #1E222A;
        border: 1px solid #2D323E;
        border-radius: 8px;
        padding: 14px;
        text-align: center;
    }
    .badge-low {
        background-color: #16A34A;
        color: white;
        padding: 6px 14px;
        border-radius: 6px;
        font-weight: bold;
    }
    .badge-mod {
        background-color: #D97706;
        color: white;
        padding: 6px 14px;
        border-radius: 6px;
        font-weight: bold;
    }
    .badge-high {
        background-color: #DC2626;
        color: white;
        padding: 6px 14px;
        border-radius: 6px;
        font-weight: bold;
    }
    .forensic-title {
        color: #60A5FA;
        font-size: 28px;
        font-weight: bold;
        margin-bottom: 0px;
    }
    .forensic-sub {
        color: #94A3B8;
        font-size: 14px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)


def main():
    # Header Banner
    st.markdown(f'<div class="forensic-title">🛡️ {APP_NAME}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="forensic-sub">{APP_SUBTITLE} | <i>"{APP_TAGLINE}"</i></div>', unsafe_allow_html=True)
    st.divider()

    # Sidebar
    st.sidebar.title("ImageGuard Forensics")
    st.sidebar.caption(f"Version {APP_VERSION} | Windows Workstation Edition")

    # Session State Initialization
    if "case_id" not in st.session_state:
        st.session_state.case_id = generate_case_id()

    st.sidebar.markdown(f"**Case ID:** `{st.session_state.case_id}`")

    # Sidebar Navigation Menu
    nav_option = st.sidebar.radio(
        "Navigation",
        [
            "📁 Image Ingestion & Overview",
            "📋 Metadata & EXIF Analysis",
            "🔍 Error Level Analysis (ELA)",
            "🌊 Noise Residual Analysis",
            "🧩 Copy-Move Clone Detection",
            "🗜️ Compression Analysis",
            "📊 Histogram Analysis",
            "📐 Canny Edge Analysis",
            "⚖️ Consolidated Evidence Engine",
            "📄 Generate PDF Forensic Report",
            "📖 Academic Project & About"
        ]
    )

    # File Uploader Widget
    st.sidebar.subheader("Target Image Ingestion")
    uploaded_file = st.sidebar.file_uploader(
        "Upload image for forensic examination",
        type=["jpg", "jpeg", "png", "webp", "tiff", "tif"],
        help="Supported formats: JPG, JPEG, PNG, WEBP, TIFF (Max 25MB)"
    )

    if uploaded_file is None:
        st.info("👋 Welcome to **ImageGuard**! Upload a target digital image from the sidebar to begin multi-module forensic analysis.")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            ### Core Forensic Modules
            - **Metadata & EXIF Extraction**: Camera models, exposure, software tags.
            - **Error Level Analysis (ELA)**: Recompression difference mapping.
            - **Noise Residual Analysis**: Spatial noise variance across grid quadrants.
            - **Copy-Move (Clone) Detection**: Intra-image feature matching with ORB + RANSAC.
            - **Compression Artifact Analysis**: 8x8 DCT grid blockiness metrics.
            - **Canny Edge Detection**: Boundary discontinuity isolation.
            """)
        with col2:
            st.markdown("""
            ### Forensic Principles
            > ⚠️ **Non-Definitive Rule**: ImageGuard evaluates forensic evidence using transparent heuristics.
            > It does **NOT** claim absolute proof of "real" or "fake". Analysis results are labeled as:
            > - *Potential manipulation indicator detected*
            > - *No strong manipulation indicator detected*
            > - *Requires further investigation*
            """)
        return

    # Process Uploaded Image Bytes
    file_bytes = uploaded_file.read()
    filename = sanitize_filename(uploaded_file.name)

    # Validate Image Ingestion
    is_valid, err_msg = validate_image_file(file_bytes, filename)
    if not is_valid:
        st.error(f"❌ Ingestion Error: {err_msg}")
        return

    # Load PIL & OpenCV Arrays
    try:
        pil_img = load_pil_image(file_bytes)
        cv2_bgr = pil_to_cv2(pil_img)
        cv2_proc, was_resized = resize_for_processing(cv2_bgr)
    except Exception as e:
        st.error(f"❌ Failed to decode image content: {str(e)}")
        return

    # Generate Hash
    hashes = generate_image_hashes(file_bytes)
    sha256_hash = hashes["sha256"]

    analysis_errors = {}

    def run_module(module_name, operation):
        try:
            return operation()
        except Exception as error:
            analysis_errors[module_name] = str(error) or "Unexpected analysis error."
            return None

    # Run Analysis Engine Modules
    with st.spinner("Analyzing image across forensic modules..."):
        meta_res = run_module("Metadata analysis", lambda: analyze_metadata(file_bytes, filename))
        image_format = meta_res.file_format if meta_res else filename.rsplit(".", 1)[-1].upper()
        is_jpeg = image_format.upper() in ["JPEG", "JPG"]
        ela_res = run_module(
            "Error Level Analysis",
            lambda: perform_ela(pil_img, quality=DEFAULT_ELA_QUALITY, scale=DEFAULT_ELA_SCALE, is_jpeg=is_jpeg),
        )
        noise_res = run_module("Noise residual analysis", lambda: analyze_noise(cv2_proc, kernel_size=DEFAULT_NOISE_KERNEL_SIZE))
        clone_res = run_module(
            "Copy-move detection",
            lambda: detect_copy_move(cv2_proc, nfeatures=DEFAULT_ORB_NFEATURES, ratio_thresh=DEFAULT_LOWE_RATIO),
        )
        comp_res = run_module("Compression analysis", lambda: analyze_compression(file_bytes, cv2_proc, image_format))
        hist_res = run_module("Histogram analysis", lambda: analyze_histograms(cv2_proc))
        edge_res = run_module(
            "Canny edge analysis",
            lambda: detect_edges(cv2_proc, low_threshold=DEFAULT_CANNY_LOW, high_threshold=DEFAULT_CANNY_HIGH),
        )

        required_evidence = (meta_res, ela_res, noise_res, clone_res, comp_res)
        evidence_sum = (
            run_module(
                "Consolidated evidence analysis",
                lambda: aggregate_evidence(meta_res, ela_res, noise_res, clone_res, comp_res),
            )
            if all(result is not None for result in required_evidence)
            else None
        )

    for module_name, message in analysis_errors.items():
        st.warning(f"{module_name} could not be completed: {message[:240]}")

    # Metrics Summary Bar
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Resolution", meta_res.dimensions if meta_res else "Unavailable")
    m2.metric("File Size", format_file_size(len(file_bytes)))
    m3.metric("EXIF Status", "Unavailable" if meta_res is None else "Available" if meta_res.has_exif else "Absent")
    m4.metric("Software Tag", "Unavailable" if meta_res is None else meta_res.software[:15] if meta_res.software != "N/A" else "Clean")
    
    badge_html = (
        '<span class="badge-low">LOW</span>' if evidence_sum and evidence_sum.indicator_level == "LOW"
        else '<span class="badge-mod">MODERATE</span>' if evidence_sum and evidence_sum.indicator_level == "MODERATE"
        else '<span class="badge-high">HIGH</span>' if evidence_sum
        else '<span class="badge-mod">UNAVAILABLE</span>'
    )
    m5.markdown(f"**Indicator Level**<br>{badge_html}", unsafe_allow_html=True)

    st.caption(f"**SHA-256:** `{sha256_hash}`")
    if was_resized:
        st.warning("⚠️ High-resolution image detected. Heavy pixel analyses (ELA, Noise, Clone Detection) used an aspect-ratio-preserved resized working array for performance.")

    st.divider()

    # Router Navigation Pages
    if nav_option == "📁 Image Ingestion & Overview":
        render_overview(pil_img, filename, hashes, meta_res, evidence_sum)
    elif nav_option == "📋 Metadata & EXIF Analysis":
        render_metadata(meta_res)
    elif nav_option == "🔍 Error Level Analysis (ELA)":
        render_ela(pil_img, meta_res)
    elif nav_option == "🌊 Noise Residual Analysis":
        render_noise(cv2_proc)
    elif nav_option == "🧩 Copy-Move Clone Detection":
        render_clone(cv2_proc)
    elif nav_option == "🗜️ Compression Analysis":
        render_compression(comp_res)
    elif nav_option == "📊 Histogram Analysis":
        render_histograms(hist_res)
    elif nav_option == "📐 Canny Edge Analysis":
        render_edge(cv2_proc)
    elif nav_option == "⚖️ Consolidated Evidence Engine":
        if evidence_sum:
            render_evidence(evidence_sum)
        else:
            st.warning("A consolidated indicator cannot be calculated because one or more required analyses failed.")
    elif nav_option == "📄 Generate PDF Forensic Report":
        if all(result is not None for result in (meta_res, ela_res, noise_res, edge_res, clone_res, comp_res, evidence_sum)):
            render_report(st.session_state.case_id, filename, sha256_hash, meta_res, ela_res, noise_res, edge_res, clone_res, comp_res, evidence_sum, hist_res)
        else:
            st.warning("A complete PDF report is unavailable because one or more required analyses failed.")
    elif nav_option == "📖 Academic Project & About":
        render_about()


# Page Render Functions
def render_overview(pil_img, filename, hashes, meta_res, evidence_sum):
    st.subheader("Target Image Overview")
    col1, col2 = st.columns([1, 1])
    with col1:
        st.image(pil_img, caption=f"Original File: {filename}", width="stretch")
    with col2:
        st.markdown("### Forensic Findings Summary")
        if evidence_sum:
            st.info(f"**Indicator Level:** {evidence_sum.indicator_level}")
            st.write(evidence_sum.overall_interpretation)
        else:
            st.warning("The consolidated indicator is unavailable because one or more required analyses failed.")
        
        st.markdown("### Cryptographic Hashes")
        st.code(f"SHA-256: {hashes['sha256']}\nMD5:    {hashes['md5']}", language="text")


def render_metadata(meta_res: MetadataResult):
    st.subheader("Metadata & EXIF Analysis")
    if meta_res is None:
        st.error("Metadata analysis could not be completed for this image.")
        return
    col1, col2 = st.columns([1, 1])
    with col1:
        st.write("**Technical Image Properties**")
        st.json({
            "File Format": meta_res.file_format,
            "MIME Type": meta_res.mime_type,
            "Dimensions": meta_res.dimensions,
            "Color Mode": meta_res.color_mode,
            "EXIF Available": meta_res.has_exif,
            "Camera Make": meta_res.camera_make,
            "Camera Model": meta_res.camera_model,
            "Date/Time Original": meta_res.datetime_original,
            "Software Tag": meta_res.software,
            "Editing Software Detected": meta_res.editing_software_detected
        })
    with col2:
        st.write("**Metadata Forensic Rationale**")
        if meta_res.editing_software_detected:
            st.warning(meta_res.summary_notes)
        else:
            st.success(meta_res.summary_notes)

        if meta_res.has_exif and meta_res.exif_raw:
            with st.expander("View Full Raw EXIF Tags"):
                st.dataframe(list(meta_res.exif_raw.items()), column_config={"0": "Tag", "1": "Value"})


def render_ela(pil_img, meta_res):
    st.subheader("Error Level Analysis (ELA)")
    st.caption("Re-saves the image at a controlled JPEG quality and amplifies pixel difference residuals.")
    
    col_param1, col_param2 = st.columns(2)
    quality = col_param1.slider("JPEG Compression Quality", 50, 99, DEFAULT_ELA_QUALITY)
    scale = col_param2.slider("Brightness Amplification Scale", 5, 30, DEFAULT_ELA_SCALE)

    try:
        is_jpeg = meta_res is None or meta_res.file_format.upper() in ["JPEG", "JPG"]
        ela_res = perform_ela(pil_img, quality=quality, scale=scale, is_jpeg=is_jpeg)
    except Exception as error:
        st.error(f"ELA could not be calculated: {str(error)[:240]}")
        return

    c1, c2 = st.columns(2)
    c1.image(pil_img, caption="Original Image", width="stretch")
    c2.image(ela_res.ela_pil_image, caption=f"ELA Map (Quality={quality}, Scale={scale}x)", width="stretch")

    st.write(f"**Mean Difference:** `{ela_res.mean_difference}` | **Max Difference:** `{ela_res.max_difference}` | **Std Dev:** `{ela_res.std_difference}`")
    st.info(ela_res.summary_notes)


def render_noise(cv2_proc):
    st.subheader("Noise Residual Analysis")
    st.caption("Extracts high-frequency noise map via Gaussian subtraction and evaluates regional noise variance.")
    
    ksize = st.slider("Gaussian Blur Kernel Size", 3, 15, DEFAULT_NOISE_KERNEL_SIZE, step=2)
    try:
        noise_res = analyze_noise(cv2_proc, kernel_size=ksize)
    except Exception as error:
        st.error(f"Noise residual analysis could not be completed: {str(error)[:240]}")
        return

    c1, c2 = st.columns(2)
    c1.image(cv2_to_pil(cv2_proc), caption="Original Working Image", width="stretch")
    c2.image(noise_res.noise_map_pil, caption="Noise Residual Map (Jet Colorized)", width="stretch")

    st.write(f"**Variance Ratio:** `{noise_res.variance_ratio}` | **Mean Noise:** `{noise_res.mean_noise}` | **Noise Std Dev:** `{noise_res.std_noise}`")
    st.write(f"**Quadrant Variances:** `{noise_res.regional_variances}`")
    st.info(noise_res.summary_notes)


def render_clone(cv2_proc):
    st.subheader("Copy-Move (Clone) Detection")
    st.caption("Locates duplicated regions within the same image using ORB feature descriptor matching and RANSAC geometric verification.")

    c_p1, c_p2 = st.columns(2)
    nfeatures = c_p1.slider("ORB Max Features", 500, 5000, DEFAULT_ORB_NFEATURES, step=500)
    ratio_thresh = c_p2.slider("Lowe's Distance Ratio Threshold", 0.5, 0.9, DEFAULT_LOWE_RATIO, step=0.05)

    try:
        clone_res = detect_copy_move(cv2_proc, nfeatures=nfeatures, ratio_thresh=ratio_thresh)
    except Exception as error:
        st.error(f"Copy-move detection could not be completed: {str(error)[:240]}")
        return

    st.image(clone_res.visualization_pil, caption=f"Copy-Move Matches Visualization (Matches: {clone_res.matched_pairs_count}, RANSAC Inliers: {clone_res.ransac_inliers_count})", width="stretch")
    
    if clone_res.is_clone_detected:
        st.warning(clone_res.summary_notes)
    else:
        st.success(clone_res.summary_notes)


def render_compression(comp_res: CompressionResult):
    st.subheader("Compression Artifact Analysis")
    if comp_res is None:
        st.error("Compression analysis could not be completed for this image.")
        return
    st.write(f"**Image Format:** `{comp_res.image_format}`")
    st.write(f"**Estimated JPEG Quality:** `{comp_res.estimated_jpeg_quality if comp_res.estimated_jpeg_quality else 'N/A'}`")
    st.write(f"**8x8 Grid Blockiness Score:** `{comp_res.blockiness_score}`")
    st.info(comp_res.summary_notes)


def render_histograms(hist_res):
    st.subheader("Image Intensity Histograms")
    if hist_res is None:
        st.error("Histogram analysis could not be completed for this image.")
        return
    st.pyplot(hist_res.histogram_figure)
    st.info(hist_res.summary_notes)


def render_edge(cv2_proc):
    st.subheader("Canny Edge Detection")
    c1, c2 = st.columns(2)
    low_thresh = c1.slider("Canny Low Threshold", 10, 150, DEFAULT_CANNY_LOW)
    high_thresh = c2.slider("Canny High Threshold", 100, 300, DEFAULT_CANNY_HIGH)

    try:
        edge_res = detect_edges(cv2_proc, low_threshold=low_thresh, high_threshold=high_thresh)
    except Exception as error:
        st.error(f"Canny edge analysis could not be completed: {str(error)[:240]}")
        return
    
    col1, col2 = st.columns(2)
    col1.image(cv2_to_pil(cv2_proc), caption="Original Image", width="stretch")
    col2.image(edge_res.edge_map_pil, caption=f"Edge Map (Density: {edge_res.edge_density_pct}%)", width="stretch")
    st.info(edge_res.summary_notes)


def render_evidence(evidence_sum: EvidenceSummary):
    st.subheader("Consolidated Forensic Evidence Summary")
    st.markdown(f"### Analysis Indicator Level: **{evidence_sum.indicator_level}** (Score: {evidence_sum.total_score})")
    st.write(evidence_sum.overall_interpretation)
    
    st.markdown("#### Detailed Technique Breakdown")
    for item in evidence_sum.evidence_items:
        st.markdown(f"- **{item.technique}**: `{item.result_status}` (+{item.weight} pts)<br>&nbsp;&nbsp;&nbsp;&nbsp;*{item.interpretation}*", unsafe_allow_html=True)

    st.warning(evidence_sum.disclaimer)


def render_report(case_id, filename, sha256_hash, meta_res, ela_res, noise_res, edge_res, clone_res, comp_res, evidence_sum, hist_res):
    st.subheader("Generate & Download Forensic PDF Report")
    st.write("Click below to compile all forensic findings, metadata tables, ELA images, and evidence scores into an official PDF report.")

    if st.button("🚀 Compile PDF Report"):
        with st.spinner("Compiling PDF report with ReportLab..."):
            pdf_path = generate_pdf_report(
                case_id=case_id,
                filename=filename,
                sha256_hash=sha256_hash,
                metadata_res=meta_res,
                ela_res=ela_res,
                noise_res=noise_res,
                edge_res=edge_res,
                clone_res=clone_res,
                comp_res=comp_res,
                evidence_sum=evidence_sum
            )
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()

            st.success(f"✅ Report compiled successfully: `{os.path.basename(pdf_path)}`")
            st.download_button(
                label="📥 Download Forensic PDF Report",
                data=pdf_bytes,
                file_name=os.path.basename(pdf_path),
                mime="application/pdf"
            )


def render_about():
    st.subheader("About ImageGuard & Academic Context")
    st.markdown("""
    **ImageGuard** is a digital image forensics desktop dashboard developed for a Computer Engineering mini project.
    
    ### Key Features
    1. **EXIF Metadata Inspection**: Software signature identification.
    2. **Error Level Analysis (ELA)**: Recompression delta detection.
    3. **Noise Residual Analysis**: Spatial noise variance evaluation across quadrants.
    4. **Copy-Move (Clone) Forgery Detection**: Intra-image ORB feature descriptor matching with RANSAC verification.
    5. **JPEG Compression & Blockiness Metrics**: 8x8 DCT boundary discontinuities.
    6. **Canny Edge Boundary Isolation**: Structural outline checks.
    7. **Consolidated Evidence Aggregation**: Transparent heuristic indicator scoring.
    8. **ReportLab PDF Generator**: Professional publication-quality report output.
    
    *Built with Python 3.11, Streamlit, OpenCV, Pillow, NumPy, Matplotlib, and ReportLab.*
    """)


if __name__ == "__main__":
    main()
