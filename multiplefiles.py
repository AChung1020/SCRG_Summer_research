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
    
    # Apply Bilateral Filter with adjusted parameters
    gray = cv2.bilateralFilter(gray, d=7, sigmaColor=50, sigmaSpace=50)
    
    # Apply Gaussian blur for noise reduction (alternative to guided filter)
    blurred_initial = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Apply Adaptive Histogram Equalization (AHE)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(blurred_initial)
    
    # Enhance contrast
    enhanced = cv2.normalize(enhanced, None, 0, 255, cv2.NORM_MINMAX)
    
    # Apply Canny edge detection
    edges = cv2.Canny(enhanced, 50, 150)
    
    # Apply morphological operations to connect broken edges
    kernel = np.ones((3,3), np.uint8)
    connected_edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
    
    # Apply hysteresis thresholding
    low_threshold = 50
    high_threshold = 100
    strong_edges = connected_edges > high_threshold
    weak_edges = (connected_edges <= high_threshold) & (connected_edges > low_threshold)
    
    # Use strong edges as seeds and dilate to connect to weak edges
    edges = np.zeros_like(strong_edges, dtype=np.uint8)
    edges[strong_edges] = 255
    edges[cv2.dilate(strong_edges.astype(np.uint8), kernel, iterations=1) & weak_edges] = 255
    
    # Invert the edges (black becomes white, white becomes black)
    # inverted_edges = cv2.bitwise_not(edges)
    
    # Overlay inverted edges on original image
    overlay = cv2.addWeighted(image, 0.7, cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR), 0.3, 0)
    
    # cv2.imshow("Inverted Edges", edges)
    # cv2.imshow("Inverted Edge Overlay", overlay)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    
    return edges


ap = argparse.ArgumentParser()

ap.add_argument("-v", "--visualize", action='store_true', help="Flag indicating whether or not to visualize each iteration")
args = vars(ap.parse_args())

thermal_dir = r'C:\Users\andre\OneDrive\Desktop\SCRG\thermal'
visible_dir = r'C:\Users\andre\OneDrive\Desktop\SCRG\visible'

# Loop through all files in the thermal directory
for filename in os.listdir(thermal_dir):
    if filename.endswith("_thermal.jpg"):
        # Get the base name of the file without the "_thermal.jpg" extension
        base_name = os.path.splitext(filename)[0].replace("_thermal", "")
        print(base_name)

        # Load the template image (thermal image)
        template = cv2.imread(os.path.join(thermal_dir, filename))
        template = preprocess_thermal_image(template)

        # Perform edge detection on the entire template
        edges_template = template

        # Create a mask for the right half of the template
        (tH, tW) = edges_template.shape[:2]
        # mask = np.zeros((tH, tW), dtype=np.uint8)
        # mask[:, tW//2:] = 255

        # Apply the mask to the edge-detected template
        # masked_template = cv2.bitwise_and(edges_template, edges_template, mask=mask)

        # Load the visible image
        visible_filename = base_name + '_optical.jpg'
        image = cv2.imread('visible/' + visible_filename)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.fastNlMeansDenoising(gray, None, h=20, searchWindowSize=35, templateWindowSize=11)
        # cv2.imshow("Visible Image", gray)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        found = None

        # Loop over the scales of the image
        for scale in np.linspace(0.45, 1.0, 200)[::-1]:
            resized = imutils.resize(gray, width=int(gray.shape[1] * scale))
            r = gray.shape[1] / float(resized.shape[1])

            if resized.shape[0] < tH or resized.shape[1] < tW:
                break

            edged = cv2.Canny(resized, 50, 200)
            if args.get("visualize", False):
                cv2.imshow("Visualize", edged)
                cv2.waitKey(0)
            result = cv2.matchTemplate(edged, edges_template, cv2.TM_CCOEFF)
            (_, maxVal, _, maxLoc) = cv2.minMaxLoc(result)

            if args.get("visualize", False):
                clone = np.dstack([edged, edged, edged])
                cv2.rectangle(clone, (maxLoc[0], maxLoc[1]), (maxLoc[0] + tW, maxLoc[1] + tH), (0, 0, 255), 2)
                # cv2.imshow("Visualize", clone)
                # cv2.waitKey(0)

            if found is None or maxVal > found[0]:
                found = (maxVal, maxLoc, r)

        (_, maxLoc, r) = found
        (startX, startY) = (int(maxLoc[0] * r), int(maxLoc[1] * r))
        (endX, endY) = (int((maxLoc[0] + tW) * r), int((maxLoc[1] + tH) * r))

        cv2.rectangle(image, (startX, startY), (endX, endY), (0, 0, 255), 2)
        crop_img = image[startY:endY, startX:endX]

        # cv2.imshow("Detected Image", image)
        # cv2.imshow("Cropped Image", crop_img)
        # cv2.waitKey(0)
        cv2.destroyAllWindows()

        # Load the thermal image again (for alignment)
        thermal_image = cv2.imread(os.path.join(thermal_dir, filename), cv2.IMREAD_COLOR)

        # Resize the cropped visible image to the thermal image dimensions
        crop_img_resized = cv2.resize(crop_img, (thermal_image.shape[1], thermal_image.shape[0]))

        # Save the resized visible image
        output_dir = './output/'
        os.makedirs(output_dir, exist_ok=True)
        cv2.imwrite(os.path.join(output_dir, visible_filename), crop_img_resized)

        # Concatenate and save the result
        results_dir = './results/'
        os.makedirs(results_dir, exist_ok=True)
        final = np.concatenate((crop_img_resized, thermal_image), axis=1)
        cv2.imwrite(os.path.join(results_dir, visible_filename), final)

        cv2.waitKey(0)