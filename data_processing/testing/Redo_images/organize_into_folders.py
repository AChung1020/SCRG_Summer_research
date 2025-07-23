import os
import shutil
import re

def organize_hip_images(source_dir):
    # Regular expression to match HIP_XX pattern
    hip_pattern = re.compile(r'(HIP_\d+)')

    # Dictionary to keep track of how many files are moved to each subdirectory
    file_counts = {}

    # Iterate through all files in the source directory
    for filename in os.listdir(source_dir):
        if os.path.isfile(os.path.join(source_dir, filename)):
            # Try to find a match for HIP_XX pattern
            match = hip_pattern.search(filename)
            if match:
                hip_dir = match.group(1)
                
                # Create the subdirectory if it doesn't exist
                subdir_path = os.path.join(source_dir, hip_dir)
                if not os.path.exists(subdir_path):
                    os.makedirs(subdir_path)

                # Move the file to the appropriate subdirectory
                src_path = os.path.join(source_dir, filename)
                dst_path = os.path.join(subdir_path, filename)
                shutil.move(src_path, dst_path)

                # Update file count for this subdirectory
                file_counts[hip_dir] = file_counts.get(hip_dir, 0) + 1

                print(f"Moved {filename} to {hip_dir}")

    # Print summary
    print("\n--- SUMMARY ---")
    print(f"Total subdirectories created: {len(file_counts)}")
    print("Files moved to each subdirectory:")
    for hip_dir, count in sorted(file_counts.items()):
        print(f"  {hip_dir}: {count} files")

# Usage
source_dir = r'/Users/andrewchung/Library/CloudStorage/OneDrive-Emory/SCRG/RESULTS_from_python_scripts/Redo_Img_optical'

organize_hip_images(source_dir)