'''Test creating a POLYDATA model without importing vtk.
'''
import sv
import sys

## Create a modeler.
kernel = sv.modeling.Kernel.POLYDATA 
modeler = sv.modeling.Modeler(kernel)

## Create a cylinder.
print("Create a cylinder.") 
center = [0.0, 0.0, 0.0]
axis = [0.0, 0.0, 1.0]
radius = 1.5
length = 10.0
cyl = modeler.cylinder(center, axis, radius, length)
polydata = cyl.get_polydata() 


