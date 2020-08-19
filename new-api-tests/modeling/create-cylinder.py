'''Test creating a cylinder.
'''
import sv
import sys
import vtk
sys.path.insert(1, '../graphics/')
import graphics as gr

# Create a modeler.
modeler = sv.modeling.Modeler(sv.modeling.Kernel.POLYDATA)
print("Modeler type: " + str(type(modeler)))

## Create a cylinder.
print("Create a cylinder ...")
center = [0.0, 0.0, 0.0]
axis = [0.0, 1.0, 0.0]
axis = [1.0, 0.0, 0.0]
radius = 4.0 
length = 16.0 
cylinder = modeler.cylinder(center=center, axis=axis, radius=radius, length=length)
print("  Cylinder type: " + str(type(cylinder)))
#
cylinder.compute_boundary_faces(angle=60.0)

cylinder_pd = cylinder.get_polydata()
print("  Cylinder: num nodes: {0:d}".format(cylinder_pd.GetNumberOfPoints()))

## Write the model.
file_name = "cylinder-model-write"
file_format = "vtp"
cylinder.write(file_name=file_name, format=file_format)

## Create renderer and graphics window.
win_width = 500
win_height = 500
renderer, renderer_window = gr.init_graphics(win_width, win_height)

## Add model polydata.
gr.add_geometry(renderer, cylinder_pd, color=[0.0, 1.0, 0.0], wire=True, edges=False)

## Add a sphere.
gr.add_sphere(renderer, center=center, radius=0.1, color=[1.0, 1.0, 1.0], wire=True)

pt1 = center
pt2 = [ center[i] + length/2.0 * axis[i] for i in range(3) ]
gr.add_line(renderer, pt1, pt2, color=[0.5, 0.0, 0.0], width=4)

# Display window.
gr.display(renderer_window)



