'''Test imaging.Image read methods. 
'''
import os
import sv
import vtk
import sys
sys.path.insert(1, '../graphics/')
import graphics as gr

# The location of some imaging data.
sv_data_dir = os.environ['SIMVASCULAR_DATA']

## Read an image.
#
print("Read image file ...")
file_name = sv_data_dir + "/data/OSMSC0110-aorta/image_data/volume/I.002.dcm"
file_name = sv_data_dir + "/DemoProject/Images/sample_data-cm.vti"

# Read image in constructor.
use_ctor = False

if use_ctor: 
    image = sv.imaging.Image(file_name)
else:
    image = sv.imaging.Image()
    image.read(file_name)

dimensions = image.get_dimensions()
print("Image dimensions: {0:g} {1:g} {2:g}".format(dimensions[0], dimensions[1], dimensions[2]))

spacing = image.get_spacing()
print("Image spacing: {0:g} {1:g} {2:g}".format(spacing[0], spacing[1], spacing[2]))

