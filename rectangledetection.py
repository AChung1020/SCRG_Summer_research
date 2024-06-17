import cv2
import numpy as np
from matplotlib import pyplot as plt

# Load the image
image_path = r"C:\Users\andre\OneDrive\Desktop\SCRG\thermal\thermal.jpg"
image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

# Apply Histogram Equalization to enhance contrast
equalized = cv2.equalizeHist(image)

# Apply Gaussian Blur to smooth the image
blurred = cv2.GaussianBlur(equalized, (5, 5), 0)

# Apply Adaptive Thresholding
adaptive_thresh = cv2.adaptiveThreshold(
    blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
)

# Apply Morphological Operations
kernel = np.ones((3, 3), np.uint8)
morph = cv2.morphologyEx(adaptive_thresh, cv2.MORPH_CLOSE, kernel)

# Apply Canny Edge Detection
edges = cv2.Canny(morph, 50, 150)

# Find contours
contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

# Draw all contours
contour_image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
cv2.drawContours(contour_image, contours, -1, (0, 255, 0), 2)

# Filter contours to find rectangles
rect_contours = []
for contour in contours:
    epsilon = 0.02 * cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, epsilon, True)
    if len(approx) == 4:
        x, y, w, h = cv2.boundingRect(approx)
        aspect_ratio = float(w) / h
        if 0.5 <= aspect_ratio <= 2.0:  # Adjust the range as needed
            rect_contours.append(contour)

# Draw the rectangle contours
rectangles_image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
cv2.drawContours(rectangles_image, rect_contours, -1, (0, 255, 0), 2)

# Display the results
plt.figure(figsize=(12, 12))
plt.subplot(2, 3, 1)
plt.title('Original Image')
plt.imshow(image, cmap='gray')
plt.subplot(2, 3, 2)
plt.title('Equalized Image')
plt.imshow(equalized, cmap='gray')
plt.subplot(2, 3, 3)
plt.title('Adaptive Threshold')
plt.imshow(adaptive_thresh, cmap='gray')
plt.subplot(2, 3, 4)
plt.title('Morphological Operations')
plt.imshow(morph, cmap='gray')
plt.subplot(2, 3, 5)
plt.title('Edges')
plt.imshow(edges, cmap='gray')
plt.subplot(2, 3, 6)
plt.title('Detected Rectangles')
plt.imshow(cv2.cvtColor(rectangles_image, cv2.COLOR_BGR2RGB))
plt.show()
