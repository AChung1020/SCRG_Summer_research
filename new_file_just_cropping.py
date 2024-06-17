import numpy as np
import argparse
import imutils
import cv2
import os
from matplotlib import pyplot as plt

# Function to preprocess thermal images
def preprocess_thermal_image(image):
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
   
    # Enhance contrast
    clahe = cv2.createCLAHE(clipLimit=10.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # Apply Gaussian blur to reduce noise
    _, enhanced = cv2.threshold(enhanced, 200, 210, cv2.THRESH_TRUNC)
    blurred = cv2.GaussianBlur(enhanced, (5, 5), sigmaX = 10)
    

    return blurred

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True, help="Path to images where template will be matched")
ap.add_argument("-v", "--visualize", action='store_true', help="Flag indicating whether or not to visualize each iteration")
args = vars(ap.parse_args())

# Load the template image (thermal image)
template = cv2.imread('thermal/' + args["image"] + '.jpg')
template = preprocess_thermal_image(template)

# Perform edge detection on the entire template
edges_template = cv2.Canny(template, 20, 200)

# Create a mask for the right half of the template
(tH, tW) = edges_template.shape[:2]
mask = np.zeros((tH, tW), dtype=np.uint8)
mask[:, tW//2:] = 255

# Apply the mask to the edge-detected template
masked_template = cv2.bitwise_and(edges_template, edges_template, mask=mask)



cv2.imshow("Masked Template", masked_template)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Load the visible image
image = cv2.imread('visible/' + args["image"] + '.jpg')
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
found = None

# Loop over the scales of the image
for scale in np.linspace(0.45, 1.0, 100)[::-1]:
    resized = imutils.resize(gray, width=int(gray.shape[1] * scale))
    r = gray.shape[1] / float(resized.shape[1])

    if resized.shape[0] < tH or resized.shape[1] < tW:
        break

    edged = cv2.Canny(resized, 50, 200)
    cv2.imshow("Visualize", edged)
    cv2.waitKey(0)
    result = cv2.matchTemplate(edged, masked_template, cv2.TM_CCOEFF)
    (_, maxVal, _, maxLoc) = cv2.minMaxLoc(result)

    if args.get("visualize", False):
        clone = np.dstack([edged, edged, edged])
        cv2.rectangle(clone, (maxLoc[0], maxLoc[1]), (maxLoc[0] + tW, maxLoc[1] + tH), (0, 0, 255), 2)
        cv2.imshow("Visualize", clone)
        cv2.waitKey(0)

    if found is None or maxVal > found[0]:
        found = (maxVal, maxLoc, r)

(_, maxLoc, r) = found
(startX, startY) = (int(maxLoc[0] * r), int(maxLoc[1] * r))
(endX, endY) = (int((maxLoc[0] + tW) * r), int((maxLoc[1] + tH) * r))

cv2.rectangle(image, (startX, startY), (endX, endY), (0, 0, 255), 2)
crop_img = image[startY:endY, startX:endX]

cv2.imshow("Detected Image", image)
cv2.imshow("Cropped Image", crop_img)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Load the thermal image again (for alignment)
thermal_image = cv2.imread('thermal/' + args["image"] + '.jpg', cv2.IMREAD_COLOR)

# Resize the cropped visible image to the thermal image dimensions
crop_img_resized = cv2.resize(crop_img, (thermal_image.shape[1], thermal_image.shape[0]))

# Save the resized visible image
cv2.imwrite(os.path.join('./output/', args["image"] + '.jpg'), crop_img_resized)

# Concatenate and save the result
final = np.concatenate((crop_img_resized, thermal_image), axis=1)
cv2.imwrite(os.path.join('./results/', args["image"] + '.jpg'), final)

cv2.waitKey(0)