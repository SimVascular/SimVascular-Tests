'''Test sv.modeling.PolyData.compute_centerlines method.

   The centerlines geometry is written to 'polydata-centerlines-results.vtp'.
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

win_width = 1000
win_height = 1000
renderer, renderer_window = gr.init_graphics(win_width, win_height)

# Create a modeler.
kernel = sv.modeling.Kernel.POLYDATA
modeler = sv.modeling.Modeler(kernel)

# Read model geometry.
model_file = str(data_path / 'DemoProject' / 'Models' / 'demo.vtp')
model = modeler.read(model_file)

model_polydata = model.get_polydata()
geom = gr.add_geometry(renderer, model_polydata, color=[0.0, 1.0, 0.0], wire=False)
geom.GetProperty().SetOpacity(0.5)

# Use node or face IDs.
use_face_ids = True 
use_face_ids = False

# Use face IDs.
#
if use_face_ids:
    face_ids = model.get_face_ids()
    cap_ids = model.identify_caps()
    print("Face IDs: {0:s}".format(str(face_ids)))
    print("Caps: {0:s}".format(str(cap_ids)))
    inlet_ids = [3]
    outlet_ids = [4,5]

else:
    inlet_ids = [6952]
    outlet_ids = [242, 2705]

    points = model_polydata.GetPoints()
    pt_6952 = points.GetPoint(6952)
    gr.add_sphere(renderer, center=pt_6952, radius=0.4, color=[1.0, 1.0, 1.0], wire=False)

    pt_242 = points.GetPoint(242)
    gr.add_sphere(renderer, center=pt_242, radius=0.4, color=[1.0, 0.0, 0.0], wire=False)

    pt_2705 = points.GetPoint(2705)
    gr.add_sphere(renderer, center=pt_2705, radius=0.4, color=[1.0, 1.0, 0.0], wire=False)

# Compute centerlines.
centerlines = model.compute_centerlines(inlet_ids, outlet_ids, use_face_ids)

## Write the centerlines. 
file_name = str(script_path / 'polydata-centerlines-results.vtp')
writer = vtk.vtkXMLPolyDataWriter()
writer.SetFileName(file_name)
writer.SetInputData(centerlines)
writer.Update()
writer.Write()

print("Centerlines: num nodes: {0:d}".format(centerlines.GetNumberOfPoints()))
gr.add_geometry(renderer, centerlines, color=[1.0, 0.0, 0.0], line_width=4.0)

# Create a mouse interactor for selecting faces.
#
picking_keys = ['s']
event_table = {}
interactor = gr.init_picking(renderer_window, renderer, model_polydata, picking_keys, event_table)

# Display window.
interactor.Start()

