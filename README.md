# 🎼 OMR-PreProcessor: Musical Feature Isolation

[![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-Image%20Processing-green?logo=opencv)](https://opencv.org/)
[![NumPy](https://img.shields.io/badge/NumPy-Matrix%20Ops-orange?logo=numpy)](https://numpy.org/)
[![Matplotlib](https://img.shields.io/badge/Matplotlib-Visualization-yellow?logo=plotly)](https://matplotlib.org/)
[![License](https://img.shields.io/badge/License-MIT-lightgrey)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-success)]()

An **Optical Music Recognition (OMR)** preprocessing pipeline built with Python and OpenCV. This project focuses on the difficult task of isolating musical notes from complex staff environments using geometric and morphological analysis.

---

## 🚀 Key Features
* **Automatic Deskewing:** Corrects camera tilt/rotation using Hough Line Transforms to ensure perfectly horizontal staff lines.
* **Selective Feature Removal:** Employs custom Morphological Kernels (Open/Close) to independently isolate and erase horizontal staff lines and vertical bar lines.
* **Dual-Stage Restoration:** Uses a vertical "closing" technique to repair note stems often damaged during staff line removal.
* **Geometric Filtering:** Separates musical primitives from alphanumeric "noise" (like fingering numbers) using aspect ratio and contour area analysis.



---

## 🛠 Project Workflow
1.  **Adaptive Thresholding:** Converts grayscale input to binary while handling uneven lighting.
2.  **Line Extraction:** Identifies 5-line staff structures via horizontal projection profiles.
3.  **Subtraction & Repair:** Erases structural lines and heals broken note stems to create a "notes-only" mask.
4.  **Segmentation:** Detects individual note-heads and stems, preparing them for future CNN classification.

---

## 🧪 Current Status (Interim Review)
The pipeline currently achieves high-accuracy note isolation on high-resolution inputs. It successfully handles:
- [x] Bar line removal via independent vertical kernels.
- [x] Stem repair using vertical morphological closing.
- [x] Basic noise filtering for non-musical symbols.

---

## 🏗 Built With
* **Python 3.x**
* **OpenCV:** Primary image processing and computer vision library.
* **NumPy:** High-performance matrix operations for projection profiles.
* **Matplotlib:** For visualization of the multi-stage transformation grid.
