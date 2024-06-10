import os
import flyr
import csv
import exiftool
from PIL import Image

def process_flir_images(source_folder, destination_folder_optical, destination_folder_thermal, csv_folder):
    # Create destination directories if they do not exist
    os.makedirs(destination_folder_optical, exist_ok=True)
    os.makedirs(destination_folder_thermal, exist_ok=True)
    os.makedirs(csv_folder, exist_ok=True)

    for filename in os.listdir(source_folder):
        if filename.lower().endswith((".jpg", ".jpeg")):
            flir_path = os.path.join(source_folder, filename)
            print(flir_path)
            # Unpack the thermogram data
            thermogram = flyr.unpack(flir_path)

            celsius_temps = thermogram.celsius

            # Prepare file names for saving
            base_filename = os.path.splitext(filename)[0]
            csv_file_path = os.path.join(csv_folder, f"{base_filename}.csv")
            optical_image_path = os.path.join(destination_folder_optical, f"{base_filename}_optical.jpg")
            render_no_edge_emphasis_path = os.path.join(destination_folder_thermal, f"{base_filename}_thermal.png")

            # Save the thermal data into a CSV file
            with open(csv_file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                # Write the header with column labels
                header = ['Row_num'] + [f'Col {j}' for j in range(1, celsius_temps.shape[1] + 1)]
                writer.writerow(header)
                # Write the temperature data with row numbers
                for i, row in enumerate(celsius_temps, start=1):
                    writer.writerow([f'Row{i}'] + list(row))

            print(f"Thermal data has been saved to {csv_file_path}")

            # Save optical and rendered images
            thermogram.optical_pil.save(optical_image_path)
            thermogram.render_pil(edge_emphasis=0).save(render_no_edge_emphasis_path)

            print(f"Saved {filename} to {destination_folder_optical} and {destination_folder_thermal}")

# This is the only part you need to edit when you want to do this with different file types
source_folder = r"C:\Users\andre\OneDrive\Desktop\SCRG\Patients\HIP_20\Pro One"
destination_folder_optical = r"C:\Users\andre\OneDrive\Desktop\SCRG\Patient_Data\optical_OnePro_Subject20"
destination_folder_thermal = r"C:\Users\andre\OneDrive\Desktop\SCRG\Patient_Data\thermal_OnePro_Subject20"
csv_folder = r"C:\Users\andre\OneDrive\Desktop\SCRG\Patient_Data\csv_files_OnePro_Subject20"

# Run the function
process_flir_images(source_folder, destination_folder_optical, destination_folder_thermal, csv_folder)
