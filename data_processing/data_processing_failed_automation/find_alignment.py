import os
import cv2
import numpy as np

def blend_images(image1, image2, alpha):
    """
    Blend two images using alpha blending, with emphasized edges on image2.
    """
    image2_edges = cv2.Canny(image2, 50, 200) 
    image2_edges_bgr = cv2.cvtColor(image2_edges, cv2.COLOR_GRAY2BGR)
    blended_image2 = cv2.addWeighted(image2_edges_bgr, alpha, image2, 1 - alpha, 0)
    blended_image = cv2.addWeighted(image1, 1 - alpha, blended_image2, alpha, 0)
    return blended_image

def process_images(thermal_base_dir, visible_base_dir):
    # Get all subdirectories
    subdirs = [d for d in os.listdir(thermal_base_dir) if d.startswith('HIP_')]

    for subdir in subdirs:
        thermal_subdir_path = os.path.join(thermal_base_dir, subdir)
        visible_subdir_path = os.path.join(visible_base_dir, subdir)

        if not os.path.exists(visible_subdir_path):
            print(f"Visible directory not found for {subdir}. Skipping.")
            continue

        # Create a single output directory for each subject
        output_dir = f'./FINAL/Blended/{subdir}/'
        os.makedirs(output_dir, exist_ok=True)

        for camera_type in ['ProOne', 'E8XT']:
            for parity in ['even', 'odd']:
                thermal_dir = os.path.join(thermal_subdir_path, f"{camera_type}_{parity}")
                visible_dir = os.path.join(visible_subdir_path, f"{camera_type}_{parity}")

                if not os.path.exists(thermal_dir) or not os.path.exists(visible_dir):
                    print(f"Directories not found for {camera_type}_{parity} in {subdir}. Skipping.")
                    continue

                process_directory(thermal_dir, visible_dir, output_dir)

        print(f"Processing complete for {subdir}")

def process_directory(thermal_dir, visible_dir, output_dir):
    alpha = 0.1  # Define the alpha value (transparency level)

    for filename in os.listdir(thermal_dir):
        if filename.endswith("_thermal.jpg"):
            base_name = os.path.splitext(filename)[0].replace("_thermal", "")
            visible_filename = base_name + '_optical.jpg'
            
            thermal_path = os.path.join(thermal_dir, filename)
            visible_path = os.path.join(visible_dir, visible_filename)

            if not os.path.exists(visible_path):
                print(f"Image not found: {visible_filename}. Skipping.")
                continue

            thermal_image = cv2.imread(thermal_path)
            visible_image = cv2.imread(visible_path)

            if thermal_image is None or visible_image is None:
                print(f"Error reading images for {base_name}. Skipping.")
                continue

            # Resize visible image to match thermal image size
            visible_image_resized = cv2.resize(visible_image, (thermal_image.shape[1], thermal_image.shape[0]))

            blended_image = blend_images(thermal_image, visible_image_resized, alpha)

            output_path = os.path.join(output_dir, f"{base_name}_blended.jpg")
            cv2.imwrite(output_path, blended_image)

# Main execution
thermal_base_dir = r'C:\Users\andre\OneDrive\Desktop\SCRG\FINAL\Thermal Images'
visible_base_dir = r'C:\Users\andre\OneDrive\Desktop\SCRG\FINAL\output_final'

process_images(thermal_base_dir, visible_base_dir)
print("All processing complete.")