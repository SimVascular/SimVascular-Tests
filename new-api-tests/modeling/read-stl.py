'''Read in an STL file and write out an SV VTP model file.

   The VTP file is written to 'read-stl-vtp-model.vtp'.
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
    e = sys.exc_info()[0]
    print("Can't find the new-api-tests/graphics package.")
    print('Exception is: ' + str(e))

## Create a modeler.
#
kernel = sv.modeling.Kernel.POLYDATA 
modeler = sv.modeling.Modeler(kernel)

## Read a model.
#
print("Read STL file ...")
file_name = str(data_path / 'models' / 'cylinder.stl')
model = modeler.read(file_name)

## Compute boundary faces if needed.
#
try:
    face_ids = model.get_face_ids()
except:
    face_ids = model.compute_boundary_faces(angle=60.0)
print("Model face IDs: " + str(face_ids))

## Remesh the model.
#
#  If the STL model contains long triangles then it is a good idea to remesh it. 
#
#  Note: The model may need to be remeshed twice to get a new surface representation.
#
remesh = True
if remesh:
    model_surf = model.get_polydata()
    remesh_model = sv.mesh_utils.remesh(model.get_polydata(), hmin=0.4, hmax=0.4)
    model.set_surface(surface=remesh_model)
    model.compute_boundary_faces(angle=60.0)

    remesh_model = sv.mesh_utils.remesh(model.get_polydata(), hmin=0.4, hmax=0.4)
    model.set_surface(surface=remesh_model)
    model.compute_boundary_faces(angle=60.0)

## Write the model.
file_name = str(script_path / "read-stl-vtp-model")
file_format = "vtp"
model.write(file_name=file_name, format=file_format)

## Create renderer and graphics window.
win_width = 500
win_height = 500
renderer, renderer_window = gr.init_graphics(win_width, win_height)

# Add model geometry using the ModelFaceID array displaying faces with different colors. 
model_pd = model.get_polydata()
fids_range = [min(face_ids), max(face_ids)]
gr.add_geometry(renderer, model_pd, array_name="ModelFaceID", scalar_range=fids_range)

# Add an interactor used to pick model faces using the 's' key.
interactor = gr.init_picking(renderer_window, renderer, surface=model_pd)
interactor.Start()

