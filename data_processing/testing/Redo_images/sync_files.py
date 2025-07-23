import os
import shutil

def sync_directories(redo_path, original_path):
    # Walk through the redo_path directory
    for root, dirs, files in os.walk(redo_path):
        for file in files:
            # Skip .DS_Store files
            if file == '.DS_Store':
                continue

            # Get the full path of the file in redo_path
            redo_file_path = os.path.join(root, file)
            
            try:
                # Extract the relative path from redo_path
                rel_path = os.path.relpath(root, redo_path)
                
                # Construct the path for the file in the original directory
                original_file_path = os.path.join(original_path, rel_path, file)
                
                # If the directory doesn't exist in the original path, create it
                os.makedirs(os.path.dirname(original_file_path), exist_ok=True)
                
                # If the file exists in the original path, replace it
                if os.path.exists(original_file_path):
                    os.remove(original_file_path)
                
                # Copy the file from redo_path to original_path
                shutil.copy2(redo_file_path, original_file_path)
                print(f"Processed: {original_file_path}")
            except Exception as e:
                print(f"Error processing {redo_file_path}: {str(e)}")

# Example usage
redo_path = "/Users/andrewchung/Library/CloudStorage/OneDrive-Emory/SCRG/RESULTS_from_python_scripts/ROI Images"
original_path = "/Users/andrewchung/Library/CloudStorage/OneDrive-Emory/SCRG/HIP_Project/ProcessedData/Separated & Processed Images/ROI Images"
sync_directories(redo_path, original_path)