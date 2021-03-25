'''This script tests reading in an SV Mesh from an .msh file.
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
demo_project = True
if demo_project:
    project_name = "DemoProject"
    mesh_name = "demo-sphere-refine"
    mesh_name = "demo-local-edge-and-sphere"
    mesh_name = "demo-local-edge-and-radius" 
    mesh_name = "demo-refine-all"
    mesh_name = "demo"

## Read an SV mesh .msh file. 
#
file_name = str(data_path / project_name / 'Meshes' / str( mesh_name + ".msh"))
print("Read SV msh file: {0:s}".format(file_name))
mesh_series = sv.meshing.Series(file_name)
num_times = mesh_series.get_num_times()
print("Number of meshes: {0:d}".format(num_times))

## Get a mesh for time 0.
#
# Meshing parameter options are read from the .msh file.
#
mesher, options = mesh_series.get_mesh(0)
face_ids = mesher.get_model_face_ids()
print("Mesh face IDs: " + str(face_ids))

## Set options.
#options.mesh_wall_first = True
#options.radius_meshing_compute_centerlines = True

## Print options.
print("Options ... ")
[ print("  {0:s}:{1:s}".format(key,str(value))) for (key, value) in sorted(options.get_values().items()) ]

## Set wall face IDs.
if demo_project:
    face_ids = [1, 2]
else:
    face_ids = [1]
mesher.set_walls(face_ids)

## Generate the mesh. 
mesher.generate_mesh(options)

## Write the mesh.
#mesher.write_mesh(file_name=mesh_name+'.vtu')

#mesh_surface = mesher.get_surface()
#print("Number of surface mesh nodes: {0:d}".format(mesh_surface.GetNumberOfPoints()))

#mesh_model_polydata = mesher.get_model_polydata()
#print("Number of volume mesh nodes: {0:d}".format(mesh_model_polydata.GetNumberOfPoints()))

#face1_polydata = mesher.get_face_polydata(1)
#print("Face 1 number of nodes: {0:d}".format(face1_polydata.GetNumberOfPoints()))
#gr.add_geom(renderer, face1_polydata, color=[1.0, 0.0, 0.0], wire=False, edges=True)

#display(renderer_win)

