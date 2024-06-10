import flirimageextractor
from matplotlib import cm

flir = flirimageextractor.FlirImageExtractor(palettes=[cm.jet, cm.bwr, cm.gist_ncar])
flir.process_image(r'C:\Users\andre\OneDrive\Desktop\SCRG_Research\HIP_01\Renamed Images\HIP_01_E8XT_1_Base.jpg')
flir.save_images()
flir.plot()