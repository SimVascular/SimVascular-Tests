'''Test adding a mesh to the SV Data Manager.

   This is tested using the Demo Project.
'''
import os
from pathlib import Path
import sv
import sys
import vtk

## Set some directory paths. 
script_path = Path(os.path.realpath(__file__)).parent
parent_path = Path(os.path.realpath(__file__)).parent.parent
data_path = parent_path / 'data'

## Read a mesh. 
#
home = str(Path.home())
file_name = home + "/SimVascular/DemoProject/Meshes/demo.vtu"
reader = vtk.vtkXMLUnstructuredGridReader()
reader.SetFileName(file_name)
reader.Update()
volume_mesh = reader.GetOutput()
print("Mesh: ");
print("  Number of nodes: {0:d}".format(mesh.GetNumberOfPoints()))
print("  Number of elements: {0:d}".format(mesh.GetNumberOfCells()))

## Read a model
modeler = sv.modeling.Modeler(sv.modeling.Kernel.POLYDATA)
file_name = str(data_path / 'DemoProject' / 'Models' / 'demo.vtp')
model = modeler.read(file_name)
model_surface = model.get_polydata()

## Add a vtk unstructure mesh object under the SV Data Manager 'Meshes' node
#  as a new  node named 'new_demo'.
#
try:
    sv.dmg.add_mesh(name="new_demo", volume=volume_mesh, surface=model_surface, model="demo")
except Exception as inst:
    print("Exception")
    print(inst)

