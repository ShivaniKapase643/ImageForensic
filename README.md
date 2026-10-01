# ImageGuard – Digital Image Forensics and Tampering Analysis Tool

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Framework: Streamlit](https://img.shields.io/badge/Framework-Streamlit-red.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Official Tagline:** *Analyze. Investigate. Verify.*  
> **Subtitle:** *Digital Image Forensics & Tampering Analysis Workstation*

---

## 📌 Project Overview

**ImageGuard** is a lightweight, professional digital image forensics workstation designed for computer vision engineers, digital investigators, and academic researchers. It analyzes digital images using non-destructive metadata extraction, error level analysis (ELA), spatial noise variance, ORB feature copy-move detection, compression artifact inspection, channel histograms, and Canny edge detection.

All findings are aggregated into a transparent **Analysis Indicator Level** (`LOW`, `MODERATE`, `HIGH`) and can be exported as an official PDF report using ReportLab.

---

## 🎯 Key Features

- **Cryptographic File Hash**: Calculates SHA-256 and MD5 checksums to guarantee digital chain-of-custody integrity.
- **EXIF & Technical Metadata Analysis**: Extracts camera make/model, acquisition date/time, GPS coordinates, exposure parameters, and flags digital editing software signatures (e.g. Photoshop, GIMP, Canva).
- **Error Level Analysis (ELA)**: Re-compresses JPEG images at controlled quality thresholds to reveal inconsistent re-compression error magnitudes.
- **Noise Residual Analysis**: Subtractions Gaussian-blurred low-pass images to isolate high-frequency grain and measures spatial noise variance across grid quadrants.
- **Copy-Move (Clone) Detection**: Uses OpenCV's ORB detector with Lowe's ratio test and RANSAC geometric affine estimation to highlight duplicated image regions.
- **JPEG Compression & Blockiness Metrics**: Evaluates 8x8 DCT boundary discontinuities and estimates quantization tables.
- **Grayscale & RGB Channel Histograms**: Computes dynamic range, luminance distribution, and statistical moments (Mean, Median, Std Dev, Min, Max).
- **Canny Edge Detection**: User-adjustable edge map generation to highlight boundary discontinuities.
- **Consolidated Evidence Engine**: Applies transparent heuristic rules to derive an overall **Analysis Indicator Level**.
- **ReportLab PDF Generator**: Compiles executive summaries, metadata tables, forensic visualizations, and legal disclaimers into a downloadable PDF report.

---

## 🏗 Project Architecture & Structure

```
ImageForensic/
│
├── app.py                         # Streamlit Main Workstation & UI Router
│
├── config/
│   ├── __init__.py
│   └── settings.py                # Configuration constants, thresholds, paths & themes
│
├── modules/
│   ├── __init__.py
│   ├── hash_generator.py          # Cryptographic SHA-256 / MD5 hashing
│   ├── metadata_analyzer.py      # EXIF parser & editing software detector
│   ├── ela_analyzer.py           # Error Level Analysis (JPEG re-compression)
│   ├── noise_analyzer.py         # Noise residual map & spatial variance
│   ├── histogram_analyzer.py     # Channel histograms & statistical metrics
│   ├── edge_analyzer.py          # Canny edge detector module
│   ├── clone_detector.py         # ORB feature-matching copy-move detector
│   ├── compression_analyzer.py   # JPEG quantization & blockiness metric
│   ├── evidence_engine.py       # Heuristic evidence engine & score calculator
│   └── report_generator.py       # ReportLab PDF compiler
│
├── utils/
│   ├── __init__.py
│   ├── image_utils.py            # Image array conversions & dynamic resizing
│   ├── validation.py             # File size, mime-type & integrity validation
│   └── formatting.py             # String, byte size & timestamp formatters
│
├── assets/
│   └── sample_images/            # Synthetic test dataset directory
│
├── reports/                      # Output directory for generated PDF reports
│
├── tests/                        # Unit test suite (pytest)
│   ├── test_validation.py
│   ├── test_hash.py
│   ├── test_metadata.py
│   ├── test_ela.py
│   ├── test_noise.py
│   ├── test_clone.py
│   └── test_evidence.py
│
├── create_sample_data.py         # Utility script to build synthetic test dataset
├── requirements.txt              # Dependency specifications
├── README.md                     # Documentation
├── LICENSE                       # MIT License
└── academic_docs.md              # Detailed Academic Project Report
```

---

## ⚙️ Installation & Running Instructions (Windows Laptop)

### Step 1: Open Terminal / PowerShell in the cloned project directory

### Step 2: Create & Activate Virtual Environment
```powershell
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Required Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Generate Demonstration Sample Data
```powershell
python create_sample_data.py
```

### Step 5: Run Automated Unit Test Suite
```powershell
pytest
```

### Step 6: Launch Streamlit Dashboard
```powershell
streamlit run app.py
```

The application will launch automatically in your web browser at `http://localhost:8501` (Streamlit's local default port).

## Deploy on Render

This repository includes a Render Blueprint (`render.yaml`) for a Python web service. It installs the dependencies from `requirements.txt` and starts Streamlit bound to `0.0.0.0` on the `PORT` assigned by Render.

### Deploy with the Blueprint

1. Push this repository to GitHub.
2. In Render, choose **New → Blueprint** and connect the `ImageForensic` repository.
3. Review the `imageguard-forensics` web service created from `render.yaml`, then deploy it.
4. Render builds with `pip install -r requirements.txt` and starts with `python run_streamlit.py`.

The repository's `.python-version` selects Python 3.11.9, matching the local virtual environment. No application secrets or additional environment variables are required; Render supplies `PORT` automatically. The Streamlit upload limit is configured to 25 MB, matching the application validator, and uploads are limited to 20 million decoded pixels to constrain memory use.

### Render limitations

- Free web services can spin down after inactivity and may take time to wake on the next visit.
- The free service filesystem is ephemeral. Generated PDF reports are available through the app's download button but are not durable server-side storage.
- Image processing and PDF generation use service memory and CPU. Very large images are rejected, and free instance resource limits can affect processing speed.
- ExifTool is not required; EXIF extraction uses Pillow and degrades safely when metadata is absent or unreadable.

### Run locally

On Windows, follow the installation steps above and run `streamlit run app.py`. To exercise the Render launcher locally in PowerShell, set `$env:PORT = "18765"` and run `python run_streamlit.py`.

See [DEPLOYMENT.md](DEPLOYMENT.md) for exact Render settings and troubleshooting.

---

## 🛡 Academic & Scientific Disclaimer

> **IMPORTANT FORENSIC PRINCIPLE**:  
> ImageGuard uses non-destructive heuristic indicators to assist human forensic examiners. It **does NOT claim definitive proof** that an image is "real" or "fake".  
> Forensic techniques can yield false positives (e.g. from camera compression, social media re-saving, repetitive natural textures) and false negatives. Human analyst review is required.

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for details.
