import numpy as np
import cv2
import os
import imutils

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

# Load the template image (thermal image)
template = cv2.imread(r'C:\Users\andre\OneDrive\Desktop\SCRG\thermal\thermal.jpg')
template = preprocess_thermal_image(template)
template = cv2.Canny(template, 50, 200)
(tH, tW) = template.shape[:2]
cv2.imshow("Template", template)

# Load the visible image
image = cv2.imread(r'C:\Users\andre\OneDrive\Desktop\SCRG\visible\thermal.jpg')
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
found = None


# Loop over the scales of the image
for scale in np.linspace(0.2, 1.0, 20)[::-1]:
    resized = imutils.resize(gray, width=int(gray.shape[1] * scale))
    r = gray.shape[1] / float(resized.shape[1])

    if resized.shape[0] < tH or resized.shape[1] < tW:
        break

    edged = cv2.Canny(resized, 50, 200)
    result = cv2.matchTemplate(edged, template, cv2.TM_CCOEFF)
    (_, maxVal, _, maxLoc) = cv2.minMaxLoc(result)

    # if args.get("visualize", False):
    #     clone = np.dstack([edged, edged, edged])
    #     cv2.rectangle(clone, (maxLoc[0], maxLoc[1]), (maxLoc[0] + tW, maxLoc[1] + tH), (0, 0, 255), 2)
    #     cv2.imshow("Visualize", clone)
    #     cv2.waitKey(0)

    if found is None or maxVal > found[0]:
        found = (maxVal, maxLoc, r)

(_, maxLoc, r) = found
(startX, startY) = (int(maxLoc[0] * r), int(maxLoc[1] * r))
(endX, endY) = (int((maxLoc[0] + tW) * r), int((maxLoc[1] + tH) * r))

cv2.rectangle(image, (startX, startY), (endX, endY), (0, 0, 255), 2)
crop_img = image[startY:endY, startX:endX]
# cv2.imshow("Image", image)
# cv2.imshow("Image", crop_img)

# Load the thermal image again (for alignment)
thermal_image = cv2.imread('thermal/' + 'thermal' + '.jpg', cv2.IMREAD_COLOR)

# Resize the cropped visible image to the thermal image dimensions
crop_img_resized = cv2.resize(crop_img, (thermal_image.shape[1], thermal_image.shape[0]))

# Save the resized visible image
cv2.imwrite(os.path.join('./output/', 'test' + '.jpg'), crop_img_resized)

# Align images
aligned_visible = align_images(crop_img_resized, thermal_preprocessed)

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

