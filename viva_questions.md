# ImageGuard - Academic Viva Voce Question Bank (45 Q&A)

---

### 1. Fundamentals of Digital Image Forensics

**Q1: What is digital image forensics?**  
*Answer:* Digital image forensics is the science of analyzing digital images to determine their origin, authenticity, and processing history, using metadata inspection, signal processing, and computer vision algorithms.

**Q2: What is the difference between active and passive image forensics?**  
*Answer:* Active forensics relies on pre-embedded data such as digital watermarks or signatures inserted during image capture. Passive (blind) forensics analyzes the image content itself without any prior embedded watermark.

**Q3: Why is SHA-256 hashing used in image forensics?**  
*Answer:* SHA-256 generates a 256-bit cryptographic checksum of the raw image file bytes. If even a single bit of the file is modified, the hash changes completely, establishing file integrity and chain-of-custody.

**Q4: Can digital image forensics definitively prove an image is fake?**  
*Answer:* No. Passive forensic algorithms produce indicators rather than absolute proof. A single technique can yield false positives due to compression, resizing, or natural scene textures. Human expert evaluation is always required.

**Q5: What are EXIF metadata tags?**  
*Answer:* Exchangeable Image File Format (EXIF) is a standard specifying formats for images recorded by digital cameras, storing attributes such as camera make/model, date/time, shutter speed, ISO, GPS coordinates, and software tags.

---

### 2. Error Level Analysis (ELA)

**Q6: How does Error Level Analysis (ELA) work?**  
*Answer:* ELA re-saves an image at a known JPEG quality level (e.g. 90%) and calculates the absolute difference between the original and recompressed image. Regions that respond differently to recompression exhibit higher residual brightness.

**Q7: Why do spliced regions show different error levels in ELA?**  
*Answer:* When an object from one JPEG image is pasted into another JPEG image with a different quality history, the pasted region reaches a different level of compression saturation, causing a localized brightness variation in the ELA difference map.

**Q8: What are the limitations of ELA on PNG or lossless images?**  
*Answer:* PNG is a lossless format that does not contain JPEG quantization matrices. Re-compressing a PNG image into JPEG format introduces uniform compression artifacts across the whole canvas, which can produce high residual baselines.

**Q9: What does the scale parameter in ELA control?**  
*Answer:* The scale parameter amplifies the visual brightness of the absolute difference array so that small pixel discrepancies (e.g. difference of 2-5 levels) become visible to the human eye.

---

### 3. Noise Residual & Spatial Analysis

**Q10: What is noise residual analysis?**  
*Answer:* Noise residual analysis isolates high-frequency image grain by subtracting a low-pass Gaussian-smoothed version of the image from the original grayscale image.

**Q11: Why is noise uniformity important in image forensics?**  
*Answer:* Camera sensors introduce a unique sensor noise profile across an unedited image. Splicing elements from different source images or applying local smoothing introduces regional noise variance mismatches.

**Q12: How does ImageGuard evaluate regional noise variance?**  
*Answer:* ImageGuard divides the noise residual map into 2x2 spatial quadrants, calculates the noise variance in each quadrant, and computes the variance ratio ($\max / \min$). A ratio $> 2.5$ suggests potential non-uniformity.

---

### 4. Copy-Move / Clone Detection

**Q13: What is copy-move forgery?**  
*Answer:* Copy-move forgery occurs when a region of an image is copied and pasted elsewhere within the exact same image, often to conceal objects or duplicate features.

**Q14: How does ORB feature detection work in copy-move detection?**  
*Answer:* ORB (Oriented FAST and Rotated BRIEF) identifies salient corner keypoints and generates rotation-invariant binary feature descriptors for each point.

**Q15: Why is spatial distance filtering necessary in copy-move detection?**  
*Answer:* Keypoints located within the same local texture block (e.g. adjacent pixels in grass or sky) naturally match each other. Spatial filtering suppresses matches where keypoints are closer than a threshold distance (e.g. 30 pixels).

**Q16: What role does RANSAC play in copy-move detection?**  
*Answer:* RANSAC (Random Sample Consensus) tests the geometric homography/affine transformation across candidate keypoint matches to filter out random false matches and verify consistent spatial duplication patterns.

**Q17: What can cause false positives in copy-move detection?**  
*Answer:* Repetitive natural textures, such as windows on a skyscraper, leaves on a tree, pattern fabrics, or crowds, contain identical feature descriptors and can generate candidate matches even without intentional editing.

---

### 5. Compression & Blockiness Artifacts

**Q18: What is JPEG blockiness?**  
*Answer:* JPEG compression divides images into 8x8 pixel blocks and applies Discrete Cosine Transform (DCT) quantization. Recompression or heavy editing creates sharp intensity discontinuities along 8x8 block boundaries.

**Q19: How is the blockiness score calculated?**  
*Answer:* By computing the mean absolute difference between adjacent pixels across 8x8 block boundaries compared to adjacent pixels within the interior of 8x8 blocks.

---

### 6. Software Architecture & Implementation

**Q20: Why was Streamlit chosen for the user interface?**  
*Answer:* Streamlit enables rapid Python-native dashboard creation, reactive widget updating, built-in image rendering, and responsive metric display without requiring heavy frontend JavaScript setup.

**Q21: Why was ReportLab chosen for PDF report generation?**  
*Answer:* ReportLab is a pure-Python library that programmatically compiles structured documents, tables, flowable elements, and embedded visualizations into standalone PDF files.

**Q22: Does ImageGuard require a GPU?**  
*Answer:* No. ImageGuard relies on classic computer vision algorithms (ORB, Canny, Gaussian subtraction, NumPy math) optimized for standard CPU execution.

---

### 7. Core Academic Viva Questions (Q23-Q45 Overview)

**Q23: What is Lowe's ratio test?**  
*Answer:* It retains feature descriptor matches where the distance to the closest match is significantly smaller than the distance to the second-closest match ($d_1 < 0.75 \times d_2$).

**Q24: What is Canny edge detection?**  
*Answer:* A multi-stage edge detection algorithm that uses Gaussian smoothing, intensity gradient calculation, non-maximum suppression, and hysteresis thresholding.

**Q25: What is the purpose of the Evidence Aggregation Engine?**  
*Answer:* It consolidates qualitative and quantitative findings from all forensic modules into an overall **Analysis Indicator Level** (`LOW`, `MODERATE`, `HIGH`) using documented heuristic rules.

**Q26: What is a false positive in digital forensics?**  
*Answer:* When an unedited image is incorrectly flagged as having potential manipulation indicators.

**Q27: What is a false negative in digital forensics?**  
*Answer:* When a manipulated image fails to trigger forensic indicators due to careful post-processing, blurring, or re-compression.

*(Questions 28 through 45 cover detailed Python function parameters, PIL memory management, array reshaping, and metric calculations as documented in `academic_docs.md`.)*
