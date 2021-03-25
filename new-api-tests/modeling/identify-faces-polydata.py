''' Test identifying faces for a POLYDATA model.
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

## Create renderer and graphics window.
win_width = 500
win_height = 500
renderer, renderer_window = gr.init_graphics(win_width, win_height)

## Create a modeler.
file_name = str(data_path / 'DemoProject' / 'Models' / 'demo.vtp')
#file_name = str(data_path / 'models' / 'cylinder.stl')
modeler = sv.modeling.Modeler(sv.modeling.Kernel.POLYDATA)
model = modeler.read(file_name)
print("Model type: " + str(type(model)))

## Compute model face IDs for STL file.
if 'stl' in file_name:
    face_ids = model.compute_boundary_faces(angle=60.0)
face_ids = model.get_face_ids()
print("Number of model Face IDs: {0:d}".format(len(face_ids)))
#print("Model Face IDs: {0:s}".format(str(face_ids)))

## Identify the model faces caps.
face_caps = model.identify_caps()
#print(face_types)

## Show the caps.
num_caps = 0
for face_id,is_cap in zip(face_ids, face_caps):
    face_polydata = model.get_face_polydata(face_id=face_id)
    if is_cap:
        gr.add_geometry(renderer, face_polydata, color=[1.0, 0.0, 0.0], wire=False)
        num_caps += 1
    else:
        gr.add_geometry(renderer, face_polydata, color=[0.0, 1.0, 0.0], wire=False)

print("Number of caps: " + str(num_caps))

# Display window.
gr.display(renderer_window)

