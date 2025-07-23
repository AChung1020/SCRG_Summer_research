import os  # Import the os module to interact with the operating system
import flyr  # Import the flyr module to process FLIR thermal images
from PIL import Image  # Import the Image class from PIL (Pillow) to handle image processing

#Allows the function in mis_folder_functions to be imported
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from data_processing.misc_folder_functions.get_base_filepath import get_sharepoint_path

#Change as you need to
ORIGNAL_FLIR_IMAGE_DIR = os.path.join(get_sharepoint_path(), "HIP_Project", "SubjData", "Phase 1")
OPTICAL_FOLDER_DESTINATION = os.path.join(get_sharepoint_path(), "HIP_Project", "RESULTS_from_python_scripts", "optical_images")
THERMAL_FOLDER_DESTINATION =  os.path.join(get_sharepoint_path(), "HIP_Project", "RESULTS_from_python_scripts", "thermal_images")

def process_flir_images(source_folder, destination_folder_optical, destination_folder_thermal):
    """
    Processes FLIR images from the source folder, extracts optical and thermal images,
    and saves them in the specified destination folders.

    :param source_folder: Path to the folder containing the source images.
    :param destination_folder_optical: Path to the folder where optical images will be saved.
    :param destination_folder_thermal: Path to the folder where thermal images will be saved.
    """

    # Walk through the directory tree, starting from source_folder
    for root, dirs, files in os.walk(source_folder):
        # Process only if the current directory's name is "Renamed Images"
        if "Renamed Images" in root:
            # Extract the top-level subdirectory name (e.g., "HIP_01")
            top_level_dir = root.split(os.sep)[-2]
            
            # Create corresponding subdirectories in the optical and thermal destination folders
            optical_subdir = os.path.join(destination_folder_optical, top_level_dir)
            thermal_subdir = os.path.join(destination_folder_thermal, top_level_dir)
            os.makedirs(optical_subdir, exist_ok=True)  # Create directory if it doesn't exist
            os.makedirs(thermal_subdir, exist_ok=True)  # Create directory if it doesn't exist

            # Iterate over all files in the current directory
            for filename in files:
                # Process only JPEG files (case insensitive)
                if filename.lower().endswith((".jpg", ".jpeg")):
                    flir_path = os.path.join(root, filename)  # Full path to the FLIR image file
                    print(f"Processing: {flir_path}")

                    # Unpack the FLIR image to extract thermal data and the embedded optical image
                    thermogram = flyr.unpack(flir_path)

                    # Generate base filename without the extension for saving processed images
                    base_filename = os.path.splitext(filename)[0]
                    
                    # Define the full path for saving the optical image
                    optical_image_path = os.path.join(optical_subdir, f"{base_filename}_optical.jpg")
                    
                    # Define the full path for saving the thermal image
                    render_no_edge_emphasis_path = os.path.join(thermal_subdir, f"{base_filename}_thermal.png")

                    # Save the extracted optical image
                    thermogram.optical_pil.save(optical_image_path)
                    
                    # Render and save the thermal image without edge emphasis (can change colors here - palettes = ["turbo", "cividis", "inferno", "grayscale", "hot"])
                    thermogram.render_pil(edge_emphasis=0, palette = 'grayscale').save(render_no_edge_emphasis_path)

                    # Print confirmation of the saved images
                    print(f"Saved {filename} to {optical_subdir} and {thermal_subdir}")

# Call the function to process the FLIR images
process_flir_images(ORIGNAL_FLIR_IMAGE_DIR, OPTICAL_FOLDER_DESTINATION, THERMAL_FOLDER_DESTINATION)
