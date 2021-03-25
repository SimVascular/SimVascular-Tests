'''Test creating a cylinder.
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
kernel = sv.modeling.Kernel.POLYDATA
modeler = sv.modeling.Modeler(kernel)
print("Modeler type: " + str(type(modeler)))

## Create a cylinder.
print("Create a cylinder ...")
center = [0.0, 0.0, 0.0]
axis = [0.0, 1.0, 0.0]
axis = [1.0, 0.0, 0.0]
radius = 1.0 
length = 6.0 
cylinder = modeler.cylinder(center=center, axis=axis, radius=radius, length=length)
print("  Cylinder type: " + str(type(cylinder)))
print(dir(cylinder))
#
cylinder.compute_boundary_faces(angle=60.0)

cylinder_pd = cylinder.get_polydata()
print("  Cylinder: num nodes: {0:d}".format(cylinder_pd.GetNumberOfPoints()))

## Write the model.
file_name = str(script_path / "cylinder-model-write")
file_format = "vtp"
cylinder.write(file_name=file_name, format=file_format)

## Create renderer and graphics window.
win_width = 500
win_height = 500
renderer, renderer_window = gr.init_graphics(win_width, win_height)

## Add model polydata.
gr.add_geometry(renderer, cylinder_pd, color=[0.0, 1.0, 0.0], wire=True, edges=False)

## Add a sphere.
gr.add_sphere(renderer, center=center, radius=0.1, color=[1.0, 1.0, 1.0], wire=True)

pt1 = center
pt2 = [ center[i] + length/2.0 * axis[i] for i in range(3) ]
gr.add_line(renderer, pt1, pt2, color=[0.5, 0.0, 0.0], width=4)

# Display window.
gr.display(renderer_window)



