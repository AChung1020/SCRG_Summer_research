import cv2
import numpy as np
import os

#Allows the function in mis_folder_functions to be imported
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from data_processing.misc_folder_functions.get_base_filepath import get_sharepoint_path

#Change as you need to
THERMAL_BASE_DIR = os.path.join(get_sharepoint_path(), "HIP_Project", "ProcessedData", "Separated & Processed Images", "thermal_images")
OPTICAL_BASE_DIR = os.path.join(get_sharepoint_path(), "HIP_Project", "ProcessedData", "Separated & Processed Images", "cropped_optical_results")

OUTPUT_DIR = os.path.join(get_sharepoint_path(), "HIP_Project", "RESULTS_from_python_scripts", "ROI_masks") 

"""
Function to handle mouse events for drawing and fitting an ellipse on an image.

This function is designed to be used as a callback for OpenCV's mouse events. It allows the user to interactively draw points on an image and fit an ellipse to these points. The function performs the following tasks:

1. On left mouse button press (EVENT_LBUTTONDOWN):
   - Adds the clicked point to a list of points.
   - Draws a small red circle at the clicked point.
   - If there are multiple points, draws green lines connecting them.

2. On mouse movement while drawing (EVENT_MOUSEMOVE):
   - Draws a temporary green line from the last point to the current mouse position.

3. On right mouse button press (EVENT_RBUTTONDOWN):
   - If there are at least 5 points, fits an ellipse to the points using OpenCV's fitEllipse function.
   - Draws the fitted ellipse on the image in green.

The function updates the display after each action, allowing the user to see the progress of their drawing and the final fitted ellipse.

Parameters:
event (int): The type of mouse event (e.g., left button down, mouse move).
x (int): The x-coordinate of the mouse pointer.
y (int): The y-coordinate of the mouse pointer.
flags (int): Any relevant flags passed by OpenCV.
param: Any extra parameters (not used in this function).

Global variables used:
points (list): List to store the coordinates of clicked points.
drawing (bool): Flag to indicate whether drawing is in progress.
img_copy (numpy.ndarray): A copy of the original image for drawing.
ellipse (tuple): Stores the parameters of the fitted ellipse.
filename (str): The name of the current image file being processed.
"""
def draw_and_fit_ellipse(event, x, y, flags, param):
    global points, drawing, img_copy, ellipse, filename

    if event == cv2.EVENT_LBUTTONDOWN:
        # Add new point on left click
        points.append((x, y))
        drawing = True
        img_copy = img.copy()
        # Draw a red circle at the clicked point
        cv2.circle(img_copy, (x, y), 3, (0, 0, 255), -1)
        if len(points) > 1:
            # Draw green lines connecting the points
            cv2.polylines(img_copy, [np.array(points)], False, (0, 255, 0), 2)
        cv2.imshow(f"Optical Image - {filename}", img_copy)

    elif event == cv2.EVENT_MOUSEMOVE and drawing:
        # Draw temporary line while moving the mouse
        temp_img = img_copy.copy()
        if len(points) > 0:
            cv2.line(temp_img, points[-1], (x, y), (0, 255, 0), 2)
        cv2.imshow(f"Optical Image - {filename}", temp_img)

    elif event == cv2.EVENT_RBUTTONDOWN:
        # Fit and draw ellipse on right click if enough points are available
        if len(points) > 4:
            ellipse = cv2.fitEllipse(np.array(points))
            cv2.ellipse(img, ellipse, (0, 255, 0), 2)
            cv2.imshow(f"Optical Image - {filename}", img)
            drawing = False

