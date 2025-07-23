# Import necessary libraries
import sys  # For system-specific parameters and functions
import os  # For interacting with the operating system, such as file and directory management
import flyr  # For processing FLIR thermal images and extracting their metadata
import csv  # For reading and writing CSV files
from datetime import datetime  # For working with dates and times
import exiftool  # For extracting EXIF metadata from image files

#Allows the function in mis_folder_functions to be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from data_processing.misc_folder_functions.get_base_filepath import get_sharepoint_path

#Change as you need to
BASE_DIRECTORY = os.path.join(get_sharepoint_path(), "HIP_Project", "SubjData", "Phase 1")
OUTPUT_CSV_PATH = os.path.join(get_sharepoint_path(), "HIP_Project", "RESULTS_from_python_scripts", "metadata_extraction_results.csv")

# Set code version (can be easily updated)
CODE_VERSION = "1"

# Dictionary containing information for different combinations of body position, lighting, and distance
combo_info = {
    "1": {"Body Position": "Knee Forward", "Lighting": "Room Light", "Distance": "35 cm"},
    "2": {"Body Position": "Knee Forward", "Lighting": "Room Light", "Distance": "50 cm"},
    "3": {"Body Position": "Knee Forward", "Lighting": "Ring Light", "Distance": "35 cm"},
    "4": {"Body Position": "Knee Forward", "Lighting": "Ring Light", "Distance": "50 cm"},
    "5": {"Body Position": "Knees Stacked", "Lighting": "Room Light", "Distance": "35 cm"},
    "6": {"Body Position": "Knees Stacked", "Lighting": "Room Light", "Distance": "50 cm"},
    "7": {"Body Position": "Knees Stacked", "Lighting": "Ring Light", "Distance": "35 cm"},
    "8": {"Body Position": "Knees Stacked", "Lighting": "Ring Light", "Distance": "50 cm"},
    "9": {"Body Position": "Knee Back", "Lighting": "Room Light", "Distance": "35 cm"},
    "10": {"Body Position": "Knee Back", "Lighting": "Room Light", "Distance": "50 cm"},
    "11": {"Body Position": "Knee Back", "Lighting": "Ring Light", "Distance": "35 cm"},
    "12": {"Body Position": "Knee Back", "Lighting": "Ring Light", "Distance": "50 cm"},
}

def extract_camera_metadata(file_path):
    """
    Extract metadata from a FLIR image file using flyr and exiftool.

    Args:
        file_path (str): Path to the image file.

    Returns:
        tuple: FLIR metadata and original date/time, or (None, None) if an error occurs.
    """
    try:
        # Extract FLIR-specific metadata using flyr
        thermogram = flyr.unpack(file_path)
        flir_metadata = thermogram.camera_metadata.data

        # Extract EXIF metadata using exiftool
        with exiftool.ExifToolHelper() as et:
            exif_metadata = et.get_metadata(file_path)[0]
            date_time_original = exif_metadata.get('APP1:DateTimeOriginal', '')
        return flir_metadata, date_time_original
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None, None

def parse_filename(filename):
    """
    Parse information from the filename.

    Args:
        filename (str): Name of the file.

    Returns:
        tuple: Extracted information (subject_id, camera, combo_number, minutes, base_or_cool).
    """
    parts = filename.split('_')  # Split the filename using underscores
    subject_id = '_'.join(parts[:2])  # Combine the first two parts for the subject ID
    camera = parts[2]  # Extract the camera identifier
    combo_number = parts[3]  # Extract the combo number

    # Extract the last part of the filename to determine additional information
    last_part = parts[-1].split('.')[0]
    minutes = ''  # Initialize minutes as an empty string
    base_or_cool = ''  # Initialize base_or_cool as an empty string

    # Determine the type of measurement (minutes, Cool/Base, or initial control)
    if 'min' in last_part:
        minutes = last_part.replace('min', '')  # Extract the number of minutes
    elif last_part in ['Cool', 'Base']:
        base_or_cool = last_part  # Determine if it's "Cool" or "Base"
    elif last_part in ['InitialCtrl', 'PreCup']:
        minutes = '0'  # Set minutes to 0 for initial control or pre-cup measurements
        base_or_cool = 'None'  # Set base_or_cool to 'None' for these cases

    return subject_id, camera, combo_number, minutes, base_or_cool

