'''Test the subtract Boolean operation.
'''
import sv
import sys
import vtk
sys.path.insert(1, '../graphics/')
import graphics as gr

# Create a modeler.
#modeler = sv.modeling.Modeler(sv.modeling.Kernel.OPENCASCADE)
modeler = sv.modeling.Modeler(sv.modeling.Kernel.POLYDATA)

## Create a box.
print("Create a box ...")
center = [0.0, 0.0, 0.0]
box = modeler.box(center, length=6.0, height=6.0, width=6.0)
print("  Box type: " + str(type(box)))
box_pd = box.get_polydata()
print("  Box: num nodes: {0:d}".format(box_pd.GetNumberOfPoints()))

## Create a cylinder.
print("Create a cylinder ...") 
center = [0.0, 0.0, -3.0]
axis = [0.0, 0.0, 1.0]
radius = 1.5
length = 10.0
cylinder = modeler.cylinder(center, axis, radius, length)
print("  Cylinder type: " + str(type(cylinder)))
cylinder_pd = cylinder.get_polydata() 
print("  Cylinder: num nodes: {0:d}".format(cylinder_pd.GetNumberOfPoints()))
#
## Create a smaller cylinder.
radius = 0.5
center = [0.0, 0.0, 0.0]
cylinder_small = modeler.cylinder(center, axis, radius, length)

## Subtract the cylinder from the box.
print("Subtract cylinder from box ...")
result = modeler.subtract(main=box, subtract=cylinder)

## Subtract the cylinder from the smaller cylinder.
#result = modeler.subtract(main=cylinder, subtract=cylinder_small)

print("  Subtract result type: " + str(type(result)))
result_pd = result.get_polydata()
print("  Subtract result: num nodes: {0:d}".format(result_pd.GetNumberOfPoints()))

## Write the model.
file_name = "box-minus-cylinder-partial"
file_format = "vtp"
result.write(file_name=file_name, format=file_format)

## Create renderer and graphics window.
win_width = 500
win_height = 500
renderer, renderer_window = gr.init_graphics(win_width, win_height)

## Add model polydata.
gr.add_geometry(renderer, box_pd, color=[0.0, 1.0, 0.0], wire=True, edges=False)
gr.add_geometry(renderer, cylinder_pd, color=[0.0, 0.0, 1.0], wire=True, edges=False)
gr.add_geometry(renderer, result_pd, color=[1.0, 0.0, 0.0], wire=False, edges=False)

# Display window.
gr.display(renderer_window)

