'''Experiment with blend num_cgsmooth_iterations parameter. 
   
   default num_cgsmooth_iterations = 2

   Blend num_cgsmooth_iterations : 1

   Blend num_cgsmooth_iterations : 2

   Blend num_cgsmooth_iterations : 10

   A larger num_cgsmooth_iterations increases spreading somewhat the blend, reduces the curvature 
   between vessels at the union boundary, at a higher cost.

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
num_cgsmooth_iterations_list = \
[ 
 (1,  [0.0,0.0,1.0]), 
 (2,  [0.0,1.0,0.0]), 
 (10, [1.0,0.0,0.0])  
]

for i,entry in enumerate(num_cgsmooth_iterations_list):
    num_cgsmooth_iterations = entry[0]
    color = entry[1]
    print("Blend num_cgsmooth_iterations : {0:g}".format(num_cgsmooth_iterations))
    options.num_cgsmooth_iterations = num_cgsmooth_iterations 
    blend = sv.geometry.local_blend(surface=model, faces=blend_faces, options=options)
    print("  Blend: Num nodes: {0:d}".format(blend.GetNumberOfPoints()))
    print("  Blend: Num cells: {0:d}".format(blend.GetNumberOfCells()))
    if i == 2:
        gr.add_geometry(renderer, blend, color=color, wire=True)
    else:
        gr.add_geometry(renderer, blend, color=color, wire=False)

    ## Write the blended surface.
    file_name = script_path / str("blend-numcgsmooth-" + str(i) + ".vtp")
    writer = vtk.vtkXMLPolyDataWriter()
    writer.SetFileName(str(file_name))
    writer.SetInputData(blend)
    writer.Update()
    writer.Write()

## Show geometry.
gr.display(renderer_window)

