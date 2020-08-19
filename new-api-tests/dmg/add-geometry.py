'''Test adding geometry to the SV Data Manager.

   This is tested using the Demo Project.
'''
from pathlib import Path
import sv
import vtk 

## Get path object from the SV Data Manager 'Paths/aorta' node. 
#
path_name = "aorta"
path = sv.dmg.get_path(path_name)
control_points = path.get_control_points()
num_control_points = len(control_points)
print("Get '{0:s}' path.".format(path_name))
print("Number of control points: {0:d}".format(num_control_points))

## Create a sphere. 
#
pt_index = int(num_control_points/2)
point = control_points[pt_index]
print("Point index: {0:d}".format(pt_index))
print("Point: {0:s}".format(str(point)))
sphere = vtk.vtkSphereSource()
sphere.SetCenter(point[0], point[1], point[2])
sphere.SetRadius(1.0)
sphere.Update()
sphere_pd = sphere.GetOutput()

## Add the sphere polydata object under the SV Data Manager 
#  'Paths/aorta' node as a new  node named 'aorta_sphere'.
#
sv.dmg.add_geometry(name="aorta_sphere", geometry=sphere_pd, plugin="Path", node=path_name)

