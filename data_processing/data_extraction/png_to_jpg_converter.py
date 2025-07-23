import os
from PIL import Image

#Allows the function in mis_folder_functions to be imported
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from data_processing.misc_folder_functions.get_base_filepath import get_sharepoint_path

#Change as you need to
THERMAL_IMAGE_DIR = os.path.join(get_sharepoint_path(), "HIP_Project", "ProcessedData", "Separated & Processed Images", "thermal_images")

def convert_png_to_jpg(root_directory):
    # Check if the root directory exists
    if not os.path.exists(root_directory):
        print(f"The directory {root_directory} does not exist.")
        return

    # Walk through all subdirectories
    for dirpath, dirnames, filenames in os.walk(root_directory):
        # Process each file in the current directory
        for filename in filenames:
            if filename.endswith(".png"):
                # Full path to the PNG file
                png_image_path = os.path.join(dirpath, filename)
                
                # Open the PNG file
                with Image.open(png_image_path) as img:
                    # Convert the image to RGB (JPG doesn't support transparency)
                    rgb_img = img.convert('RGB')
                    
                    # Create the JPG filename
                    jpg_filename = f"{os.path.splitext(filename)[0]}.jpg"
                    jpg_image_path = os.path.join(dirpath, jpg_filename)
                    
                    # Save the image as JPG in the same directory
                    rgb_img.save(jpg_image_path)
                    print(f"Converted {png_image_path} to {jpg_image_path}")
                    
                    # Delete the original PNG file
                    os.remove(png_image_path)
                    print(f"Deleted original PNG: {png_image_path}")

    print("Conversion complete.")

# Example usage:
convert_png_to_jpg(THERMAL_IMAGE_DIR) 