def write_metadata_to_csv(base_directory, output_csv_path):
    """
    Extract metadata from all FLIR images in the HIP directories and write to a CSV file.

    Args:
        base_directory (str): Base directory containing HIP folders.
        output_csv_path (str): Path to save the output CSV file.
    """
    # List of columns to exclude from the metadata when writing to CSV
    columns_to_drop = ['model','date_time','gps_info', 'make', 'resolution_unit', 'exif_offset', 'software', 'orientation', 'y_cb_cr_positioning', 'x_resolution', 'y_resolution']

    # Open the CSV file for writing
    with open(output_csv_path, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        header_written = False  # Flag to check if the header has been written

        # Iterate through HIP directories (01 to 35)
        for i in range(1, 36):
            hip_dir = f"HIP_{i:02d}"  # Format the directory name (e.g., "HIP_01", "HIP_02", etc.)
            directory_path = os.path.join(base_directory, hip_dir, "Renamed Images")

            if not os.path.exists(directory_path):  # Skip if the directory does not exist
                print(f"Directory not found: {directory_path}")
                continue

            # Get all FLIR image files in the directory
            flir_files = [os.path.join(directory_path, file) for file in os.listdir(directory_path) if file.lower().endswith('.jpg')]

            for file_path in flir_files:
                # Extract metadata from each FLIR image
                flir_metadata, date_time_original = extract_camera_metadata(file_path)

                if flir_metadata:
                    date, time = '', ''  # Initialize date and time as empty strings
                    if date_time_original:
                        try:
                            # Parse the date-time string to extract date and time
                            date_time = datetime.strptime(date_time_original.split('.')[0], '%Y:%m:%d %H:%M:%S')
                            # Extract timezone offset if available
                            tz_offset = date_time_original.split('.')[-1]
                            date = date_time.strftime('%Y-%m-%d')  # Format date as 'YYYY-MM-DD'
                            time = f"{date_time.strftime('%H:%M:%S')}{tz_offset}"  # Format time with timezone offset
                        except ValueError:
                            print(f"Unable to parse date_time_original: {date_time_original}")
                            date, time = '', ''  # Reset date and time if parsing fails

                    # Write header if not already written
                    if not header_written:
                        # Define the CSV header, including combo information and metadata fields
                        header = ['Filename', 'Subject ID', 'Camera', 'Combo Number', 'Body Position', 'Lighting', 'Distance', '# Minutes', 'Base or Cool', 'Code Version']
                        header += [key for key in flir_metadata.keys() if key not in columns_to_drop and key != 'image_description']
                        header += ['date', 'time']
                        csvwriter.writerow(header)  # Write the header row to the CSV file
                        header_written = True  # Set the flag to indicate the header has been written

                    # Parse the filename to extract information
                    file_name = os.path.basename(file_path)
                    file_name_without_extension = os.path.splitext(file_name)[0]  # Remove the .jpg extension
                    subject_id, camera, combo_number, minutes, base_or_cool = parse_filename(file_name)
                    combo_data = combo_info.get(combo_number, {"Body Position": "", "Lighting": "", "Distance": ""})

                    # Prepare row data to be written to the CSV file
                    row = [file_name_without_extension, subject_id, camera, combo_number, 
                           combo_data["Body Position"], combo_data["Lighting"], combo_data["Distance"],
                           minutes, base_or_cool, CODE_VERSION]
                    row += [flir_metadata[key] for key in flir_metadata.keys() if key not in columns_to_drop and key != 'image_description']
                    row += [date, time]

                    # Find the index of the 'model' column
                    model_index = header.index('model') if 'model' in header else -1

                    # Update the 'model' column if any parameter is empty
                    if '' in row and model_index != -1:
                        row[model_index] = 'FLIR ONE Pro (gen 3)'

                    # Write the row to the CSV file
                    csvwriter.writerow(row)

# Execute the main function to process the metadata and write to CSV
write_metadata_to_csv(BASE_DIRECTORY, OUTPUT_CSV_PATH)
print(f"Camera metadata for all HIP directories has been written to {OUTPUT_CSV_PATH}")