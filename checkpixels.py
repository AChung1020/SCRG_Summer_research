import cv2

def show_pixel_value(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f'The pixel value at ({x}, {y}) is {image[y, x]}')

# Load the image
image = cv2.imread(r'C:\Users\andre\OneDrive\Desktop\SCRG\thermal\HIP_01_ProOne_1_Cool_thermal.jpg', cv2.IMREAD_GRAYSCALE)

# Display the image
cv2.imshow('Image', image)

# Set the mouse callback function
cv2.setMouseCallback('Image', show_pixel_value)

cv2.waitKey(0)
cv2.destroyAllWindows()
