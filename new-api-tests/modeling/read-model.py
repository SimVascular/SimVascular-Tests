'''Test solid.Modeler read methods. 
'''
import sv
import vtk
import sys
sys.path.insert(1, '../graphics/')
import graphics as gr

## Create a modeler.
#
kernel = sv.modeling.Kernel.OPENCASCADE
kernel = sv.modeling.Kernel.PARASOLID 
kernel = sv.modeling.Kernel.POLYDATA 

modeler = sv.modeling.Modeler(kernel)

## Read a model.
#
print("Read modeling model file ...")

if kernel == sv.modeling.Kernel.PARASOLID:
    file_name = "../data/meshing/aorta-iliac.xmt_txt"
elif kernel == sv.modeling.Kernel.OPENCASCADE: 
    file_name = "../data/models/cylinder.brep"
else:
    file_name = "../data/DemoProject/Models/demo.vtp"
    file_name = "../data/models/cylinder.stl"

model = modeler.read(file_name)
print("Model type: " + str(type(model)))

## Compute boundary faces if needed.
#
try:
    face_ids = model.get_face_ids()
except:
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
gr.add_geometry(renderer, model_pd, color=[0.0, 1.0, 0.0], wire=True, edges=False)

face1_polydata = model.get_face_polydata(face_id=face_ids[0])
gr.add_geometry(renderer, face1_polydata, color=[1.0, 0.0, 0.0], wire=False)


# Display window.
gr.display(renderer_window)

