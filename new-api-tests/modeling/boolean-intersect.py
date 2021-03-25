'''Test modeling.Modeler intersect method. 
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

## Create a modeler.
#modeler = sv.modeling.Modeler(sv.modeling.Kernel.OPENCASCADE)
modeler = sv.modeling.Modeler(sv.modeling.Kernel.POLYDATA)

# Create a cylinder.
print("Create a cylinder ...") 
center = [0.0, 0.0, 0.0]
axis = [0.0, 0.0, 1.0]
radius = 1.0
length = 10.0
cylinder1 = modeler.cylinder(center, axis, radius, length)
cylinder1_pd = cylinder1.get_polydata() 
#
axis = [0.0, 1.0, 0.0]
cylinder2 = modeler.cylinder(center, axis, radius, length)
cylinder2_pd = cylinder2.get_polydata()

## Intersect cylinders.
result = modeler.intersect(cylinder1, cylinder2)
result_pd = result.get_polydata()

## Create renderer and graphics window.
win_width = 500
win_height = 500
renderer, renderer_window = gr.init_graphics(win_width, win_height)

## Add model polydata.
gr.add_geometry(renderer, cylinder1_pd, color=[0.0, 1.0, 0.0], wire=True, edges=False)
gr.add_geometry(renderer, cylinder2_pd, color=[0.0, 0.0, 1.0], wire=True, edges=False)
gr.add_geometry(renderer, result_pd, color=[1.0, 0.0, 0.0], wire=False, edges=False)

# Display window.
gr.display(renderer_window)


