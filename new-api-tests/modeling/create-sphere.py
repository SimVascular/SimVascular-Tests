'''Test creating a sphere.
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

# Create a modeler.
#modeler = sv.modeling.Modeler(sv.modeling.Kernel.OPENCASCADE)
modeler = sv.modeling.Modeler(sv.modeling.Kernel.POLYDATA)

## Create a sphere.
print("Create a sphere ...")
center = [0.0, 0.0, 0.0]
radius = 2.0 
sphere = modeler.sphere(center=center, radius=radius)
print("  Sphere type: " + str(type(sphere)))
sphere_pd = sphere.get_polydata()
print("  Sphere: num nodes: {0:d}".format(sphere_pd.GetNumberOfPoints()))
 
## Create renderer and graphics window.
win_width = 500
win_height = 500
renderer, renderer_window = gr.init_graphics(win_width, win_height)

## Add model polydata.
gr.add_geometry(renderer, sphere_pd, color=[0.0, 1.0, 0.0], wire=True, edges=False)

# Display window.
gr.display(renderer_window)

