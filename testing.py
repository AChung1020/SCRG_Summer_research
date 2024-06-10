import subprocess
from PIL import Image, ImageFilter, ImageChops

def load_image(filepath):
    return Image.open(filepath)

def get_exif_tags(filepath):
    result = subprocess.run(['exiftool', filepath], capture_output=True, text=True)
    tags = {}
    for line in result.stdout.splitlines():
        tag, value = line.split(':', 1)
        tags[tag.strip()] = value.strip()
    return tags

def get_offsets(tags):
    print("Printing all EXIF tags to find Offset X and Offset Y:")
    for key, value in tags.items():
        print(f"{key}: {value}")
    
    x_offset = int(tags.get('Offset X', 0)) 
    y_offset = int(tags.get('Offset Y', 0))  
    return x_offset, y_offset

def resize_image(image, target_size):
    return image.resize(target_size, Image.ANTIALIAS)

def apply_offset(image, x_offset, y_offset, target_size):
    target_width, target_height = target_size
    result_image = Image.new('RGBA', (target_width, target_height))
    result_image.paste(image, (x_offset, y_offset))
    return result_image

def extract_edges(image):
    gray_image = image.convert('L')
    edges = gray_image.filter(ImageFilter.FIND_EDGES)
    inverted_edges = ImageChops.invert(edges)
    return inverted_edges.convert('RGBA')

def blend_edges_with_thermal(optical_edges, thermal_image, alpha=0.8):
    # Resize the optical edges to match the size of the thermal image
    optical_edges_resized = optical_edges.resize(thermal_image.size)
    
    # Convert to RGBA if not already in that mode
    if optical_edges_resized.mode != 'RGBA':
        optical_edges_resized = optical_edges_resized.convert('RGBA')
    if thermal_image.mode != 'RGBA':
        thermal_image = thermal_image.convert('RGBA')
    
    # Blend the images
    blended_image = Image.blend(thermal_image, optical_edges_resized, alpha)
    return blended_image


# File paths
flir_filepath = r'C:\Users\andre\OneDrive\Desktop\SCRG_Research\HIP_01\ProOne\20240326T144930.jpg'  # Composite FLIR image file path
output_filepath = r'C:\Users\andre\OneDrive\Desktop\SCRG_Research\test_images\blended_image.png'  # Path where the blended image will be saved

# Load the composite FLIR image
flir_image = load_image(flir_filepath)

# Extract EXIF tags from the FLIR image
tags = get_exif_tags(flir_filepath)

print("EXIF tags extracted from the FLIR image:")
for key, value in tags.items():
    print(f"{key}: {value}")

# Get offsets from the EXIF tags
x_offset, y_offset = get_offsets(tags)

# Get the dimensions of the FLIR image
flir_width, flir_height = flir_image.size

# Split the FLIR image into optical and thermal parts
thermal_width = flir_width // 2
thermal_image = flir_image.crop((0, 0, thermal_width, flir_height))
optical_image = flir_image.crop((thermal_width, 0, flir_width, flir_height))

# Resize the optical image to match the size of the thermal image
optical_image_resized = resize_image(optical_image, thermal_image.size)

# Apply offsets to align the images correctly
adjusted_optical_image = apply_offset(optical_image_resized, 0, y_offset, flir_image.size)

# Extract edges from the adjusted optical image
optical_edges = extract_edges(adjusted_optical_image)

# Blend edges with the thermal image
blended_image = blend_edges_with_thermal(optical_edges, thermal_image, alpha=0.2)

# Save the blended image to the specified path
blended_image.save(output_filepath)
print(f"Blended image saved to {output_filepath}")
