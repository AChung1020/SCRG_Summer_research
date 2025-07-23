# Import necessary libraries
import numpy as np
from PIL import Image
import pandas as pd

def get_white_pixel_coordinates(image_path):
    """
    Get coordinates of white pixels in an image.
    
    Args:
    image_path (str): Path to the image file.
    
    Returns:
    numpy.ndarray: Array of (y, x) coordinates of white pixels.
    """
    with Image.open(image_path) as img:
        img_array = np.array(img)
    # Find coordinates where pixel value is 255 (white)
    white_pixels = np.column_stack(np.where(img_array == 255))
    return white_pixels

def get_temperatures_for_coordinates(coordinates, temp_df):
    """
    Get temperatures for given coordinates from a temperature dataframe.
    
    Args:
    coordinates (numpy.ndarray): Array of (y, x) coordinates.
    temp_df (pandas.DataFrame): Dataframe containing temperature data.
    
    Returns:
    numpy.ndarray: Array of temperatures corresponding to the given coordinates.
    """
    temperatures = []
    for y, x in coordinates:
        temp = temp_df.iloc[y, x]
        temperatures.append(temp)
    return np.array(temperatures)

# Define file paths
image_path = r"HIP_01_E8XT_1_Base_cropped_optical_mask.png"
csv_path = r"/Users/andrewchung/Desktop/PythonCode/temp_csv/HIP_01/HIP_01_E8XT_1_Base.csv"

# Get white pixel coordinates from the image
coordinates = get_white_pixel_coordinates(image_path)

# Read temperature data from CSV file
temp_df = pd.read_csv(csv_path, header=None)

# Get temperatures for white pixel coordinates
temperatures = get_temperatures_for_coordinates(coordinates, temp_df)

# Calculate statistics
min_temp = np.min(temperatures)
max_temp = np.max(temperatures)
std_dev = np.std(temperatures)
median_temp = np.median(temperatures)

# Print results
print(f"Image: {image_path}")
print(f"Number of white pixels: {len(coordinates)}")
print(f"Minimum temperature in white pixel areas: {min_temp}")
print(f"Maximum temperature in white pixel areas: {max_temp}")
print(f"Standard deviation of temperatures: {std_dev}")
print(f"Median temperature: {median_temp}")

# If you want to see all coordinates and their temperatures:
# for (y, x), temp in zip(coordinates, temperatures):
#     print(f"Coordinate ({x}, {y}): Temperature {temp}")