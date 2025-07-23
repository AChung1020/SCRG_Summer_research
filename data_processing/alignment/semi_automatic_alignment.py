import numpy as np
import cv2
import os
import json
import sys

# Add the parent directory to the system path to import custom modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from data_processing.misc_folder_functions.get_base_filepath import get_sharepoint_path

# Define base directories for thermal and visible images
THERMAL_BASE_DIR = os.path.join(get_sharepoint_path(), "HIP_Project", "ProcessedData", "Separated & Processed Images", "thermal_images")
VISIBLE_BASE_DIR = os.path.join(get_sharepoint_path(), "HIP_Project", "ProcessedData", "Separated & Processed Images", "optical_images")

OUTPUT_BASE_DIR = os.path.join(get_sharepoint_path(), "HIP_Project", "RESULTS_from_python_scripts", "aligned_images")
BLENDED_OUTPUT_BASE_DIR = os.path.join(get_sharepoint_path(), "HIP_Project", "RESULTS_from_python_scripts", "blended_images")
CROPPED_OPTICAL_BASE_DIR = os.path.join(get_sharepoint_path(), "HIP_Project", "RESULTS_from_python_scripts", "cropped_optical_images")
TRANSOFRM_INFO_BASE_DIR = os.path.join(get_sharepoint_path(), "HIP_Project", "RESULTS_from_python_scripts", "transform_info")

# Global variables to store points, current image, window name, and filename
thermal_points = []
optical_points = []
current_image = None
window_name = ""
current_filename = ""

def click_event(event, x, y, flags, param):
    """Handle mouse click events to mark points on images."""
    global thermal_points, optical_points, current_image, window_name
    if event == cv2.EVENT_LBUTTONDOWN:
        cv2.circle(current_image, (x, y), 3, (0, 255, 0), -1)
        cv2.imshow(window_name, current_image)
        if window_name.startswith("Thermal Image"):
            thermal_points.append((x, y))
        elif window_name.startswith("Optical Image"):
            optical_points.append((x, y))

def get_points(image, name):
    """Display image and collect user-clicked points."""
    global current_image, window_name
    current_image = image.copy()
    window_name = f"{name}: {current_filename}"
    cv2.imshow(window_name, current_image)
    cv2.setMouseCallback(window_name, click_event)
    while len(thermal_points) < 2 if name.startswith("Thermal Image") else len(optical_points) < 2:
        cv2.waitKey(1)
    cv2.destroyAllWindows()

def align_images(thermal_path, optical_path, output_path, blended_output_path, cropped_optical_path, transform_info_path, alpha=0.3):
    """Align thermal and optical images based on user-selected points."""
    global thermal_points, optical_points, current_filename

    while True:
        thermal_points.clear()
        optical_points.clear()

        # Load images
        thermal_img = cv2.imread(thermal_path)
        optical_img = cv2.imread(optical_path)

        # Get user input for alignment points
        current_filename = os.path.basename(thermal_path)
        print(f"Processing: {current_filename}")
        print("Please click 2 points on the thermal image")
        get_points(thermal_img, "Thermal Image")

        current_filename = os.path.basename(optical_path)
        print("Please click 2 corresponding points on the optical image")
        get_points(optical_img, "Optical Image")

        # Calculate transformation matrix
        thermal_pts = np.array(thermal_points)
        optical_pts = np.array(optical_points)

        scale_x = (thermal_pts[1][0] - thermal_pts[0][0]) / (optical_pts[1][0] - optical_pts[0][0])
        scale_y = (thermal_pts[1][1] - thermal_pts[0][1]) / (optical_pts[1][1] - optical_pts[0][1])

        tx = thermal_pts[0][0] - scale_x * optical_pts[0][0]
        ty = thermal_pts[0][1] - scale_y * optical_pts[0][1]

        #First two columns, scalin and rotation. rotation = 0. and the last column is translation
        M = np.array([ 
            [scale_x, 0, tx],
            [0, scale_y, ty]
        ])

        # Store transformation info
        transform_info = {
            "scale_x": float(scale_x),
            "scale_y": float(scale_y),
            "translation_x": float(tx),
            "translation_y": float(ty)
        }

        # Apply transformation and blend images
        aligned_optical = cv2.warpAffine(optical_img, M, (thermal_img.shape[1], thermal_img.shape[0]))
        blended_image = blend_images(thermal_img, aligned_optical, alpha)

        # Display result and wait for user confirmation
        cv2.imshow(f"Blended Result: {os.path.basename(output_path)}", blended_image)
        key = cv2.waitKey(0) & 0xFF

        if key == ord('y'):
            # Save results if user approves
            result = np.hstack((aligned_optical, thermal_img))
            cv2.imwrite(output_path, result)
            cv2.imwrite(blended_output_path, blended_image)
            cv2.imwrite(cropped_optical_path, aligned_optical)
            
            with open(transform_info_path, 'w') as f:
                json.dump(transform_info, f, indent=4)
            
            cv2.destroyAllWindows()
            print("Results saved successfully.")
            break
        elif key == ord('n'):
            cv2.destroyAllWindows()
            print("Alignment not satisfactory. Let's try again.")
        else:
            cv2.destroyAllWindows()
            print("Invalid input. Please try again.")

