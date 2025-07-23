import os
import csv
import exiftool
from datetime import datetime

def extract_all_metadata(file_path):
    """
    Extract all metadata from a given file using ExifTool.

    Args:
    file_path (str): Path to the file from which to extract metadata.

    Returns:
    dict: A dictionary containing all metadata, or None if an error occurs.
    """
    try:
        with exiftool.ExifToolHelper() as et:
            metadata = et.get_metadata(file_path)[0]
        return metadata
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

def write_metadata_to_csv(input_file, output_csv_path):
    """
    Extract metadata from a file and write it to a CSV file.

    Args:
    input_file (str): Path to the input file from which to extract metadata.
    output_csv_path (str): Path to the output CSV file where metadata will be written.
    """
    # Extract metadata from the input file
    metadata = extract_all_metadata(input_file)
    
    if metadata:
        # Open the output CSV file and write the metadata
        with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            csvwriter = csv.writer(csvfile)
            # Write the header row
            csvwriter.writerow(['Tag', 'Value'])
            
            # Write each metadata tag and its value
            for tag, value in metadata.items():
                csvwriter.writerow([tag, value])
        
        print(f"Metadata has been written to {output_csv_path}")
    else:
        print("No metadata could be extracted.")

# Example usage
# Replace with your input file path
input_file = r"/Users/andrewchung/Desktop/PythonCode/Phase 1/HIP_01/Renamed Images/HIP_01_ProOne_1_Cool.jpg"
# Replace with your desired output path
output_csv_path = r"./metadata_onefile.csv"

# Call the function to extract metadata and write it to CSV
write_metadata_to_csv(input_file, output_csv_path)