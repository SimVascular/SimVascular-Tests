'''Test imaging.Image transform methods. 
'''
import os
import sv
import vtk
import sys
sys.path.insert(1, '../graphics/')
import graphics as gr

# The location of some imaging data.
sv_data_dir = os.environ['SIMVASCULAR_DATA']

## Create an Image object.
#
print("Read image file ...")
file_name = sv_data_dir + "/data/OSMSC0110-aorta/image_data/volume/I.002.dcm"
file_name = sv_data_dir + "/DemoProject/Images/sample_data-cm.vti"
image = sv.imaging.Image(file_name)
dimensions = image.get_dimensions()
print("Image dimensions: {0:g} {1:g} {2:g}".format(dimensions[0], dimensions[1], dimensions[2]))
spacing = image.get_spacing()
print("Image spacing: {0:g} {1:g} {2:g}".format(spacing[0], spacing[1], spacing[2]))
origin = image.get_origin()
print("Image origin: {0:g} {1:g} {2:g}".format(origin[0], origin[1], origin[2]))

## Set the transformation matrix.
#
matrix = vtk.vtkMatrix4x4()
matrix.Identity()
for i in range(3):
    matrix.SetElement(i, 3, origin[i])

## Transform the image.
#
image.transform(matrix)
origin = image.get_origin()
print("New Image origin: {0:g} {1:g} {2:g}".format(origin[0], origin[1], origin[2]))

