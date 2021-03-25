'''Test creating a POLYDATA model from a PolyData object.
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

## Read PolyData.
file_name = str(data_path / 'models' / 'loft-test-interpolate.vtp')
reader = vtk.vtkXMLPolyDataReader()
reader.SetFileName(file_name) 
reader.Update()
read_polydata = reader.GetOutput()

## Create a model from the PolyData object.
model = sv.modeling.PolyData(surface=read_polydata)
polydata = model.get_polydata()

## Compute boundary faces.
face_ids = model.compute_boundary_faces(angle=60.0)
print("Model face IDs: " + str(face_ids))

## Write the model.
if True:
    file_name = str(script_path / "loft-model-written")
    file_format = "vtp"
    model.write(file_name=file_name, format=file_format)

## Create renderer and graphics window.
win_width = 500
win_height = 500
renderer, renderer_window = gr.init_graphics(win_width, win_height)

## Add model polydata.
gr.add_geometry(renderer, polydata, color=[1.0, 0.0, 0.0], wire=False, edges=True)

# Display window.
gr.display(renderer_window)