def blend_images(image1, image2, alpha):
    """Blend two images with enhanced contrast for the optical image."""
    enhanced_optical = cv2.addWeighted(image2, 1.2, np.zeros(image2.shape, image2.dtype), 0, 0)
    blended_image = cv2.addWeighted(image1, 1 - alpha, enhanced_optical, alpha, 0)
    return blended_image

def process_images(thermal_dir, visible_dir, output_dir, blended_output_dir, cropped_optical_dir, transform_info_dir):
    """Process all images in the given directories."""
    # Create output directories if they don't exist
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(blended_output_dir, exist_ok=True)
    os.makedirs(cropped_optical_dir, exist_ok=True)
    os.makedirs(transform_info_dir, exist_ok=True)

    for filename in os.listdir(thermal_dir):
        if filename.endswith("_thermal.jpg"):
            base_name = os.path.splitext(filename)[0].replace("_thermal", "")
            thermal_path = os.path.join(thermal_dir, filename)
            optical_filename = base_name + '_optical.jpg'
            optical_path = os.path.join(visible_dir, optical_filename)

            if not os.path.exists(optical_path):
                print(f"Error: Could not find matching optical image for {filename}")
                continue

            output_path = os.path.join(output_dir, f"{base_name}_aligned.jpg")
            blended_output_path = os.path.join(blended_output_dir, f"{base_name}_blended.jpg")
            cropped_optical_path = os.path.join(cropped_optical_dir, f"{base_name}_cropped_optical.jpg")
            transform_info_path = os.path.join(transform_info_dir, f"{base_name}_transform_info.json")

            # Skip if results already exist
            if os.path.exists(blended_output_path) and os.path.exists(cropped_optical_path) and os.path.exists(transform_info_path):
                print(f"Skipping {base_name} - results already exist")
                continue

            align_images(thermal_path, optical_path, output_path, blended_output_path, cropped_optical_path, transform_info_path)
            print(f"Processed: {base_name}")

# Main execution
thermal_base_dir = THERMAL_BASE_DIR
visible_base_dir = VISIBLE_BASE_DIR

# Define output directories
output_base_dir = OUTPUT_BASE_DIR
blended_output_base_dir = BLENDED_OUTPUT_BASE_DIR
cropped_optical_base_dir = CROPPED_OPTICAL_BASE_DIR
transform_info_base_dir = TRANSOFRM_INFO_BASE_DIR

# Process images in subdirectories
for subdir in os.listdir(thermal_base_dir):
    thermal_subdir = os.path.join(thermal_base_dir, subdir)
    optical_subdir = f"{subdir}"
    visible_subdir = os.path.join(visible_base_dir, optical_subdir)
    
    if os.path.isdir(thermal_subdir) and os.path.isdir(visible_subdir):
        output_subdir = os.path.join(output_base_dir, subdir)
        blended_output_subdir = os.path.join(blended_output_base_dir, subdir)
        cropped_optical_subdir = os.path.join(cropped_optical_base_dir, subdir)
        transform_info_subdir = os.path.join(transform_info_base_dir, subdir)
        process_images(thermal_subdir, visible_subdir, output_subdir, blended_output_subdir, cropped_optical_subdir, transform_info_subdir)
    else:
        print(f"Skipping {subdir} - directories not found")

# Clean up any remaining windows
cv2.destroyAllWindows()