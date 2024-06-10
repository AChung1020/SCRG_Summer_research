import numpy as np
import cv2
import os

# Function to preprocess thermal images
def preprocess_thermal_image(image):
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
   
    # Enhance contrast
    clahe = cv2.createCLAHE(clipLimit=10.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(enhanced, (5, 5), sigmaX=10)
   
    return blurred

# Function to align images using cross-correlation
def align_images(im1, im2):
    # Convert images to grayscale
    im1_gray = cv2.cvtColor(im1, cv2.COLOR_BGR2GRAY)
    im2_gray = im2

    # Find cross-correlation
    result = cv2.matchTemplate(im2_gray, im1_gray, cv2.TM_CCOEFF_NORMED)
    _, _, _, max_loc = cv2.minMaxLoc(result)

    # Calculate offset
    offset_x, offset_y = max_loc

    # Apply offset to align images
    aligned = np.zeros_like(im2_gray)
    aligned[offset_y:offset_y+im1_gray.shape[0], offset_x:offset_x+im1_gray.shape[1]] = im1_gray

    return aligned

# Load images
thermal_image = cv2.imread(r'C:\Users\andre\OneDrive\Desktop\SCRG\thermal\thermal.jpg')
visible_image = cv2.imread(r'C:\Users\andre\OneDrive\Desktop\SCRG\visible\thermal.jpg', cv2.IMREAD_COLOR)

# Resize visible image to 640x480
visible_image = cv2.resize(visible_image, (640, 480))

# Preprocess thermal image
thermal_preprocessed = preprocess_thermal_image(thermal_image)

# Align images
aligned_visible = align_images(visible_image, thermal_preprocessed)

# Ensure aligned_visible has the same number of channels as thermal_image for blending
if aligned_visible.ndim == 2:
    aligned_visible = cv2.cvtColor(aligned_visible, cv2.COLOR_GRAY2BGR)

# Blend images
alpha = 0.5  # Adjust alpha for desired blending effect
blended = cv2.addWeighted(thermal_image, alpha, aligned_visible, 1 - alpha, 0)

# Display and save blended image
cv2.imshow('Blended Image', blended)
cv2.imwrite(r'C:\Users\andre\OneDrive\Desktop\SCRG\results\blended.jpg', blended)
cv2.waitKey(0)
cv2.destroyAllWindows()