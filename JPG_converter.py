import os
from PIL import Image

def convert_png_to_jpg(directory_path):
    # Check if the directory exists
    if not os.path.exists(directory_path):
        print(f"The directory {directory_path} does not exist.")
        return

    # Create an output directory for the JPG files
    output_directory = os.path.join(directory_path, 'converted_JPG')
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Loop through all files in the directory
    for filename in os.listdir(directory_path):
        if filename.endswith(".png"):
            # Open the PNG file
            png_image_path = os.path.join(directory_path, filename)
            with Image.open(png_image_path) as img:
                # Convert the image to RGB (JPG doesn't support transparency)
                rgb_img = img.convert('RGB')
                # Save the image as JPG in the output directory
                jpg_image_path = os.path.join(output_directory, f"{os.path.splitext(filename)[0]}.jpg")
                rgb_img.save(jpg_image_path)
                print(f"Converted {filename} to {jpg_image_path}")

    print("Conversion complete.")

# Example usage:
convert_png_to_jpg(r"C:\Users\andre\OneDrive\Desktop\SCRG\thermal")
