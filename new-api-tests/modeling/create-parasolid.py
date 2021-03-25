'''Test creating a Parasolid model.
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
kernel = sv.modeling.Kernel.PARASOLID
modeler = sv.modeling.Modeler(kernel)

## Create a cylinder.
print("Create a cylinder.") 
center = [0.0, 0.0, 0.0]
axis = [0.0, 0.0, 1.0]
radius = 1.5
length = 10.0
cyl = modeler.cylinder(center, axis, radius, length)
face_ids = cyl.get_face_ids()
print("Model face IDs: " + str(face_ids))

## Write the model.
cyl.write(file_name=str(script_path/"cylinder-parasolid"))

## Create renderer and graphics window.
win_width = 500
win_height = 500
renderer, renderer_window = gr.init_graphics(win_width, win_height)

## Add model polydata.
polydata = cyl.get_polydata() 
gr.add_geometry(renderer, polydata, color=[1.0, 0.0, 0.0], wire=False, edges=True)

# Display window.
gr.display(renderer_window)



