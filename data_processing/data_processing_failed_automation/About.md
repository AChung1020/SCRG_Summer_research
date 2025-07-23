To get to the end results, run the files in the following manner:

flir_image_extraction -> png_to_jpg_converter -> alignment -> sorting folders -> remove_outliers -> averaging -> manual_adjustment -> find_alignment

In each of the folders, you have to change the directory paths so that the function will find the correct files every time

The following files execute the following:
flir image extraction -> extracts the optical, thermal, and csv files. The thermal images are JPGs
png_to_jpg_converter -> converts the PNG thermal images to JPG images which allows us to use cv2
alignment -> will find the csv distances and the automated outputs and results which will be output and results. Most likely the outputs and results from this script will not be useful, since the ones we save are the final outputs and final results located in manual adjustment script.
sorting folders -> Will sort the Thermal and Optical images into their respective distances and camera types
remove outliers -> will remove outliers based on a plus minus error of the values indicated int he file
averaging -> will average all the numbers for each camera type for each subject
manual adjustment -> will adjust the new Final outputs and final results to the average calculated by averaging
find alignment -> will blend the images together

In the folders, always pay attention to the directories, as that is what you will need to change for each local device. 

Wish to find a better and more accurate way to do this.

Andrew Chung 07/01/2024

Useless, failed attempt.