'''Experiment with blend target_decimation parameter. 
   
   default target_decimation = 0.01 

   while ( this->ActualReduction < this->TargetReduction )

   ActualReduction = (double) numDeletedTris / numTris;

      numDeletedTris / numTris = 0.01 = 1%  

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
mdir = '../data/geometry/'
file_name = "two-cyls.vtp" 
file_name = "demo-no-blend.vtp" 
reader = vtk.vtkXMLPolyDataReader()
reader.SetFileName(mdir+file_name) 
reader.Update()
model = reader.GetOutput()

## Set faces to blend.
if file_name == "two-cyls.vtp":
    blend_faces = [ { 'radius': 0.5, 'face1':1, 'face2':2 } ]
elif file_name == "demo-no-blend.vtp":
    blend_faces = [ { 'radius': 0.5, 'face1':1, 'face2':2 } ]

## Perform the blend operation.
blend = sv.geometry.local_blend(surface=model, faces=blend_faces, options=options)
print("Blend: Num nodes: {0:d}".format(blend.GetNumberOfPoints()))
print("Blend: Num cells: {0:d}".format(blend.GetNumberOfCells()))

## Write the blended surface.
file_name = "blended-" + file_name;
writer = vtk.vtkXMLPolyDataWriter()
writer.SetFileName(file_name)
writer.SetInputData(blend)
writer.Update()
writer.Write()


