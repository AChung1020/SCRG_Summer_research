import csv
import os
import shutil
from collections import Counter

def copy_matching_images(csv_file, source_dir, destination_dir):
    # Read the CSV file
    with open(csv_file, 'r') as f:
        csv_reader = csv.reader(f)
        next(csv_reader)  # Skip header row
        filenames = [row[0] for row in csv_reader]

    unique_csv_entries = set(filenames)
    
    # Count duplicates in CSV
    duplicates = [item for item, count in Counter(filenames).items() if count > 1]

    # Create the destination directory if it doesn't exist
    os.makedirs(destination_dir, exist_ok=True)

    # Dictionary to keep track of found files and their sources
    found_files = {}

    # Walk through the source directory and its subdirectories
    for root, _, files in os.walk(source_dir):
        for file in files:
            # Remove the "_optical" suffix and file extension for comparison
            name_without_suffix = file.rsplit('_thermal', 1)[0].rsplit('.', 1)[0]
            
            if name_without_suffix in unique_csv_entries:
                source_path = os.path.join(root, file)
                destination_path = os.path.join(destination_dir, file)
                shutil.copy2(source_path, destination_path)
                
                if name_without_suffix in found_files:
                    print(f"Warning: Duplicate file found for {name_without_suffix}")
                    print(f"  Previous: {found_files[name_without_suffix]}")
                    print(f"  Current:  {source_path}")
                found_files[name_without_suffix] = source_path

    # Find missing files
    missing_files = unique_csv_entries - set(found_files.keys())
    
    # Count files in destination directory
    copied_files = [f for f in os.listdir(destination_dir) if os.path.isfile(os.path.join(destination_dir, f))]

    # Print summary
    print("\n--- SUMMARY ---")
    print(f"Total entries in CSV: {len(filenames)}")
    print(f"Unique entries in CSV: {len(unique_csv_entries)}")
    print(f"Duplicate entries in CSV: {len(duplicates)}")
    print(f"Files found and copied: {len(found_files)}")
    print(f"Files in CSV not found in source: {len(missing_files)}")
    print(f"Actual files in destination directory: {len(copied_files)}")

    if duplicates:
        print("\nDuplicate entries in CSV:")
        for dup in duplicates:
            print(f"  - {dup} (occurs {filenames.count(dup)} times)")

    if missing_files:
        print("\nFiles from CSV not found in source directory:")
        for file in sorted(missing_files):
            print(f"  - {file}")

# Usage
csv_file = r'/Users/andrewchung/Desktop/PythonCode/Files_Redo.csv'
source_dir = r'/Users/andrewchung/Library/CloudStorage/OneDrive-Emory/SCRG/HIP_Project/ProcessedData/Separated & Processed Images/thermal_images'
destination_dir = r'/Users/andrewchung/Library/CloudStorage/OneDrive-Emory/SCRG/RESULTS_from_python_scripts/Redo_Img_thermal'

copy_matching_images(csv_file, source_dir, destination_dir)