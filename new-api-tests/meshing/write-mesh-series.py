'''This scipt tests writing an SV Mesh group to a .msh file.

   Write: 'MESH-test.msh'
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

try:
    sys.path.insert(1, str(parent_path / 'graphics'))
    import graphics as gr
except:
    print("Can't find the new-api-tests/graphics package.")

## Demo project tests.
if True:
    project_name = "DemoProject"
    mesh_name = "demo-sphere-refine"
    mesh_name = "demo-local-edge-and-sphere"
    mesh_name = "demo-local-edge-and-radius" 
    mesh_name = "demo-refine-all"
    mesh_name = "demo"

# CylinderProject tests.
else:
    project_name = "CylinderProject"
    mesh_name = "cylinder"

## Read an SV mesh group file. 
#
file_name = str(data_path / project_name / 'Meshes' / (mesh_name + ".msh"))
print("Read SV msh file: {0:s}".format(file_name))
mesh_group = sv.meshing.Series(file_name)
num_meshes = mesh_group.get_num_times()
print("Number of meshes: {0:d}".format(num_meshes))

## Write a mesh group.
file_name = str(script_path / (mesh_name + "-test.msh"))
mesh_group.write(file_name)

