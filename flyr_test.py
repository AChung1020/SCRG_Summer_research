import flyr
import csv

# Define the path to the FLIR image
flir_path = r"C:\Users\andre\OneDrive\Desktop\SCRG\HIP_01\ProOne\20240326T145200.jpg"

import exiftool

with exiftool.ExifToolHelper() as et:
    metadata = et.get_metadata(flir_path)
    print(metadata)

# Unpack the thermogram data
thermogram = flyr.unpack(flir_path)

# Access camera metadata
cm = thermogram.camera_metadata
print(cm.data)  # Raw EXIF data (dict)
print(cm.gps_data)  # Raw GPS data (dict)
print(cm.date_time)  # Parsed datetime object of when picture was taken (datetime)
print(cm.gps_altitude)  # (float)
print(cm.gps_image_direction)  # (float)
print(cm.gps_latitude)  # (float)
print(cm.gps_longitude)  # (float)
print(cm.gps_map_datum)  # (str)
print(cm.make)  # (str)
print(cm.model)  # (str)
print(cm.software)  # (str)
print(cm.x_resolution)  # (float)
print(cm.y_resolution)  # (float)

print('\n----flir temp data---')
celsius_temps = thermogram.celsius

# Save the thermal data into a CSV file
csv_file_path = r"C:\Users\andre\OneDrive\Desktop\SCRG\csv_files\thermal_data.csv"

with open(csv_file_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    # Write the header with column labels
    header = [''] + [f'Column{j}' for j in range(1, celsius_temps.shape[1] + 1)]
    writer.writerow(header)
    # Write the temperature data with row numbers
    for i, row in enumerate(celsius_temps, start=1):
        writer.writerow([f'Row{i}'] + list(row))

print(f"Thermal data has been saved to {csv_file_path}")

# Save optical and rendered images
optical_image_path = r"C:\Users\andre\OneDrive\Desktop\SCRG\visible\thermal.jpg"
render_no_edge_emphasis_path = r"C:\Users\andre\OneDrive\Desktop\SCRG\thermal\thermal.png"
thermogram.optical_pil.save(optical_image_path)
thermogram.render_pil(edge_emphasis=0).save(render_no_edge_emphasis_path)


# create a script for saving images from specigic folder and extracting all the images from the directory
# check the thermal_data.csv to extracted thermal data and compare
#start writing documentation