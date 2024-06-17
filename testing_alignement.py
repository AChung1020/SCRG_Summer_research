import os
import cv2
import sys

#To run this file, you need to do the following:
#run python3 alignment.py <filename>
#Scroll down to the TODO and change the file paths tot he location of the thermal and cropped visible(output) images

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

def main(filename):
    #TODO: Define the file paths to the place you have the images
    image1_path = os.path.join(r'C:\Users\andre\OneDrive\Desktop\SCRG\thermal', filename)
    image2_path = os.path.join(r'C:\Users\andre\OneDrive\Desktop\SCRG\output', filename)

    # Load the two images
    image1 = cv2.imread(image1_path)
    image2 = cv2.imread(image2_path)

    if image1 is None or image2 is None:
        print(f"Error loading images with filename: {filename}")
        return

    # Define the alpha value (transparency level)
    alpha = 0.1  

    blended_image = blend_images(image1, image2, alpha)

    output_directory = os.path.join(os.path.dirname(image1_path), 'blended')
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    output_path = os.path.join(output_directory, filename)
    cv2.imwrite(output_path, blended_image)

    print(f"Blended image saved to: {output_path}")

    # Optionally display the blended image
    cv2.imshow('Blended Image', blended_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <filename>")
    else:
        main(sys.argv[1])
