'''Test settng the image spacing. 
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

# Read image.
image = sv.imaging.Image(file_name)

origin = image.get_origin()
print("Image origin: {0:g} {1:g} {2:g}".format(origin[0], origin[1], origin[2]))
dimensions = image.get_dimensions()
print("Image dimensions: {0:g} {1:g} {2:g}".format(dimensions[0], dimensions[1], dimensions[2]))
spacing = image.get_spacing()
print("Image spacing: {0:g} {1:g} {2:g}".format(spacing[0], spacing[1], spacing[2]))

image.set_spacing([0.0078125, 0.02, 0.0078125])

spacing = image.get_spacing()
print("New image spacing: {0:g} {1:g} {2:g}".format(spacing[0], spacing[1], spacing[2]))

