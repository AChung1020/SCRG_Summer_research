import numpy as np
import argparse
import imutils
import cv2
import os
from matplotlib import pyplot as plt

MAX_FEATURES = 40  # Increased to improve matching quality
GOOD_MATCH_PERCENT = 0.90

# Function to preprocess thermal images
def preprocess_thermal_image(image):
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
   
    # Enhance contrast
    clahe = cv2.createCLAHE(clipLimit=10.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
   
    # Apply adaptive threshold to obtain binary image
    binary = cv2.adaptiveThreshold(enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
   
    # Find contours and fill them to create filled rectangular blocks
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    filled = np.zeros_like(binary)
    cv2.drawContours(filled, contours, -1, (255), thickness=cv2.FILLED)
   
    # Perform morphological open to remove lines
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    morph_opened = cv2.morphologyEx(filled, cv2.MORPH_OPEN, kernel)
   
    # Draw bounding rectangles around largest rectangles
    contours, _ = cv2.findContours(morph_opened, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    rect_img = image.copy()
    for cnt in contours:
        if cv2.contourArea(cnt) > 1000:  # Adjust the threshold as needed
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(rect_img, (x, y), (x + w, y + h), (0, 255, 0), 2)
   
    cv2.imshow("Preprocessed Thermal Image", rect_img)
    cv2.waitKey(0)  # Wait for a key press to close the window
    cv2.destroyAllWindows()  # Close the window after the key press
   
    return morph_opened

# Function to preprocess visible images
def preprocess_visible_image(image):
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
   
    # Apply adaptive threshold to obtain binary image
    binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
   
    # Find contours and fill them to create filled rectangular blocks
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    filled = np.zeros_like(binary)
    cv2.drawContours(filled, contours, -1, (255), thickness=cv2.FILLED)
   
    # Perform morphological open to remove lines
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    morph_opened = cv2.morphologyEx(filled, cv2.MORPH_OPEN, kernel)
   
    # Draw bounding rectangles around largest rectangles
    contours, _ = cv2.findContours(morph_opened, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    rect_img = image.copy()
    for cnt in contours:
        if cv2.contourArea(cnt) > 1000:  # Adjust the threshold as needed
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(rect_img, (x, y), (x + w, y + h), (0, 255, 0), 2)
   
    cv2.imshow("Preprocessed Visible Image", rect_img)
    cv2.waitKey(0)  # Wait for a key press to close the window
    cv2.destroyAllWindows()  # Close the window after the key press
   
    return morph_opened

# Function to align the thermal and visible image, it returns the homography matrix
def alignImages(im1, im2, filename):
    # Preprocess images
    im2Gray = preprocess_thermal_image(im2)
    im1Gray = preprocess_visible_image(im1)

    # Apply edge detection
    im2Edges = cv2.Canny(im2Gray, 50, 200)
    im1Edges = cv2.Canny(im1Gray, 50, 200)
   
    # Detect ORB features and compute descriptors
    orb = cv2.ORB_create(MAX_FEATURES)
    keypoints1, descriptors1 = orb.detectAndCompute(im1Edges, None)
    keypoints2, descriptors2 = orb.detectAndCompute(im2Edges, None)

    # Visualize edges
    cv2.imshow("Edges Image 1", im1Edges)
    cv2.imshow("Edges Image 2", im2Edges)
    cv2.waitKey(0)  # Wait for a key press to close the windows
    cv2.destroyAllWindows()  # Close the windows after the key press

    # Match features
    matcher = cv2.DescriptorMatcher_create(cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING)
    matches = matcher.match(descriptors2, descriptors1, None)
   
    # Sort matches by score
    matches.sort(key=lambda x: x.distance, reverse=False)
   
    # Remove not so good matches
    numGoodMatches = int(len(matches) * GOOD_MATCH_PERCENT)
    matches = matches[:numGoodMatches]
   
    # Draw top matches
    imMatches = cv2.drawMatches(im2, keypoints2, im1, keypoints1, matches, None)
    plt.imshow(imMatches), plt.show()
    cv2.imwrite(os.path.join('./registration/', filename), imMatches)
   
    # Extract location of good matches
    points1 = np.zeros((len(matches), 2), dtype=np.float32)
    points2 = np.zeros((len(matches), 2), dtype=np.float32)
   
    for i, match in enumerate(matches):
        points1[i, :] = keypoints2[match.queryIdx].pt
        points2[i, :] = keypoints1[match.trainIdx].pt


   
    # Find homography
    h, mask = cv2.findHomography(points1, points2, cv2.RANSAC)
   
    # Use homography
    height, width, channels = im2.shape
    im1Reg = cv2.warpPerspective(im1, h, (width, height))
   
    return im1Reg, h

# Construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True, help="Path to images where template will be matched")
ap.add_argument("-v", "--visualize", action='store_true', help="Flag indicating whether or not to visualize each iteration")
args = vars(ap.parse_args())

# Load the template image (thermal image)
template = cv2.imread('thermal/' + args["image"] + '.jpg')
template = preprocess_thermal_image(template)
template = cv2.Canny(template, 50, 200)
(tH, tW) = template.shape[:2]
cv2.imshow("Template", template)

# Load the visible image
image = cv2.imread('visible/' + args["image"] + '.jpg')
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
# cv2.imshow("Image", image)
# cv2.imshow("Image", crop_img)

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

# Align images and compute homography
refFilename = "thermal/" + args["image"] + '.jpg'
print("Reading reference image: ", refFilename)
imReference = cv2.imread(refFilename, cv2.IMREAD_COLOR)

imFilename = "output/" + args["image"] + '.jpg'
print("Reading image to align: ", imFilename)
im = cv2.imread(imFilename, cv2.IMREAD_COLOR)
file_name = args["image"] + '.jpg'
imReg, h = alignImages(im, imReference, file_name)
cv2.imshow('imreg', imReg)
cv2.waitKey(0)  # Wait for a key press to close the window
cv2.destroyAllWindows()  # Close the window after the key press

print("Estimated homography: \n", h)