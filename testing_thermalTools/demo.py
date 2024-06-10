# -*- coding: utf-8 -*-
"""
This script contains a demonstration of the functions and capabilities of this
repository. It will also give an example work flow for a set of images.

@author: susanmeerdink
December 2019
"""

# Importing Functions
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TKAgg') # Needed to have figures display properly. 
import flirimageextractor
import utilities as u

## Load Image using flirimageextractor
# Note: I had to change the path of my exiftool which you may need to also change.
filename = r'C:\Users\andre\OneDrive\Desktop\SCRG_Research\HIP_01\ProOne\20240326T144930.jpg'
flir = flirimageextractor.FlirImageExtractor()
flir.process_image(filename, RGB=True)

## Examine thermal and full resolution RGB images
# Most FLIR cameras take a thermal image and a corresponding RGB image. 
# The RGB camera is higher resolution and has a larger field of view. 
therm = flir.get_thermal_np()
rgb_fullres = flir.get_rgb_np()

## Check how well thermal and rgb registration is without manually correction
# You can see that the images do not line up and there is an offset even after 
# correcting for offset provided in file header
rgb_lowres, rgb_crop = u.extract_coarse_image(flir)

### Determine manual correction of Thermal and RGB registration 
offset, pts_temp, pts_rgb = u.manual_img_registration(flir)
print('X pixel offset is ' + str(offset[0]) + ' and Y pixel offset is ' + str(offset[1]))

## Fix Thermal and RGB registration with manual correction
# You can see with the manually determined offsets that the images are now aligned.
# By doing this we can use the RGB image to classify the material types in the images.
# This is useful if you are interested in one particular part or class type.
offset = [-261.0, -171.0]  # This i the manual offset I got when running the demo images.
rgb_lowres, rgb_crop = u.extract_coarse_image(flir, offset=offset, plot=1)
