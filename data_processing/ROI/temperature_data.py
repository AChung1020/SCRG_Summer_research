import os  # For interacting with the file system
import numpy as np  # For numerical operations, especially on arrays
from PIL import Image  # For opening and processing image files
import pandas as pd  # For handling and analyzing data, especially in CSV files

#Allows the function in mis_folder_functions to be imported
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from data_processing.misc_folder_functions.get_base_filepath import get_sharepoint_path

REGIONOFINTEREST_ROOT_DIR = os.path.join(get_sharepoint_path(), "HIP_Project", "ProcessedData", "Separated & Processed Images", "ROI Images")
#directory of all temperature pixel value csvs
TEMPERATURE_ROOT_DIR = os.path.join(get_sharepoint_path(), "HIP_Project", "ProcessedData", "Separated & Processed Images", "temperature_csv")

# Define the output path for the results CSV
OUTPUT_CSV_PATH = os.path.join(get_sharepoint_path(), "HIP_Project", "RESULTS_from_python_scripts", "temperature_analysis_results.csv")

def get_white_pixel_coordinates(image_path):
    """
    Get the coordinates of white pixels in an image.

    Args:
        image_path (str): The path to the image file.

    Returns:
        np.ndarray: An array of coordinates where the white pixels are located.
    """
    # Open the image file and convert it to a numpy array
    with Image.open(image_path) as img:
        img_array = np.array(img)

    # Find the coordinates where the pixel value is 255 (white)
    white_pixels = np.column_stack(np.where(img_array == 255))

    return white_pixels

def get_temperatures_for_coordinates(coordinates, temp_df):
    """
    Extract temperature values from the CSV file at the given coordinates.

    Args:
        coordinates (np.ndarray): An array of coordinates (y, x) where temperatures should be extracted.
        temp_df (pd.DataFrame): The DataFrame containing temperature values.

    Returns:
        np.ndarray: An array of temperature values corresponding to the given coordinates.
    """
    temperatures = []

    # Loop through each coordinate and retrieve the corresponding temperature
    for y, x in coordinates:
        temp = temp_df.iloc[y, x]  # Use iloc to access the DataFrame by row and column index
        temperatures.append(temp)

    return np.array(temperatures)

def process_image_and_csv(image_path, csv_path):
    """
    Process an image and its corresponding temperature CSV to extract statistics.

    Args:
        image_path (str): The path to the binary mask image file.
        csv_path (str): The path to the temperature CSV file.

    Returns:
        dict: A dictionary containing various statistics about the temperatures in white pixel areas.
    """
    print(f"Processing image: {image_path}")
    print(f"Corresponding CSV: {csv_path}")

    # Get the coordinates of the white pixels in the image
    coordinates = get_white_pixel_coordinates(image_path)
    print(f"Number of white pixels found: {len(coordinates)}")

    # Load the temperature data from the CSV file into a DataFrame
    temp_df = pd.read_csv(csv_path, header=None)
    print(f"CSV shape: {temp_df.shape}")

    # Extract the temperature values at the white pixel coordinates
    temperatures = get_temperatures_for_coordinates(coordinates, temp_df)
    print(f"Number of temperatures extracted: {len(temperatures)}")

    if len(temperatures) == 0:
        print("Warning: No temperatures extracted. Skipping this file.")
        return None

    # Calculate statistics on the extracted temperatures
    min_temp = np.min(temperatures)
    max_temp = np.max(temperatures)
    std_dev = np.std(temperatures)
    median_temp = np.median(temperatures)

    # Modify the image name by removing "_cropped_optical_mask.png"
    modified_image_name = os.path.basename(image_path).replace("_cropped_optical_mask.png", "")

    # Return the results as a dictionary
    return {
        'Filename': modified_image_name,
        'white_pixels': len(coordinates),
        'min_temp': min_temp,
        'max_temp': max_temp,
        'std_dev': std_dev,
        'median_temp': median_temp
    }

def main(roi_root_dir, temp_root_dir):
    """
    Main function to process all images and corresponding temperature CSVs.

    Args:
        roi_root_dir (str): Root directory containing the ROI (Region of Interest) images.
        temp_root_dir (str): Root directory containing the temperature CSV files.

    Returns:
        tuple: A list of results and a list of files that were not processed.
    """
    results = []
    unprocessed_files = []

    # Iterate over each subdirectory in the ROI root directory
    for subdir in os.listdir(roi_root_dir):
        # Define paths to the binary mask images and corresponding temperature CSVs
        roi_subdir = os.path.join(roi_root_dir, subdir, 'binary_masks')
        temp_subdir = os.path.join(temp_root_dir, subdir)

        if not (os.path.isdir(roi_subdir) and os.path.isdir(temp_subdir)):
            continue

        # Process each image file in the binary mask directory
        for image_file in os.listdir(roi_subdir):
            if image_file.endswith('_optical_mask.png'):
                image_path = os.path.join(roi_subdir, image_file)

                # Generate the base name to find the corresponding CSV file
                base_name = image_file.replace('_cropped_optical_mask.png', '')

                csv_file = f"{base_name}.csv"
                csv_path = os.path.join(temp_subdir, csv_file)

                # Check if the corresponding CSV file exists
                if os.path.exists(csv_path):
                    try:
                        # Process the image and its CSV file
                        result = process_image_and_csv(image_path, csv_path)
                        if result is not None:
                            results.append(result)
                        else:
                            unprocessed_files.append(image_file)
                    except Exception as e:
                        # Handle any errors that occur during processing
                        print(f"Error processing {image_file}: {str(e)}")
                        unprocessed_files.append(image_file)
                else:
                    print(f"Warning: No matching CSV found for {image_file}")
                    unprocessed_files.append(image_file)

    return results, unprocessed_files

# Set your root directories here
roi_root_dir = REGIONOFINTEREST_ROOT_DIR
temp_root_dir = TEMPERATURE_ROOT_DIR

# Call the main function and retrieve the results
results, unprocessed_files = main(roi_root_dir, temp_root_dir)

# Optionally print the results (commented out for now)

# for result in results:
#     print(f"Image: {result['image']}")
#     print(f"Number of white pixels: {result['white_pixels']}")
#     print(f"Minimum temperature in white pixel areas: {result['min_temp']}")
#     print(f"Maximum temperature in white pixel areas: {result['max_temp']}")
#     print(f"Standard deviation of temperatures: {result['std_dev']}")
#     print(f"Median temperature: {result['median_temp']}")
#     print("---")
# If you want to save results to a CSV file:

if results:
    df = pd.DataFrame(results)
    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(OUTPUT_CSV_PATH), exist_ok=True)
    df.to_csv(OUTPUT_CSV_PATH, index=False)
    print(f"Results saved to {OUTPUT_CSV_PATH}")
else:
    print("No results to save to CSV.")

# Print the list of files that were not processed
print("\nFiles that were not processed:")
for file in unprocessed_files:
    print(file)

print(f"\nTotal number of unprocessed files: {len(unprocessed_files)}")