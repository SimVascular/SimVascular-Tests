'''Test getting a mesh from the SV Data Manager.

   This is tested using the Demo Project.
'''

import sv
import vtk
  
## Create a Python mesh object from the SV Data Manager 'Meshes/demo' node. 
#
mesh_name = "demo"
mesh = sv.dmg.get_mesh(mesh_name)
print("Mesh: ");
print("  Number of nodes: {0:d}".format(mesh.GetNumberOfPoints()))
print("  Number of elements: {0:d}".format(mesh.GetNumberOfCells()))

