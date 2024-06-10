import subprocess
from PIL import Image, ImageFilter, ImageChops

def load_image(filepath):
    # Load an image
    image = Image.open(filepath)
    return image

def get_exif_tags(filepath):
    result = subprocess.run(['exiftool', filepath], capture_output=True, text=True)
    tags = {}
    for line in result.stdout.splitlines():
        tag, value = line.split(':', 1)
        tags[tag.strip()] = value.strip()
    return tags

def get_offsets(tags):
    print("Printing all EXIF tags to find OffsetX and OffsetY:")
    for key, value in tags.items():
        print(f"{key}: {value}")
    
    x_offset = int(tags.get('Offset X', 0)) 
    y_offset = int(tags.get('Offset Y', 0))  
    return x_offset, y_offset

def apply_offset(image, x_offset, y_offset):
    # No offset adjustment, return the original image
    return image

def extract_edges(image):
    gray_image = image.convert('L')
    edges = gray_image.filter(ImageFilter.FIND_EDGES)
    inverted_edges = ImageChops.invert(edges)
    return inverted_edges.convert('RGBA')

def blend_edges_with_thermal(optical_edges, thermal_image, alpha=0.8):
    if optical_edges.mode != 'RGBA':
        optical_edges = optical_edges.convert('RGBA')
    if thermal_image.mode != 'RGBA':
        thermal_image = thermal_image.convert('RGBA')
    
    blended_image = Image.blend(thermal_image, optical_edges, alpha)
    return blended_image

optical_filepath = r'C:\Users\andre\OneDrive\Desktop\SCRG\output\result.jpg'
thermal_filepath = r'C:\Users\andre\OneDrive\Desktop\SCRG\thermal\thermal.png'

optical_image = load_image(optical_filepath)
thermal_image = load_image(thermal_filepath)

tags = get_exif_tags(thermal_filepath)

print("EXIF tags extracted from the thermal image:")
for key, value in tags.items():
    print(f"{key}: {value}")

x_offset, y_offset = get_offsets(tags)

print(optical_image.size)

# No offset adjustment applied
adjusted_thermal_image = apply_offset(thermal_image, -x_offset, -y_offset)

optical_edges = extract_edges(optical_image)

blended_image = blend_edges_with_thermal(optical_edges, adjusted_thermal_image, alpha=0.2)
blended_image.show() 
