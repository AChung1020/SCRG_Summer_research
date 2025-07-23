import os
import shutil
import re

def copy_cupping_images(source_dir, dest_dir):
    """
    Copy and rename cupping images from a source directory to a destination directory.

    Args:
    source_dir (str): Path to the source directory containing the original images.
    dest_dir (str): Path to the destination directory where images will be copied.
    """
    # Create the destination directory if it doesn't exist
    os.makedirs(dest_dir, exist_ok=True)
    
    # Regex pattern to match filenames of interest
    # Matches HIP_XX_E8XT_6_SUFFIX_thermal.jpg, where SUFFIX can contain spaces
    pattern = re.compile(r'HIP_\d+_E8XT_6_([^_]+)_thermal\.jpg$')
    
    # Walk through the source directory
    for root, dirs, files in os.walk(source_directory):
        for file in files:
            # Print each file path for debugging
            print(os.path.join(root, file))
            
            # Check if the file matches our pattern
            match = pattern.match(file)
            if match and 'Base' not in file and 'Cool' not in file:
                # Extract the suffix, removing any leading/trailing spaces
                suffix = match.group(1).strip()
                
                # Create the new filename
                new_filename = f"HIP_{file.split('_')[1]}_E8XT_6_{suffix}.jpg"
                
                # Construct full paths for source and destination
                src_path = os.path.join(root, file)
                dst_path = os.path.join(dest_dir, new_filename)
                
                # Copy the file, preserving metadata
                shutil.copy2(src_path, dst_path)
                print(f"Copied and renamed: {src_path} -> {dst_path}")

# Define source and destination directories
source_directory = r"/Users/andrewchung/Library/CloudStorage/OneDrive-Emory/SCRG/HIP_Project/ProcessedData/Separated & Processed Images/thermal_images"
destination_directory = r"/Users/andrewchung/Library/CloudStorage/OneDrive-Emory/SCRG/RESULTS_from_python_scripts/only cupping images"

# Call the function to copy and rename the cupping images
copy_cupping_images(source_directory, destination_directory)