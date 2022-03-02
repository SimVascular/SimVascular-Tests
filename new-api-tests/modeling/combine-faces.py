'''Test solid.Modeler combine faces method. 

   This method is only defined for PolyData models.
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
modeler = sv.modeling.Modeler(sv.modeling.Kernel.POLYDATA)

## Read a model.
#
print("Read modeling model file ...")
file_name = str(data_path / 'models' / 'cylinder.vtp')
model = modeler.read(file_name)

## Compute boundary faces if needed.
#
try:
    face_ids = model.get_face_ids()
except:
    face_ids = model.compute_boundary_faces(angle=60.0)
print("Model face IDs: " + str(face_ids))

## Combine faces
model.combine_faces(face_id=1, combine_with=[2])

face_ids = model.get_face_ids()
print("New model face IDs: " + str(face_ids))

## Write the model.
#file_name = str(script_Path / "model-written")
#file_format = "vtp"
#model.write(file_name=file_name, format=file_format)

## Create renderer and graphics window.
win_width = 500
win_height = 500
renderer, renderer_window = gr.init_graphics(win_width, win_height)

## Add model polydata.
model_pd = model.get_polydata()
#gr.add_geometry(renderer, model_pd, color=[0.0, 1.0, 0.0], wire=True, edges=False)

face1_polydata = model.get_face_polydata(face_id=face_ids[0])
gr.add_geometry(renderer, face1_polydata, color=[1.0, 0.0, 0.0], wire=False)

face2_polydata = model.get_face_polydata(face_id=face_ids[1])
gr.add_geometry(renderer, face2_polydata, color=[0.0, 1.0, 0.0], wire=False)

# Display window.
gr.display(renderer_window)

