'''Experiment with blend target_decimation parameter. 
   
   default target_decimation = 0.01 

   while ( this->ActualReduction < this->TargetReduction )

   ActualReduction = (double) numDeletedTris / numTris;

      numDeletedTris / numTris = 0.01 = 1%  

 target_decimation = 0.0
   Blend: Num nodes: 13672
   Blend: Num cells: 27340

 target_decimation = 0.01 
   Blend: Num nodes: 22340
   Blend: Num cells: 44676

 target_decimation = 0.02 
   Blend: Num nodes: 14984
   Blend: Num cells: 29964

 target_decimation = 0.10 

'''
import os
from pathlib import Path
import sv
import sys
import vtk

## Set some directory paths. 
script_path = Path(os.path.realpath(__file__)).parent
parent_path = Path(os.path.realpath(__file__)).parent.parent
data_path = parent_path / 'data'

try:
    sys.path.insert(1, str(parent_path / 'graphics'))
    import graphics as gr
except:
    print("Can't find the new-api-tests/graphics package.")

## Initialize graphics.
#
win_width = 500
win_height = 500
renderer, renderer_window = gr.init_graphics(win_width, win_height)

## Create blend options.
options = sv.geometry.BlendOptions()
print("\n\nOptions values: ")
[ print("  {0:s}:{1:s}".format(key,str(value))) for (key, value) in sorted(options.get_values().items()) ]
print("\n\n")
#

## Read in a model.
file_name = str(data_path / 'geometry' / 'two-cyls.vtp')
#file_name = str(data_path / 'geometry' / 'demo-no-blend.vtp')
reader = vtk.vtkXMLPolyDataReader()
reader.SetFileName(file_name) 
reader.Update()
model = reader.GetOutput()

## Set faces to blend.
blend_radius = 1.0
print("Blend radius: {0:f}".format(blend_radius))

if "two-cyls.vtp" in file_name:
    blend_faces = [ { 'radius': blend_radius, 'face1':1, 'face2':2 } ]
elif "demo-no-blend.vtp" in file_name:
    blend_faces = [ { 'radius': blend_radius, 'face1':1, 'face2':2 } ]

## Perform the blend operation.
#
target_decimation_list = [ (0.01, [1.0,0.0,0.0]), (0.02,[0.0,1.0,0.0]),  (0.10,[0.0,0.0,1.0])  ]

for i,entry in enumerate(target_decimation_list):
    target_decimation = entry[0]
    color = entry[1]
    print("Blend target_decimation: {0:g}".format(target_decimation))
    options.target_decimation = target_decimation 
    blend = sv.geometry.local_blend(surface=model, faces=blend_faces, options=options)
    print("  Blend: Num nodes: {0:d}".format(blend.GetNumberOfPoints()))
    print("  Blend: Num cells: {0:d}".format(blend.GetNumberOfCells()))
    gr.add_geometry(renderer, blend, color=color, wire=True)

    ## Write the blended surface.
    file_name = str(script_path / str("blended-decimate-" + str(i) + ".vtp"))
    writer = vtk.vtkXMLPolyDataWriter()
    writer.SetFileName(file_name)
    writer.SetInputData(blend)
    writer.Update()
    writer.Write()

## Show geometry.
gr.display(renderer_window)

