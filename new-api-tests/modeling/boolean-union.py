'''Test the union Boolean operation.
'''
import sv
import sys
import vtk
sys.path.insert(1, '../graphics/')
import graphics as gr

# Create a modeler.
#oc_modeler = sv.modeling.Modeler(sv.modeling.Kernel.OPENCASCADE)
modeler = sv.modeling.Modeler(sv.modeling.Kernel.POLYDATA)
#modeler = sv.modeling.Modeler(sv.modeling.Kernel.POLYDATA)
print("sv.modeling.Kernel.POLYDATA: {0:s}".format(sv.modeling.Kernel.POLYDATA))

## Create a box.
print("Create a box ...")
center = [0.0, 0.0, 0.0]
box = modeler.box(center, length=6.0, height=6.0, width=6.0)
#box = oc_modeler.box(center, length=6.0, height=6.0, width=6.0)
print("  Box type: " + str(type(box)))
box_pd = box.get_polydata()
print("  Box: num nodes: {0:d}".format(box_pd.GetNumberOfPoints()))

## Create a cylinder.
print("Create a cylinder ...") 
center = [0.0, 0.0, 1.0]
axis = [0.0, 0.0, 1.0]
radius = 1.5
length = 10.0
cylinder = modeler.cylinder(center, axis, radius, length)
cylinder_pd = cylinder.get_polydata() 

## Subtract the cylinder from the box.
print("Union the cylinder and the box ...")
result = modeler.union(model1=box, model2=cylinder)
result_pd = result.get_polydata()

## Create renderer and graphics window.
win_width = 500
win_height = 500
renderer, renderer_window = gr.init_graphics(win_width, win_height)

## Add model polydata.
#gr.add_geometry(renderer, box_pd, color=[0.0, 1.0, 0.0], wire=True, edges=False)
#gr.add_geometry(renderer, cylinder_pd, color=[0.0, 0.0, 1.0], wire=True, edges=False)
gr.add_geometry(renderer, result_pd, color=[1.0, 0.0, 0.0], wire=True, edges=False)

# Display window.
gr.display(renderer_window)

