semi_automatic_alignment runs in the following manner:

the paths can be set with these variablesL

THERMAL_BASE_DIR = the path to the thermal images
VISIBLE_BASE_DIR = the path tot the optical images


it assumes that the directory structure of each of thermal_base_dir and visible_base_dir have subdirectories for each subject. It also assumes that the names of the thermal_base_dir images and visible_base_dir images have matching names besides the suffix. So for example HIP_01_E8XT_Cool, the files that represent the optical(HIP_01_E8XT_Cool_optical) and thermal images(HIP_01_E8XT_Cool_thermal) for this patient data will be the same, and it will automatically drop the
suffix _optical and _thermal. 

You do not need to change the output_base_dir, blended_output_base_dir, and cropped_optical_base_dir unless you want different directory names. 


When you run the program, it will immediately begin. the general process of the alignment goes as follows:

Thermal image pops up -> click 2 points -> Optical image pops up -> click 2 points -> show the aligned image: if satisfied click "y" else click "n".(make sure not in caps lock)

The points must be clicked in the same order, meaning the corresponding points in the thermal and optical iamge MUST be clicked in the same order or else the
algnment process won't work. 

Also a general tip is to click points not in a straight line, as it seems to help with the alignment. 
Another tip is to try and pick points over a large area, not in a small area.

Andrew Chung 08/21/24

