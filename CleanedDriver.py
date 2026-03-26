# ==============================
# IMPORT LIBRARIES
# ==============================
import cv2
import numpy as np
import matplotlib.pyplot as plt


# ==============================
# LOAD IMAGE & PREPROCESSING
# ==============================
# Read input image
img = cv2.imread("img.jpg")

# Convert to grayscale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Apply adaptive thresholding (handles uneven lighting)
thresh = cv2.adaptiveThreshold(
    gray, 255,
    cv2.ADAPTIVE_THRESH_MEAN_C,
    cv2.THRESH_BINARY_INV,
    15, 8
)


# ==============================
# DESKEWING USING HOUGH TRANSFORM
# ==============================
# Detect edges
edges = cv2.Canny(thresh, 50, 150)

# Detect lines using Hough Transform
lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)

# Compute angles of detected lines
angles = []
for rho, theta in lines[:, 0]:
    angle = (theta * 180 / np.pi) - 90
    angles.append(angle)

# Use median angle to correct skew
median_angle = np.median(angles)

# Get image center
(h, w) = img.shape[:2]
center = (w // 2, h // 2)

# Rotate image to deskew
M = cv2.getRotationMatrix2D(center, median_angle, 1.0)
deskewed = cv2.warpAffine(thresh, M, (w, h))

# Convert original image to RGB (for plotting)
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


# ==============================
# STAFF LINE REMOVAL
# ==============================

# --- 1. Detect and Remove Horizontal Staff Lines ---
horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))

# Extract horizontal lines
staff_lines = cv2.morphologyEx(deskewed, cv2.MORPH_OPEN, horizontal_kernel)

# Thicken detected lines to ensure full removal
thicken_h = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 3))
staff_lines_thickened = cv2.dilate(staff_lines, thicken_h, iterations=1)

# Subtract staff lines from image
no_staff = cv2.subtract(deskewed, staff_lines_thickened)


# --- 2. Repair Image (Fix broken stems and bar lines) ---
stem_repair_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 7))

repaired = cv2.morphologyEx(
    no_staff,
    cv2.MORPH_CLOSE,
    stem_repair_kernel
)


# --- 3. Remove Vertical Bar Lines using Shape Filtering ---
final_cleaned = repaired.copy()

# Find contours
contours, _ = cv2.findContours(
    final_cleaned,
    cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE
)

# Remove tall & thin contours (bar lines)
for c in contours:
    x, y, w, h = cv2.boundingRect(c)

    # Bar line condition (tall and narrow)
    if h > 40 and w < 10:
        cv2.drawContours(final_cleaned, [c], -1, 0, cv2.FILLED)


# ==============================
# NOTE DETECTION (BOUNDING BOXES)
# ==============================
output_boxes = img_rgb.copy()

# Slightly thicken note components to improve detection
kernel_fatten = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
fattened_notes = cv2.dilate(final_cleaned, kernel_fatten, iterations=1)

# Find contours on processed image
final_contours, _ = cv2.findContours(
    fattened_notes,
    cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE
)

# Draw bounding boxes around detected notes
for c in final_contours:
    x, y, w, h = cv2.boundingRect(c)

    # Ignore very small noise
    if h > 10 and w > 5:
        cv2.rectangle(output_boxes, (x, y), (x + w, y + h), (255, 0, 0), 2)


# ==============================
# VISUALIZATION (OUTPUT)
# ==============================
plt.figure(figsize=(12, 6))

# --- Original Image ---
plt.subplot(4, 1, 1)
plt.imshow(img_rgb)
plt.title('Original Image')
plt.axis('off')

# --- Thresholded Image ---
plt.subplot(4, 1, 2)
plt.imshow(thresh, cmap='gray')
plt.title('Adaptive Threshold')
plt.axis('off')

# --- Cleaned Image ---
plt.subplot(4, 1, 3)
plt.imshow(final_cleaned, cmap='gray')
plt.title('Final Cleaned (No Bar Lines)')
plt.axis('off')

# --- Final Detection ---
plt.subplot(4, 1, 4)
plt.imshow(output_boxes)
plt.title('Detected Notes')
plt.axis('off')

# Render plots
plt.tight_layout()
plt.show()
