'''
Test writing a mesh.

'''
import sv
import vtk
from mesh_utils import setup_mesher

## Create a mesher and load a model.
mesher = setup_mesher(sv.meshing.Kernel.TETGEN)

## Load a mesh. 
file_name = 'cylinder-mesh.vtu'
mesher.load_mesh(file_name)

## Write the mesh. 
file_name = 'cylinder-mesh-tmp.vtu'
mesher.write_mesh(file_name)