"""
Function to process a pair of optical and thermal images.

This function handles the interactive process of selecting a region of interest (ROI) on an optical image
and applying it to a corresponding thermal image. It performs the following steps:

1. Loads the optical image and sets up the interactive ROI selection process.
2. Allows the user to draw points on the optical image to define an elliptical ROI.
3. Fits an ellipse to the user-drawn points.
4. Creates a binary mask based on the fitted ellipse.
5. Loads and resizes the corresponding thermal image to match the optical image dimensions.
6. Overlays the ROI mask on the thermal image.
7. Displays the result and waits for user confirmation.
8. If confirmed, saves the binary mask and the thermal image with the ROI overlay.
9. If not confirmed, allows the user to retry the ROI selection.

The function uses OpenCV for image processing and display operations.

Parameters:
optical_path (str): File path to the optical image.
thermal_path (str): File path to the corresponding thermal image.
output_dir (str): Directory where the output files (masks and overlays) will be saved.

Global variables used:
img (numpy.ndarray): The loaded optical image.
img_copy (numpy.ndarray): A copy of the optical image for drawing.
points (list): List to store the coordinates of user-clicked points.
drawing (bool): Flag to indicate whether drawing is in progress.
ellipse (tuple): Stores the parameters of the fitted ellipse.
filename (str): The name of the current image file being processed.

The function does not return any value but saves output files to the specified directory.
"""
def process_image_pair(optical_path, thermal_path, output_dir):
    global img, img_copy, points, drawing, ellipse, filename

    filename = os.path.basename(optical_path)

    while True:
        # Load the optical image and initialize variables
        img = cv2.imread(optical_path)
        img_copy = img.copy()
        points = []
        drawing = False
        ellipse = None

        # Set up the window and mouse callback for ROI selection
        cv2.namedWindow(f"Optical Image - {filename}")
        cv2.imshow(f"Optical Image - {filename}", img)
        cv2.setMouseCallback(f"Optical Image - {filename}", draw_and_fit_ellipse)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        # Create a binary mask from the fitted ellipse
        mask = np.zeros((img.shape[0], img.shape[1]), dtype=np.uint8)

        if ellipse is not None:
            cv2.ellipse(mask, ellipse, 255, -1)

        # Load and resize the thermal image
        thermal_img = cv2.imread(thermal_path)
        thermal_img = cv2.resize(thermal_img, (mask.shape[1], mask.shape[0]))

        # Create a colored mask overlay
        colored_mask = np.zeros_like(thermal_img)
        colored_mask[mask == 255] = [0, 255, 0]

        # Blend the thermal image with the mask overlay
        alpha = 0.5
        result = cv2.addWeighted(thermal_img, 1, colored_mask, alpha, 0)

        # Display the result and wait for user confirmation
        cv2.imshow(f"Thermal Image with Mask Overlay - {filename}", result)
        key = cv2.waitKey(0) & 0xFF
        cv2.destroyAllWindows()

        if key == ord('y'):
            # Save the binary mask
            mask_dir = os.path.join(output_dir, "binary_masks")
            os.makedirs(mask_dir, exist_ok=True)
            mask_path = os.path.join(mask_dir, f"{os.path.splitext(os.path.basename(optical_path))[0]}_mask.png")
            cv2.imwrite(mask_path, mask)

            print(f"Binary mask saved at: {mask_path}")

            # Save the thermal image with mask overlay
            overlay_dir = os.path.join(output_dir, "thermal_with_mask")
            os.makedirs(overlay_dir, exist_ok=True)
            overlay_path = os.path.join(overlay_dir, f"{os.path.splitext(os.path.basename(thermal_path))[0]}_with_mask.png")
            cv2.imwrite(overlay_path, result)

            print(f"Thermal image with mask overlay saved at: {overlay_path}")
            break
        elif key == ord('n'):
            # If the user is not satisfied, continue the loop to retry
            continue
        else:
            print("Invalid key pressed. Please press 'y' to accept or 'n' to retry.")

"""
Main function to process all image pairs in the specified directories.

This function walks through the directory structure containing optical and thermal images,
processes matching pairs, and saves the results. It performs the following tasks:

1. Defines the base directories for optical images, thermal images, and output.
2. Walks through the optical image directory structure.
3. For each subdirectory in the optical directory:
   - Finds the corresponding subdirectory in the thermal directory.
   - Processes each cropped optical image file:
     a. Finds the matching thermal image.
     b. Checks if the image pair has already been processed.
     c. If not processed, calls process_image_pair() to handle ROI selection and masking.
4. Skips any images that have already been processed or don't have a matching thermal image.

The function uses os.walk() to navigate the directory structure and os.path operations
to handle file paths and checks.

No parameters are required as the function uses global constants for directory paths.

Global constants used:
OPTICAL_BASE_DIR (str): Base directory for optical images.
THERMAL_BASE_DIR (str): Base directory for thermal images.

The function does not return any value but orchestrates the entire image processing workflow.
"""
def main():
    optical_dir = OPTICAL_BASE_DIR
    thermal_dir = THERMAL_BASE_DIR
    output_dir = OUTPUT_DIR

    # Walk through the directory structure
    for root, dirs, files in os.walk(optical_dir):
        for dir_name in dirs:
            optical_subdir = os.path.join(root, dir_name)
            thermal_subdir = os.path.join(thermal_dir, dir_name)
            
            # Skip if the corresponding thermal directory doesn't exist
            if not os.path.exists(thermal_subdir):
                continue

            # Process each optical image file
            for optical_file in os.listdir(optical_subdir):
                if optical_file.endswith("_cropped_optical.jpg"):
                    base_name = optical_file.replace("_cropped_optical.jpg", "")
                    thermal_file = f"{base_name}_thermal.jpg"
                    thermal_path = os.path.join(thermal_subdir, thermal_file)
                    
                    # Check if the corresponding thermal image exists
                    if os.path.exists(thermal_path):
                        # Check if this image pair has already been processed
                        mask_path = os.path.join(output_dir, dir_name, "binary_masks", f"{base_name}_cropped_optical_mask.png")
                        if os.path.exists(mask_path):
                            print(f"Skipped images (already processed): {optical_file}")
                            continue

                        print(f"Processing: {optical_file} and {thermal_file}")
                        optical_path = os.path.join(optical_subdir, optical_file)
                        process_image_pair(optical_path, thermal_path, os.path.join(output_dir, dir_name))
                    else:
                        print(f"Matching thermal image not found for: {optical_file}")

if __name__ == "__main__":
    main()