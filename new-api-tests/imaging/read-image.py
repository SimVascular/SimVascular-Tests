'''Test imaging.Image read methods. 
'''
import sv
import vtk
import sys
sys.path.insert(1, '../graphics/')
import graphics as gr

## Read an image.
#
print("Read image file ...")

file_name = "sample_data-cm.vti"
file_name = "/Users/parkerda/SimVascular/data/OSMSC0110-aorta/image_data/volume/I.002.dcm"

image = sv.imaging.Image(file_name)
dimensions = image.get_dimensions()
print("Image dimensions: {0:g} {1:g} {2:g}".format(dimensions[0], dimensions[1], dimensions[2]))

spacing = image.get_spacing()
print("Image spacing: {0:g} {1:g} {2:g}".format(spacing[0], spacing[1], spacing[2]))

