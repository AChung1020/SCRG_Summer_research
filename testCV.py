import os
import flyr
import csv
import exiftool
from datetime import datetime

# Define the path to the directory containing FLIR images
directory_path = r"C:\Users\andre\OneDrive\Desktop\SCRG_Research\HIP_01\Renamed Images"

# Define the path to the output CSV file
output_csv_path = r"camera_metadata.csv"

# Function to extract camera metadata from a FLIR image and return it as a dictionary
def extract_camera_metadata(file_path):
    try:
        thermogram = flyr.unpack(file_path)
        cm = thermogram.camera_metadata
        metadata = dict(cm.data)  # Convert the metadata list to a dictionary
        
        with exiftool.ExifToolHelper() as et:
            exif_metadata = et.get_metadata(file_path)
            date_time_original = None
            for item in exif_metadata:
                if item['TagName'] == 'EXIF:DateTimeOriginal':
                    date_time_original = item['Value']
                    break
            if date_time_original:
                date_time = datetime.strptime(date_time_original, '%Y:%m:%d %H:%M:%S')
                metadata['date'] = date_time.strftime('%Y:%m:%d')
                metadata['time'] = date_time.strftime('%H:%M:%S')
            else:
                metadata['date'] = ''
                metadata['time'] = ''
        
        return metadata
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

# Function to write dictionary content to a CSV file
def write_metadata_to_csv(directory_path, output_csv_path):
    # Collect all FLIR image files in the directory
    flir_files = [os.path.join(directory_path, file) for file in os.listdir(directory_path) if file.lower().endswith('.jpg')]

    # Open the CSV file for writing
    with open(output_csv_path, 'w', newline='') as csvfile:
        # Create a CSV writer object
        csvwriter = csv.writer(csvfile)

        # Write the header (first row) of the CSV file
        header_written = False
        for file_path in flir_files:
            metadata = extract_camera_metadata(file_path)
            if metadata:
                if not header_written:
                    # Write the header based on the keys of the dictionary
                    header = ['file_name', 'date', 'time'] + [key for key in metadata.keys() if key not in ['date', 'time', 'image_description']]
                    csvwriter.writerow(header)
                    header_written = True

                # Write the metadata values for each file
                file_name = os.path.basename(file_path)  # Get the base name (file name without the directory path)
                row = [file_name, metadata['date'], metadata['time']] + [metadata[key] for key in metadata.keys() if key not in ['date', 'time', 'image_description']]
                for i in range(0, len(row)):
                    if row[i] == '':
                        row[i] = 'Flir One Pro'
                csvwriter.writerow(row)

# Call the function to write metadata to the CSV file
write_metadata_to_csv(directory_path, output_csv_path)
print(f"Camera metadata has been written to {output_csv_path}")