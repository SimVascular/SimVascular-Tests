'''Experiment with blend num_lapsmooth_iterations parameter. 
   
   default num_lapsmooth_iterations = 50

   Blend num_lapsmooth_iterations : 1
     Blend: Num nodes: 22340
     Blend: Num cells: 44676

   Blend num_lapsmooth_iterations : 50
     Blend: Num nodes: 22340
     Blend: Num cells: 44676

   Blend num_lapsmooth_iterations : 100
     Blend: Num nodes: 22340
     Blend: Num cells: 44676

   A larger num_lapsmooth_iterations increases spreading the blend, reduces the curvature 
   between vessels at the union boundary.

'''
from pathlib import Path
import sv
import sys
import vtk
sys.path.insert(1, '../graphics/')
import graphics as gr

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
mdir = '../data/geometry/'
file_name = "demo-no-blend.vtp" 
file_name = "two-cyls.vtp" 
reader = vtk.vtkXMLPolyDataReader()
reader.SetFileName(mdir+file_name) 
reader.Update()
model = reader.GetOutput()

## Set faces to blend.
blend_radius = 1.0
print("Blend radius: {0:f}".format(blend_radius))

if file_name == "two-cyls.vtp":
    blend_faces = [ { 'radius': blend_radius, 'face1':1, 'face2':2 } ]
elif file_name == "demo-no-blend.vtp":
    blend_faces = [ { 'radius': blend_radius, 'face1':1, 'face2':2 } ]

## Perform the blend operation.
#
num_lapsmooth_iterations_list = \
[ 
 (1,   [0.0,0.0,1.0]), 
 (50,  [0.0,1.0,0.0]), 
 (1000, [1.0,0.0,0.0])  
]

for i,entry in enumerate(num_lapsmooth_iterations_list):
    num_lapsmooth_iterations = entry[0]
    color = entry[1]
    print("Blend num_lapsmooth_iterations : {0:g}".format(num_lapsmooth_iterations))
    options.num_lapsmooth_iterations = num_lapsmooth_iterations 
    blend = sv.geometry.local_blend(surface=model, faces=blend_faces, options=options)
    print("  Blend: Num nodes: {0:d}".format(blend.GetNumberOfPoints()))
    print("  Blend: Num cells: {0:d}".format(blend.GetNumberOfCells()))
    if i == 2:
        gr.add_geometry(renderer, blend, color=color, wire=True)
    else:
        gr.add_geometry(renderer, blend, color=color, wire=False)

    ## Write the blended surface.
    file_name = "blend-numlapsmooth-" + str(i) + ".vtp"
    writer = vtk.vtkXMLPolyDataWriter()
    writer.SetFileName(file_name)
    writer.SetInputData(blend)
    writer.Update()
    writer.Write()

## Show geometry.
gr.display(renderer_window)

