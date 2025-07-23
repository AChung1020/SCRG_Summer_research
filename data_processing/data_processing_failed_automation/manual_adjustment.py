import numpy as np
import cv2
import os
import pandas as pd

def process_images(thermal_base_dir, visible_base_dir, csv_dir):
    # Get all subdirectories
    subdirs = [d for d in os.listdir(visible_base_dir) if d.startswith('optical_HIP_')]

    for subdir in subdirs:
        subdir_number = subdir.split('_')[-1]
        thermal_subdir = f'thermal_HIP_{subdir_number}'
        csv_file = os.path.join(csv_dir, f"processed_pixel_offsets_{subdir_number}.csv")

        if not os.path.exists(csv_file):
            print(f"CSV file not found for {subdir_number}. Skipping.")
            continue

        # Read CSV file
        df = pd.read_csv(csv_file)
        offsets = {row['Group']: row.to_dict() for _, row in df.iterrows()}

        thermal_subdir_path = os.path.join(thermal_base_dir, thermal_subdir)
        visible_subdir_path = os.path.join(visible_base_dir, subdir)

        for camera_type in ['ProOne', 'E8XT']:
            for parity in ['even', 'odd']:
                group = f"{camera_type}_{parity}"
                thermal_dir = os.path.join(thermal_subdir_path, f"{parity}_{camera_type}_thermal")
                visible_dir = os.path.join(visible_subdir_path, f"{parity}_{camera_type}_optical")

                if not os.path.exists(thermal_dir) or not os.path.exists(visible_dir):
                    print(f"Directories not found for {group} in {subdir_number}. Skipping.")
                    continue

                left_offset = offsets[group]['Left']
                right_offset = offsets[group]['Right']
                top_offset = offsets[group]['Top']
                bottom_offset = offsets[group]['Bottom']

                process_directory(thermal_dir, visible_dir, left_offset, right_offset, top_offset, bottom_offset, subdir_number, group)

def process_directory(thermal_dir, visible_dir, left_offset, right_offset, top_offset, bottom_offset, subdir_number, group):
    output_dir = f'./output_final/HIP_{subdir_number}/{group}/'
    results_dir = f'./results_final/HIP_{subdir_number}/{group}/'
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(results_dir, exist_ok=True)

    for filename in os.listdir(thermal_dir):
        if filename.endswith("_thermal.jpg"):
            base_name = os.path.splitext(filename)[0].replace("_thermal", "")
            visible_filename = base_name + '_optical.jpg'
            
            visible_path = os.path.join(visible_dir, visible_filename)
            thermal_path = os.path.join(thermal_dir, filename)

            if not os.path.exists(visible_path) or not os.path.exists(thermal_path):
                print(f"Image not found: {visible_filename} or {filename}. Skipping.")
                continue

            image = cv2.imread(visible_path)
            thermal_image = cv2.imread(thermal_path, cv2.IMREAD_COLOR)

            if image is None or thermal_image is None:
                print(f"Error reading images for {base_name}. Skipping.")
                continue

            height, width = image.shape[:2]

            startX = int(left_offset)
            startY = int(top_offset)
            endX = int(width - right_offset)
            endY = int(height - bottom_offset)

            cv2.rectangle(image, (startX, startY), (endX, endY), (0, 0, 255), 2)
            crop_img = image[startY:endY, startX:endX]
            crop_img_resized = cv2.resize(crop_img, (thermal_image.shape[1], thermal_image.shape[0]))

            cv2.imwrite(os.path.join(output_dir, visible_filename), crop_img_resized)

            final = np.concatenate((crop_img_resized, thermal_image), axis=1)
            cv2.imwrite(os.path.join(results_dir, visible_filename), final)

    print(f"Processing complete for HIP_{subdir_number}/{group}")

# Main execution
thermal_base_dir = r'C:\Users\andre\OneDrive\Desktop\SCRG\Thermal Images'
visible_base_dir = r'C:\Users\andre\OneDrive\Desktop\SCRG\Optical Images'
csv_dir = r'C:\path\to\csv\files\directory'

process_images(thermal_base_dir, visible_base_dir, csv_dir)