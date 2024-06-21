import os
import cv2

def blend_images(image1, image2, alpha):
    """
    Blend two images using alpha blending, with emphasized edges on image2.
    
    Args:
    - image1: The first image (background).
    - image2: The second image (overlay).
    - alpha: The alpha value for blending (between 0.0 and 1.0).
    
    Returns:
    - blended_image: The resulting blended image.
    """
    image2_edges = cv2.Canny(image2, 50, 200) 
    
    image2_edges_bgr = cv2.cvtColor(image2_edges, cv2.COLOR_GRAY2BGR)
    
    blended_image2 = cv2.addWeighted(image2_edges_bgr, alpha, image2, 1 - alpha, 0)
    
    blended_image = cv2.addWeighted(image1, 1 - alpha, blended_image2, alpha, 0)
    
    return blended_image

def main(thermal_dir, visible_dir):
    output_directory = os.path.join(thermal_dir, 'blended')
    os.makedirs(output_directory, exist_ok=True)

    # Loop through all files in the thermal directory
    for filename in os.listdir(thermal_dir):
        if filename.endswith("_thermal.jpg"):
            # Get the base name of the file without the "_thermal.jpg" extension
            base_name = os.path.splitext(filename)[0].replace("_thermal", "")

            # Load the thermal image
            image1_path = os.path.join(thermal_dir, filename)
            image1 = cv2.imread(image1_path)

            if image1 is None:
                print(f"Error loading thermal image: {filename}")
                continue

            # Load the corresponding visible image
            visible_filename = base_name + "_optical.jpg"
            image2_path = os.path.join(visible_dir, visible_filename)
            image2 = cv2.imread(image2_path)

            if image2 is None:
                print(f"Error loading visible image: {visible_filename}")
                continue

            # Define the alpha value (transparency level)
            alpha = 0.1  

            blended_image = blend_images(image1, image2, alpha)

            output_path = os.path.join(output_directory, filename)
            cv2.imwrite(output_path, blended_image)

            print(f"Blended image saved to: {output_path}")

if __name__ == "__main__":
    # TODO: Define the file paths to the directories containing thermal and visible images
    thermal_dir = r'C:\Users\andre\OneDrive\Desktop\SCRG\thermal'
    visible_dir = r'C:\Users\andre\OneDrive\Desktop\SCRG\output'

    main(thermal_dir, visible_dir)