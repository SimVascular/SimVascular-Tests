'''Test classifying a point. 
'''
import sv
import sys
import vtk
sys.path.insert(1, '../graphics/')
import graphics as gr

win_width = 500
win_height = 500
renderer, renderer_window = gr.init_graphics(win_width, win_height)

## Create a modeler.
#
kernel = sv.modeling.Kernel.POLYDATA
modeler = sv.modeling.Modeler(kernel)

## Create a cylinder.
#
print("Create a cylinder.")
center = [0.0, 0.0, 0.0]
axis = [0.0, 0.0, 1.0]
radius = 1.5
length = 10.0
cylinder = modeler.cylinder(center, axis, radius, length)
cylinder_polydata = cylinder.get_polydata()

#----------
# classify
#----------
tol = 1e-6
point = [0.0, 0.0, 0.0]
point = [1.2, 0.0, 0.0]
point = [1.5, 0.0, 0.0]
point = [1.5-tol, 0.0, 0.0]
result = sv.geometry.point_inside(cylinder_polydata, point)
print("Classify point result: " + str(result))

sphere = vtk.vtkSphereSource()
sphere.SetCenter(point[0], point[1], point[2])
sphere.SetRadius(0.2)
sphere.Update()
sphere_pd = sphere.GetOutput()
gr.add_geometry(renderer, sphere_pd, color=[1.0, 1.0, 1.0])
#result = sv.geometry.classify_point(sphere, point)

## Show geometry.
#
gr.add_geometry(renderer, cylinder_polydata, color=[1.0,0.0,0.0], wire=True)
gr.display(renderer_window)

