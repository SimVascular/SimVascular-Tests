'''
Test the sv.geometry.local_blend() function. 
'''
from pathlib import Path
import sv
import vtk

## Create blend options.
options = sv.geometry.BlendOptions()
print("\n\nOptions values: ")
[ print("  {0:s}:{1:s}".format(key,str(value))) for (key, value) in sorted(options.get_values().items()) ]
print("\n\n")

## Read in a model.
file_name = "two-cyls.vtp" 
reader = vtk.vtkXMLPolyDataReader()
reader.SetFileName(file_name) 
reader.Update()
model = reader.GetOutput()

## Set faces to blend.
if file_name == "two-cyls.vtp":
    blend_faces = [ { 'radius': 0.5, 'face1':1, 'face2':2 } ]

## Perform the blend operation.
blend = sv.geometry.local_blend(surface=model, faces=blend_faces, options=options)

## Write the blended surface.
file_name = "blended-" + file_name;
writer = vtk.vtkXMLPolyDataWriter()
writer.SetFileName(file_name)
writer.SetInputData(blend)
writer.Update()
writer.Write()




