'''Test solid.Modeler read methods. 
'''
import sv
import vtk
import sys
sys.path.insert(1, '../graphics/')
import graphics as gr

## Create a modeler.
modeler = sv.modeling.Modeler(sv.modeling.Kernel.OPENCASCADE)
modeler = sv.modeling.Modeler(sv.modeling.Kernel.POLYDATA)

## Read a model.
print("Read modeling model file ...")
file_name = "../data/models/loft-test-interpolate.vtp"
file_name = "../data/models/cylinder.brep"
file_name = "../data/models/cylinder.stl"
model = modeler.read(file_name)
print("Model type: " + str(type(model)))

## Compute boundary faces.
face_ids = model.compute_boundary_faces(angle=60.0)
print("Model face IDs: " + str(face_ids))

## Write the model.
if False:
    file_name = "model-written"
    file_format = "vtp"
    model.write(file_name=file_name, format=file_format)

## Create renderer and graphics window.
win_width = 500
win_height = 500
renderer, renderer_window = gr.init_graphics(win_width, win_height)

## Add model polydata.
model_pd = model.get_polydata()
gr.add_geometry(renderer, model_pd, color=[0.0, 1.0, 0.0], wire=False, edges=False)

# Display window.
gr.display(renderer_window)

