import os  # Import the os module for interacting with the operating system
import flyr  # Import the flyr module for processing FLIR thermal images
import csv  # Import the csv module for reading and writing CSV files

#Allows the function in mis_folder_functions to be imported
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from data_processing.misc_folder_functions.get_base_filepath import get_sharepoint_path

#Change as you need to
ORIGINAL_FLIR_IMAGES_DIR = os.path.join(get_sharepoint_path(), "HIP_Project", "SubjData", "Phase 1")
TEMPERATURE_CSV_DIR = os.path.join(get_sharepoint_path(), "HIP_Project", "RESULTS_from_python_scripts", "temperature_csv")  

def extract_flir_temperatures(root_directory, output_directory):
    """
    Extract temperature data from FLIR images and save them as CSV files.

    Args:
        root_directory (str): The root directory containing subdirectories with FLIR images.
        output_directory (str): The directory where the CSV files will be saved.
    """
    # Walk through the directory tree starting from the root_directory
    for subdir, _, files in os.walk(root_directory):
        # Check if the current directory is named "Renamed Images"
        if os.path.basename(subdir) == "Renamed Images":
            # Iterate through all files in the current directory
            for filename in files:
                # Process only JPEG files (case-insensitive)
                if filename.lower().endswith(('.jpg', '.jpeg')):
                    flir_path = os.path.join(subdir, filename)  # Construct the full path to the FLIR image file
                    print(f"Processing: {flir_path}")

                    try:
                        # Unpack the FLIR image to extract thermal data
                        thermogram = flyr.unpack(flir_path)
                        celsius_temps = thermogram.celsius  # Extract temperature data in Celsius

                        # Create a relative path from the root directory to the current subdir
                        relative_path = os.path.relpath(os.path.dirname(subdir), root_directory)
                        # Create the corresponding subdirectory in the output directory
                        output_subdir = os.path.join(output_directory, relative_path)
                        os.makedirs(output_subdir, exist_ok=True)  # Create the directory if it doesn't exist

                        # Generate the base filename (without extension) and CSV filename
                        base_filename = os.path.splitext(filename)[0]
                        csv_filename = f"{base_filename}.csv"
                        csv_path = os.path.join(output_subdir, csv_filename)  # Construct the full path to the CSV file

                        # Open the CSV file for writing temperature data
                        with open(csv_path, mode='w', newline='') as file:
                            writer = csv.writer(file)  # Create a CSV writer object
                            writer.writerows(celsius_temps)  # Write the temperature data to the CSV file

                        print(f"Temperature data saved to: {csv_path}")

                    except Exception as e:
                        # Print an error message if an exception occurs during processing
                        print(f"Error processing {flir_path}: {str(e)}")

    print("Processing complete.")  # Indicate that the processing is complete

# Example usage
if __name__ == "__main__":

    extract_flir_temperatures(ORIGINAL_FLIR_IMAGES_DIR, TEMPERATURE_CSV_DIR)  # Call the function to extract temperature data
