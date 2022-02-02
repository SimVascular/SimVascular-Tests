'''Test the sv.geometry.local_sphere_smooth() function. 
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

## Read model to smooth.
file_name = str(data_path / 'geometry' / 'two-cyls.vtp')
reader = vtk.vtkXMLPolyDataReader()
reader.SetFileName(file_name) 
reader.Update()
model = reader.GetOutput()
gr.add_geometry(renderer, model, wire=True)

radius = 1.0
center = [-0.1, 4.0, -0.4]
gr.add_sphere(renderer, center, radius, color=[0,1,0], wire=True)

## Perform the smoothing operation.
smoothing_params = { 'method':'laplacian', 'num_iterations':100, 'relaxation_factor':0.01 } 
smoothing_params = { 'method':'constrained', 'num_iterations':5, 'constrain_factor':0.2, 'num_cg_solves':30 } 

smoothed_model = sv.geometry.local_sphere_smooth(model, radius, center, smoothing_params)
gr.add_geometry(renderer, smoothed_model, color=[1,0,0])

## Show geometry.
gr.display(renderer_window)


