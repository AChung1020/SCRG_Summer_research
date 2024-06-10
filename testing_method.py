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

    cv2.imshow("Processed Thermal Image", enhanced)
    cv2.waitKey(0)  # Wait for a key press to close the window
    cv2.destroyAllWindows()  # Close the window after the key press
    
    
    # Apply Gaussian blur to reduce noise
    _, enhanced = cv2.threshold(enhanced, 200, 210, cv2.THRESH_TRUNC)
    blurred = cv2.GaussianBlur(enhanced, (5, 5), sigmaX = 10)
    cv2.imshow("Processed Thermal Image", blurred)
    cv2.waitKey(0)  # Wait for a key press to close the window
    cv2.destroyAllWindows()  # Close the window after the key press
    
    return blurred

# Function to align the thermal and visible image, it returns the homography matrix
def alignImages(im1, im2, filename):
    # Preprocess images to focus on the right quadrants
    height1, width1 = im1.shape[:2]
    height2, width2 = im2.shape[:2]
    im1_cropped = im1[:, width1 // 2:]
    im2_cropped = im2[:, width2 // 2:]
   
    # Convert to grayscale
    im2Gray = preprocess_thermal_image(im2_cropped)
    im1Gray = cv2.cvtColor(im1_cropped, cv2.COLOR_BGR2GRAY)

    # Apply Sobel edge detection to im1Gray
    # sobelx1 = cv2.Sobel(im1Gray, cv2.CV_64F, 1, 0, ksize=31)
    # sobely1 = cv2.Sobel(im1Gray, cv2.CV_64F, 0, 1, ksize=31)
    # im1Edges = cv2.magnitude(sobelx1, sobely1)

    # cv2.normalize(im1Edges, im1Edges, 0, 255, cv2.NORM_MINMAX)
    # im1Edges = np.uint8(im1Edges)

    # Apply Sobel edge detection to im2Gray
    # sobelx2 = cv2.Sobel(im2Gray, cv2.CV_64F, 1, 0, ksize=31)
    # sobely2 = cv2.Sobel(im2Gray, cv2.CV_64F, 0, 1, ksize=31)
    # im2Edges = cv2.magnitude(sobelx2, sobely2)

    # cv2.normalize(im2Edges, im2Edges, 0, 255, cv2.NORM_MINMAX)
    # im2Edges = np.uint8(im2Edges)
    # _, im2Edges = cv2.threshold(im2Edges, 120, 255, cv2.THRESH_BINARY)

    im2Edges = cv2.Canny(im2Gray, 50, 200)
    im1Edges = cv2.Canny(im1Gray, 50, 200)
    # Detect ORB features and compute descriptors

    mask1 = np.zeros(im1Edges.shape, dtype=np.uint8) 
    mask2 = np.zeros(im2Edges.shape, dtype=np.uint8) 
    height, width = im1Edges.shape 
    mask1[:height // 2, :] = 255 # Upper half set to 255 
    mask2[:height // 2, :] = 255 # Upper half set to 255
    
    orb = cv2.ORB_create(MAX_FEATURES)
    keypoints1, descriptors1 = orb.detectAndCompute(im1Edges, mask1)
    keypoints2, descriptors2 = orb.detectAndCompute(im2Edges, mask2)

    # Visualize edges
    cv2.imshow("Sobel Edges Image 1", im1Edges)
    cv2.imshow("Sobel Edges Image 2", im2Edges)


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
    imMatches = cv2.drawMatches(im2_cropped, keypoints2, im1_cropped, keypoints1, matches, None)
    plt.imshow(imMatches), plt.show()
    cv2.imwrite(os.path.join('./registration/', filename), imMatches)
   
    # Extract location of good matches
    points1 = np.zeros((len(matches), 2), dtype=np.float32)
    points2 = np.zeros((len(matches), 2), dtype=np.float32)
   
    for i, match in enumerate(matches):
        points1[i, :] = keypoints2[match.queryIdx].pt
        points2[i, :] = keypoints1[match.trainIdx].pt
   
    # Adjust points to original image coordinates
    points1[:, 0] += width1 // 2
    points2[:, 0] += width2 // 2
   
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
