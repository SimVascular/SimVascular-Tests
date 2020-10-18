'''Test creating a Parasolid model.
'''
import sv
import sys
import vtk
sys.path.insert(1, '../graphics/')
import graphics as gr

## Create a modeler.
kernel = sv.modeling.Kernel.PARASOLID
modeler = sv.modeling.Modeler(kernel)

## Create a cylinder.
print("Create a cylinder.") 
center = [0.0, 0.0, 0.0]
axis = [0.0, 0.0, 1.0]
radius = 1.5
length = 10.0
cyl = modeler.cylinder(center, axis, radius, length)
face_ids = cyl.get_face_ids()
print("Model face IDs: " + str(face_ids))

## Write the model.
cyl.write(file_name="cylinder-parasolid") 

## Create renderer and graphics window.
win_width = 500
win_height = 500
renderer, renderer_window = gr.init_graphics(win_width, win_height)

## Add model polydata.
polydata = cyl.get_polydata() 
gr.add_geometry(renderer, polydata, color=[1.0, 0.0, 0.0], wire=False, edges=True)

# Display window.
gr.display(renderer_window)



