# ImageGuard - PowerPoint Presentation Structure (15 Slides)
## Final-Year Computer Engineering Project Pitch & Defense Guide

---

### Slide 1: Title Slide
- **Title:** ImageGuard – Digital Image Forensics and Tampering Analysis Tool
- **Subtitle:** A Passive Multi-Module Forensic Workstation for Image Integrity Verification
- **Presenter:** [Student Name] | Final Year Computer Engineering
- **Guide/Mentor:** [Project Guide Name]
- **Speaking Script:** "Good morning respected members of the panel and project guide. Today I am presenting ImageGuard, a digital image forensics tool designed to analyze digital images for signs of tampering using non-destructive computer vision algorithms."

---

### Slide 2: Introduction & Motivation
- **Bullet Points:**
  - Digital image manipulation is widespread via software like Photoshop, Canva, and AI editors.
  - Verification of visual evidence is critical in journalism, law enforcement, and insurance.
  - Need for explainable, accessible, passive forensic tools.
- **Speaking Script:** "With the accessibility of editing tools, visual content can be modified easily. Our motivation was to build a tool that helps investigators analyze images passively without relying on watermarks or expensive hardware."

---

### Slide 3: Problem Statement
- **Bullet Points:**
  - Commercial forensic tools are expensive and proprietary.
  - Black-box AI tools lack scientific transparency and produce unexplainable outputs.
  - Misinterpreting forensic evidence leads to false claims of authenticity or forgery.
- **Speaking Script:** "Existing solutions are either costly or produce black-box predictions without showing the underlying pixel statistics. ImageGuard provides transparent evidence aggregation across distinct techniques."

---

### Slide 4: Proposed Solution - ImageGuard
- **Bullet Points:**
  - Modular Python-based workstation powered by Streamlit and OpenCV.
  - Multi-layered analysis: Metadata, ELA, Noise, Copy-Move, Compression, Histograms, Edges.
  - Automated ReportLab PDF report generation.
- **Speaking Script:** "ImageGuard is built with Python and Streamlit. It integrates seven distinct analysis modules into a unified dashboard, generating a downloadable PDF report for case documentation."

---

### Slide 5: System Architecture
- **Bullet Points:**
  - Ingestion & Validation Layer -> Preprocessing & Cryptographic Hashing (SHA-256).
  - Parallel Forensic Engine Modules.
  - Transparent Heuristic Evidence Aggregation Engine.
  - Dashboard UI & PDF Compiler.
- **Speaking Script:** "Here we see the system architecture. Uploaded images are validated and hashed using SHA-256 before being passed to our seven independent analytical modules."

---

### Slide 6: Cryptographic Integrity & Metadata Analysis
- **Bullet Points:**
  - SHA-256 and MD5 hashes ensure file integrity (Chain of Custody).
  - Parses EXIF camera tags (Make, Model, Date/Time, Exposure).
  - Detects digital editing software markers (Photoshop, GIMP, Canva).
- **Speaking Script:** "The metadata module extracts camera acquisition details and checks for editing software tags, while SHA-256 ensures the image file content remains verifiable."

---

### Slide 7: Error Level Analysis (ELA)
- **Bullet Points:**
  - Re-compresses image at controlled quality (default 90%).
  - Calculates absolute pixel brightness difference.
  - Highlights regions with inconsistent JPEG compression histories.
- **Speaking Script:** "Error Level Analysis works by re-compressing the image. Regions inserted from another source often display different error levels compared to original areas."

---

### Slide 8: Spatial Noise Residual Analysis
- **Bullet Points:**
  - Subtracts Gaussian low-pass filter to isolate high-frequency noise.
  - Computes noise variance across 2x2 spatial quadrants.
  - Identifies non-uniform noise distribution across canvas.
- **Speaking Script:** "Noise residual analysis isolates fine sensor grain. Mismatched noise variances across image quadrants suggest splicing or localized retouching."

---

### Slide 9: Copy-Move / Clone Detection (ORB + RANSAC)
- **Bullet Points:**
  - Extracts keypoints & descriptors using ORB detector.
  - Filters out self-matches and adjacent texture points using spatial distance thresholds.
  - Applies Lowe's ratio test and RANSAC affine verification.
- **Speaking Script:** "For copy-move forgery, where an object is cloned within the image, we match ORB feature descriptors and verify their spatial geometry using RANSAC."

---

### Slide 10: Compression & Histogram Analysis
- **Bullet Points:**
  - Measures 8x8 DCT boundary discontinuities (Grid Blockiness Metric).
  - Generates Red, Green, Blue, and Grayscale histograms.
  - Calculates dynamic range and statistical moments.
- **Speaking Script:** "Compression analysis evaluates 8x8 blocking artifacts, while histogram analysis displays color distribution and luminance statistics."

---

### Slide 11: Heuristic Evidence Engine & Indicator Levels
- **Bullet Points:**
  - Combines findings into an **Analysis Indicator Level** (`LOW`, `MODERATE`, `HIGH`).
  - Transparent point weights for each technique.
  - Explicit disclaimer: Heuristic score, NOT statistical forgery probability.
- **Speaking Script:** "The evidence engine aggregates scores into an Indicator Level. Crucially, we clearly state that this is a project heuristic and not a definitive claim of fake or real."

---

### Slide 12: Streamlit Workstation UI Demo
- **Bullet Points:**
  - Responsive metric cards, navigation sidebar, and tabbed panels.
  - Interactive parameters (ELA quality, Canny thresholds, ORB feature counts).
  - Downloadable PDF report generator.
- **Speaking Script:** "Our dashboard features an intuitive sidebar, real-time metric cards, interactive parameter controls, and one-click PDF report downloads."

---

### Slide 13: Experimental Results & Sample Findings
- **Bullet Points:**
  - Evaluated on pristine, recompressed, and copy-move manipulated test images.
  - Successfully highlights cloned regions in synthetic copy-move tests.
  - Accurately flags software metadata in modified files.
- **Speaking Script:** "We tested ImageGuard on controlled sample datasets. The ORB copy-move module effectively isolated cloned regions, while ELA highlighted compression variance."

---

### Slide 14: Advantages & System Limitations
- **Advantages:** Lightweight, explainable, no GPU required, professional PDF export.
- **Limitations:** Passive techniques can yield false positives from web compression or repetitive natural textures.
- **Speaking Script:** "While ImageGuard is lightweight and explainable, passive techniques have inherent limitations such as false matches on repetitive textures like leaves or tiles."

---

### Slide 15: Conclusion & Future Scope
- **Bullet Points:**
  - Developed a practical, college-ready digital image forensics tool.
  - Future work: DCT frequency domain matching, PRNU sensor fingerprinting, lightweight AI classifiers.
- **Speaking Script:** "In conclusion, ImageGuard successfully provides a multi-module forensic analysis environment for students and investigators. Thank you. I welcome your questions."
