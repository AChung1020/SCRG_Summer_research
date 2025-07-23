import numpy as np
import imutils
import cv2
import os
import csv

def adaptive_hysteresis_thresholding(edges, sigma=0.33):
    median = np.median(edges)
    low_threshold = int(max(0, (1.0 - sigma) * median))
    high_threshold = int(min(255, (1.0 + sigma) * median))
    return low_threshold, high_threshold

def preprocess_thermal_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, d=7, sigmaColor=50, sigmaSpace=50)
    blurred_initial = cv2.GaussianBlur(gray, (5, 5), 0)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(blurred_initial)
    enhanced = cv2.normalize(enhanced, None, 0, 255, cv2.NORM_MINMAX)
    edges = cv2.Canny(enhanced, 50, 150)
    
    kernel = np.ones((3,3), np.uint8)
    connected_edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
    
    low_threshold, high_threshold = adaptive_hysteresis_thresholding(connected_edges, sigma=0.5)
    strong_edges = connected_edges > high_threshold
    weak_edges = (connected_edges <= high_threshold) & (connected_edges > low_threshold)
    
    final_edges = np.zeros_like(strong_edges, dtype=np.uint8)
    final_edges[strong_edges] = 255
    final_edges[cv2.dilate(strong_edges.astype(np.uint8), kernel, iterations=1) & weak_edges] = 255
    
    return final_edges

def process_image_pair(thermal_path, optical_path, output_dir, results_dir, csv_writer, visualize=False):
    template = cv2.imread(thermal_path)
    template = preprocess_thermal_image(template)
    edges_template = template
    (tH, tW) = edges_template.shape[:2]

    image = cv2.imread(optical_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.fastNlMeansDenoising(gray, None, h=20, searchWindowSize=35, templateWindowSize=11)

    found = None

    for scale in np.linspace(0.45, 1.0, 200)[::-1]:
        resized = imutils.resize(gray, width=int(gray.shape[1] * scale))
        r = gray.shape[1] / float(resized.shape[1])

        if resized.shape[0] < tH or resized.shape[1] < tW:
            break

        edged = cv2.Canny(resized, 50, 200)
        result = cv2.matchTemplate(edged, edges_template, cv2.TM_CCOEFF)
        (_, maxVal, _, maxLoc) = cv2.minMaxLoc(result)

        if visualize:
            clone = np.dstack([edged, edged, edged])
            cv2.rectangle(clone, (maxLoc[0], maxLoc[1]), (maxLoc[0] + tW, maxLoc[1] + tH), (0, 0, 255), 2)
            cv2.imshow("Visualize", clone)
            cv2.waitKey(0)

        if found is None or maxVal > found[0]:
            found = (maxVal, maxLoc, r)

    (_, maxLoc, r) = found
    (startX, startY) = (int(maxLoc[0] * r), int(maxLoc[1] * r))
    (endX, endY) = (int((maxLoc[0] + tW) * r), int((maxLoc[1] + tH) * r))

    # Calculate distances from edges
    distance_left = startX
    distance_right = image.shape[1] - endX
    distance_top = startY
    distance_bottom = image.shape[0] - endY

    # Write the distances to the CSV file
    csv_writer.writerow([os.path.basename(optical_path), distance_left, distance_right, distance_top, distance_bottom])

    # Create a copy of the image to draw on
    image_with_distances = image.copy()

    # Draw rectangle and distances
    cv2.rectangle(image_with_distances, (startX, startY), (endX, endY), (0, 0, 255), 2)
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.5
    font_color = (255, 255, 255)
    line_color = (0, 255, 0)
    thickness = 2

    cv2.line(image_with_distances, (0, startY), (startX, startY), line_color, thickness)
    cv2.putText(image_with_distances, f"Left: {distance_left}", (10, startY-10), font, font_scale, font_color, thickness)
    cv2.line(image_with_distances, (endX, endY), (image.shape[1], endY), line_color, thickness)
    cv2.putText(image_with_distances, f"Right: {distance_right}", (endX+10, endY-10), font, font_scale, font_color, thickness)
    cv2.line(image_with_distances, (startX, 0), (startX, startY), line_color, thickness)
    cv2.putText(image_with_distances, f"Top: {distance_top}", (startX+10, 20), font, font_scale, font_color, thickness)
    cv2.line(image_with_distances, (endX, endY), (endX, image.shape[0]), line_color, thickness)
    cv2.putText(image_with_distances, f"Bottom: {distance_bottom}", (endX-100, image.shape[0]-10), font, font_scale, font_color, thickness)

    crop_img = image[startY:endY, startX:endX]
    thermal_image = cv2.imread(thermal_path, cv2.IMREAD_COLOR)
    crop_img_resized = cv2.resize(crop_img, (thermal_image.shape[1], thermal_image.shape[0]))

    cv2.imwrite(os.path.join(output_dir, os.path.basename(optical_path)), crop_img_resized)

    final = np.concatenate((crop_img_resized, thermal_image), axis=1)
    cv2.imwrite(os.path.join(results_dir, os.path.basename(optical_path)), final)

def main():
    # MAY NEED TO CHANGE THE DIRECTORY PATHS
    thermal_main_dir = r'C:\Users\andre\OneDrive\Desktop\SCRG\Thermal Images'
    optical_main_dir = r'C:\Users\andre\OneDrive\Desktop\SCRG\Optical Images'
    visualize = False  # Set to True if you want to visualize each iteration

    for thermal_dir in os.listdir(thermal_main_dir):
        if thermal_dir.startswith("thermal_HIP_"):
            number = thermal_dir.split("_")[-1]
            optical_dir = f"optical_HIP_{number}"
            
            if not os.path.exists(os.path.join(optical_main_dir, optical_dir)):
                print(f"Skipping {thermal_dir} as matching optical directory not found.")
                continue

            output_dir = f'./Output/output_HIP_{number}/'
            results_dir = f'./Results/results_HIP_{number}/'

            # Check if both output and results directories already exist
            if os.path.exists(output_dir) and os.path.exists(results_dir):
                print(f"Skipping HIP_{number} as output and results directories already exist.")
                continue

            os.makedirs(output_dir, exist_ok=True)
            os.makedirs(results_dir, exist_ok=True)


            # MAY NEED TO CHANGE DIRECTORY FILEPATH SO ./SCRG
            csv_file = os.path.join('./SCRG', f'pixel_offsets_{number}.csv')

            with open(csv_file, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Filename", "Left", "Right", "Top", "Bottom"])

                thermal_path = os.path.join(thermal_main_dir, thermal_dir)
                optical_path = os.path.join(optical_main_dir, optical_dir)

                for filename in os.listdir(thermal_path):
                    if filename.endswith("_thermal.jpg"):
                        base_name = os.path.splitext(filename)[0].replace("_thermal", "")
                        print(f"Processing {base_name}")

                        thermal_file = os.path.join(thermal_path, filename)
                        optical_file = os.path.join(optical_path, f"{base_name}_optical.jpg")

                        if not os.path.exists(optical_file):
                            print(f"Skipping {base_name} as matching optical file not found.")
                            continue

                        process_image_pair(thermal_file, optical_file, output_dir, results_dir, writer, visualize)

    print("Processing complete.")

if __name__ == "__main__":
    main()