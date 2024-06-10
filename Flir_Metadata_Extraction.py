import os
import flyr
import csv
from datetime import datetime
import exiftool

directory_path = r"C:\Users\andre\OneDrive\Desktop\SCRG_Research\HIP_01\Renamed Images"
output_csv_path = r"camera_metadata.csv"

def extract_camera_metadata(file_path):
    try:
        thermogram = flyr.unpack(file_path)
        flir_metadata = thermogram.camera_metadata.data

        with exiftool.ExifToolHelper() as et:
            exif_metadata = et.get_metadata(file_path)[0] 
            date_time_original = exif_metadata.get('EXIF:DateTimeOriginal', '')
        return flir_metadata, date_time_original
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None, None
    
def write_metadata_to_csv(directory_path, output_csv_path):
    flir_files = [os.path.join(directory_path, file) for file in os.listdir(directory_path) if file.lower().endswith('.jpg')]

    with open(output_csv_path, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)

        header_written = False
        for file_path in flir_files:
            flir_metadata, date_time_original = extract_camera_metadata(file_path)
            if flir_metadata:
                date, time = '', ''
                if date_time_original:
                    date_time = datetime.strptime(date_time_original, '%Y:%m:%d %H:%M:%S')
                    date = date_time.strftime('%Y-%m-%d')
                    time = date_time.strftime('%H:%M:%S')
                
                if not header_written:
                    header = ['file_name'] + [key for key in flir_metadata.keys() if key != 'image_description']
                    header += ['date', 'time']  
                    csvwriter.writerow(header)
                    header_written = True

                file_name = os.path.basename(file_path) 
                row = [file_name] + [flir_metadata[key] for key in flir_metadata.keys() if key != 'image_description']
                row += [date, time] 
                
                for i in range(0, len(row)):
                    if row[i] == '':
                        row[i] == 'FLIR ONE Pro (gen 3)'

                csvwriter.writerow(row)

write_metadata_to_csv(directory_path, output_csv_path)
print(f"Camera metadata has been written to {output_csv_path}")
