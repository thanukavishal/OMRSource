# 🎼 OMR Web Application: Sheet Music to MIDI Converter

[![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-Frontend-61DAFB?logo=react)](https://react.dev/)
[![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-green?logo=opencv)](https://opencv.org/)
[![NumPy](https://img.shields.io/badge/NumPy-Matrix%20Ops-orange?logo=numpy)](https://numpy.org/)
[![Matplotlib](https://img.shields.io/badge/Matplotlib-Visualization-yellow?logo=plotly)](https://matplotlib.org/)
[![Vite](https://img.shields.io/badge/Vite-Build%20Tool-646CFF?logo=vite)](https://vitejs.dev/)
[![License](https://img.shields.io/badge/License-MIT-lightgrey)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Completed-success)]()

An **Optical Music Recognition (OMR)** web application that transforms sheet music images into digital musical data through a computer vision pipeline. Built with **Python**, **OpenCV**, and **React**, the system preprocesses music sheets, isolates musical notes using image processing techniques, and generates downloadable **MIDI** files through a modern web interface.

---

## 🚀 Key Features

* **Modern React Web Application:** Upload and process sheet music through an intuitive browser interface.
* **Automatic Deskewing:** Corrects camera tilt and rotation using Hough Line Transforms.
* **Staff & Bar Line Removal:** Removes horizontal staff lines and vertical bar lines using custom morphological operations.
* **Dual-Stage Stem Restoration:** Repairs broken note stems after staff line removal using vertical morphological closing.
* **Geometric Noise Filtering:** Eliminates non-musical symbols using contour area and aspect ratio analysis.
* **Musical Note Isolation:** Produces clean note masks suitable for recognition and MIDI generation.
* **Intermediate Processing Preview:** Displays every major stage of the image processing pipeline.
* **MIDI File Generation:** Converts processed musical notation into downloadable MIDI output.

---

## 🛠 Project Workflow

1. **Upload Sheet Music:** User uploads a PNG, JPG, or JPEG image.
2. **Adaptive Thresholding:** Converts the image into a clean binary representation.
3. **Automatic Deskewing:** Corrects image orientation using Hough Transform.
4. **Staff Line Detection:** Identifies five-line staff structures.
5. **Staff & Bar Line Removal:** Removes structural elements while preserving notes.
6. **Stem Restoration:** Repairs note stems damaged during line removal.
7. **Noise Filtering:** Removes unwanted symbols and artifacts.
8. **Note Segmentation:** Extracts musical notes for further processing.
9. **MIDI Generation:** Converts detected notes into a playable MIDI file.
10. **Result Visualization:** Displays processed images and allows MIDI download.

---

## 🧪 Project Status

The project has been successfully completed with an integrated image processing pipeline and React web application.

### ✅ Completed Features

- [x] React-based frontend
- [x] Python backend API
- [x] Automatic image preprocessing
- [x] Adaptive thresholding
- [x] Automatic deskewing
- [x] Staff line removal
- [x] Vertical bar line removal
- [x] Stem restoration
- [x] Geometric noise filtering
- [x] Musical note segmentation
- [x] MIDI generation
- [x] Processing stage visualization

---

## 🏗 Built With

| Technology | Purpose |
|------------|---------|
| 🐍 **Python 3.x** | Backend processing |
| 👁️ **OpenCV** | Computer vision & image processing |
| 🔢 **NumPy** | Matrix operations |
| 📊 **Matplotlib** | Image visualization |
| ⚛️ **React** | Frontend web application |
| ⚡ **Vite** | React development environment |

---

## 📂 Project Architecture

```text
               React Frontend
                     │
                     ▼
          Upload Sheet Music Image
                     │
                     ▼
          Python Backend (API Server)
                     │
                     ▼
        OpenCV Image Processing Pipeline
                     │
     ┌───────────────┼───────────────┐
     ▼               ▼               ▼
Processed Images   Note Detection   MIDI Generation
     │               │               │
     └───────────────┼───────────────┘
                     ▼
            Results Display & Download
```

---

## 💻 Running the Project

### Backend

```bash
python server.py
```

Runs on:

```
http://127.0.0.1:8000
```

### Frontend

```bash
npm install
npm run dev
```

Runs on:

```
http://127.0.0.1:5173
```

---

## 🔮 Future Enhancements

The current system provides a strong foundation for Optical Music Recognition. Planned improvements include:

- 🎼 Deep Learning-based note classification
- 🎹 Support for chords and polyphonic music
- 🎵 Recognition of rests, clefs, dynamics, and time signatures
- 📄 Multi-page sheet music processing
- 🎶 MusicXML export support
- 🔊 Built-in audio playback
- ☁️ Cloud deployment
- 👤 User accounts and project history
- ⚡ Performance optimization for large scores
- ✍️ Handwritten music recognition

---

## 📸 Sample Processing Pipeline

```
Input Image
      │
      ▼
Adaptive Thresholding
      │
      ▼
Deskewing
      │
      ▼
Staff Line Removal
      │
      ▼
Bar Line Removal
      │
      ▼
Stem Restoration
      │
      ▼
Noise Filtering
      │
      ▼
Note Segmentation
      │
      ▼
Generated MIDI
```

---

## 📄 License

This project is licensed under the **MIT License**.