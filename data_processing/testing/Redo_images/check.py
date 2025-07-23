import os
from pathlib import Path

def get_modified_filenames(directory, suffix_to_remove):
    # Initialize a dictionary to store modified filenames
    modified_filenames = {}
    # Walk through the directory
    for root, dirs, files in os.walk(directory):
        for filename in files:
            # If the file ends with the specified suffix, remove it
            if filename.endswith(suffix_to_remove):
                modified_name = filename[:-len(suffix_to_remove)]
                modified_filenames[modified_name] = os.path.join(root, filename)
            else:
                # If no suffix to remove, keep the original filename
                modified_filenames[filename] = os.path.join(root, filename)
    return modified_filenames

def compare_and_delete_directories(dir1, dir2):
    # Get modified filenames for both directories
    dir1_files = get_modified_filenames(dir1, ".csv")
    dir2_files = get_modified_filenames(dir2, "_thermal.jpg")

    # Find unique files in each directory
    unique_dir1 = set(dir1_files.keys()) - set(dir2_files.keys())
    unique_dir2 = set(dir2_files.keys()) - set(dir1_files.keys())

    # Print and delete unique files in directory 1
    print("Unique files in directory 1 (to be deleted):")
    for file in unique_dir1:
        full_path = dir1_files[file]
        print(f"  {full_path}")
        os.remove(full_path)
        print(f"  Deleted: {full_path}")

    # Print unique files in directory 2
    print("\nUnique files in directory 2:")
    for file in unique_dir2:
        print(f"  {file}")

    # Print total number of deleted files
    print(f"\nTotal files deleted from directory 1: {len(unique_dir1)}")

# Define the paths to the directories
directory1 = "/Users/andrewchung/Library/CloudStorage/OneDrive-Emory/SCRG/HIP_Project/ProcessedData/Separated & Processed Images/temperature_csv"
directory2 = "/Users/andrewchung/Library/CloudStorage/OneDrive-Emory/SCRG/HIP_Project/ProcessedData/Separated & Processed Images/thermal_images"

# Ask for user confirmation before proceeding
confirm = input("This script will delete files in directory 1. Are you sure you want to proceed? (yes/no): ")
if confirm.lower() == 'yes':
    # If confirmed, run the comparison and deletion process
    compare_and_delete_directories(directory1, directory2)
else:
    # If not confirmed, cancel the operation
    print("Operation cancelled. No files were deleted.")