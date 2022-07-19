'''Exmaple to create a saccular aneurysm by unioning a sphere with the demo aorta model. 
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
#
kernel = sv.modeling.Kernel.POLYDATA 
modeler = sv.modeling.Modeler(kernel)

## Read a model.
#
print("Read modeling model file ...")
file_name = str(data_path / 'DemoProject' / 'Models' / 'demo.vtp')
model = modeler.read(file_name)

## Compute boundary faces if needed.
#
try:
    face_ids = model.get_face_ids()
except:
    face_ids = model.compute_boundary_faces(angle=60.0)
print("Model face IDs: " + str(face_ids))

## Create a sphere.
print("Create a sphere ...")
center = [1.0, 3.0, -8.0]
radius = 2.0
sphere = modeler.sphere(center=center, radius=radius)
print("  Sphere type: " + str(type(sphere)))

## Union sphere and model.
model_union = modeler.union(model1=model, model2=sphere)

## Write the model.
file_name = "aneurysm"
file_format = "vtp"
model_union.write(file_name=str(script_path / file_name), format=file_format)

## Create renderer and graphics window.
win_width = 500
win_height = 500
renderer, renderer_window = gr.init_graphics(win_width, win_height)

## Add model polydata.
model_pd = model.get_polydata()
gr.add_geometry(renderer, model_pd, color=[0.0, 1.0, 0.0], wire=True, edges=False)

## Add sphere polydata.
sphere_pd = sphere.get_polydata()
gr.add_geometry(renderer, sphere_pd, color=[0.0, 0.0, 1.0], wire=True, edges=False)

## Add model union polydata.
model_union_pd = model_union.get_polydata()
gr.add_geometry(renderer, model_union_pd, color=[1.0, 0.0, 0.0], wire=True, edges=False)

# Display window.
gr.display(renderer_window)

