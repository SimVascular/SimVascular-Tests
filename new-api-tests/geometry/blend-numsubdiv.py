'''Experiment with blend num_subdivision_operations parameter. 
   
   default num_subdivision_operations = 1

   Blend num_subdivision_operations : 0
     Blend: Num nodes: 12074
     Blend: Num cells: 24144

   Blend num_subdivision_operations : 1
     Blend: Num nodes: 22340
     Blend: Num cells: 44676

   Blend num_subdivision_operations : 2
     Blend: Num nodes: 199108
     Blend: Num cells: 398212

   A larger num_subdivision_operations value increases the number of polygons substantually. 

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
file_name = str(data_path / 'geometry' / 'demo-no-blend.vtp')
#file_name = str(data_path / 'geometry' / 'two-cyls.vtp')
reader = vtk.vtkXMLPolyDataReader()
reader.SetFileName(file_name) 
reader.Update()
model = reader.GetOutput()
print("Model: ")
print("  Num cells: {0:d}".format(model.GetNumberOfCells()))

## Set faces to blend.
blend_radius = 1.0
print("Blend radius: {0:f}".format(blend_radius))

if "two-cyls.vtp" in file_name:
    blend_faces = [ { 'radius': blend_radius, 'face1':1, 'face2':2 } ]
elif "demo-no-blend.vtp" in file_name:
    blend_faces = [ { 'radius': blend_radius, 'face1':1, 'face2':2 } ]

## Perform the blend operation.
#
num_subdivision_operations_list = \
[ 
 (0,  [0.0,0.0,1.0]), 
 (1,  [0.0,1.0,0.0]), 
 (2, [1.0,0.0,0.0])  
]

for i,entry in enumerate(num_subdivision_operations_list):
    num_subdivision_operations = entry[0]
    color = entry[1]
    print("Blend num_subdivision_operations : {0:g}".format(num_subdivision_operations))
    options.num_subdivision_operations = num_subdivision_operations 
    blend = sv.geometry.local_blend(surface=model, faces=blend_faces, options=options)
    print("  Blend: Num nodes: {0:d}".format(blend.GetNumberOfPoints()))
    print("  Blend: Num cells: {0:d}".format(blend.GetNumberOfCells()))
    if i == 2:
        gr.add_geometry(renderer, blend, color=color, wire=True)
    else:
        gr.add_geometry(renderer, blend, color=color, wire=False)

    ## Write the blended surface.
    file_name = str(script_path / str("blend-numsubbdiv-" + str(i) + ".vtp"))
    writer = vtk.vtkXMLPolyDataWriter()
    writer.SetFileName(file_name)
    writer.SetInputData(blend)
    writer.Update()
    writer.Write()

## Show geometry.
gr.display(renderer_window)

