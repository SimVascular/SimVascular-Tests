'''This scipt tests reading in an SV Model .mdl file.
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

## Read an SV model group file. 
#
home = str(Path.home())
file_name = str(data_path / 'DemoProject' / 'Models' / 'demo.mdl')
print("Read SV mdl file: {0:s}".format(file_name))
demo_models = sv.modeling.Series(file_name)
num_models = demo_models.get_num_times()
print("  Number of models: {0:d}".format(num_models))

print("Get a model for time=0")
model = demo_models.get_model(0)
print("  Model type: " + str(type(model)))
face_ids = model.get_face_ids()
print("  Model Face IDs: {0:s}".format(str(face_ids)))

model_polydata = model.get_polydata() 
print("  Model polydata: num nodes: {0:d}".format(model_polydata.GetNumberOfPoints()))
print("  Model polydata: num polygons: {0:d}".format(model_polydata.GetNumberOfCells()))

face1_polydata = model.get_face_polydata(face_id=1)
face2_polydata = model.get_face_polydata(face_id=2)
face3_polydata = model.get_face_polydata(face_id=3)
print("  Model face 1 polydata: num nodes: {0:d}".format(face1_polydata.GetNumberOfPoints()))
print("  Model face 2 polydata: num nodes: {0:d}".format(face2_polydata.GetNumberOfPoints()))

## Create renderer and graphics window.
win_width = 500
win_height = 500
renderer, renderer_window = gr.init_graphics(win_width, win_height)

#add_geom(renderer, model_polydata, color=[0.5,0.5,0.5], wire=True)
gr.add_geometry(renderer, face1_polydata, color=[1.0, 0.0, 0.0], wire=False)
gr.add_geometry(renderer, face2_polydata, color=[1.0, 1.0, 0.0], wire=False)
gr.add_geometry(renderer, face3_polydata, color=[1.0, 0.0, 1.0], wire=False)

# Display window.
gr.display(renderer_window)


