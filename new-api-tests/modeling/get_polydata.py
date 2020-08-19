'''Test getting model polydata. 
'''
import sv
import sys
import vtk
sys.path.insert(1, '../graphics/')
import graphics as gr

## Create a modeler.
modeler = None
if len(sys.argv) == 2:
    if sys.argv[1] == 'o':
        modeler = sv.modeling.Modeler(sv.modeling.Kernel.OPENCASCADE)
        print("Create OPENCASCADE modeler")
    elif sys.argv[1] == 'p':
        modeler = sv.modeling.Modeler(sv.modeling.Kernel.PARASOLID)
        print("Create PARASOLID modeler")

if modeler == None:
    modeler = sv.modeling.Modeler(sv.modeling.Kernel.POLYDATA)
    print("Create POLYDATA modeler")

## Create a cylinder.
print("Create a cylinder ...")
center = [0.0, 0.0, 0.0]
axis = [0.0, 1.0, 0.0]
axis = [1.0, 0.0, 0.0]
radius = 2.0 
length = 4.0 
model = modeler.cylinder(center=center, axis=axis, radius=radius, length=length)
#
model.compute_boundary_faces(angle=60.0)
face_ids = model.get_face_ids()
print("Model Face IDs: {0:s}".format(str(face_ids)))
#
## Create renderer and graphics window.
win_width = 500
win_height = 500
renderer, renderer_window = gr.init_graphics(win_width, win_height)

## Add model polydata.
model_pd = model.get_polydata()
gr.add_geometry(renderer, model_pd, color=[0.0, 1.0, 0.0], wire=True, edges=False)

# Display window.
gr.display(renderer_window)

