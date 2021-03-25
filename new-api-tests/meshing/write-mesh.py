'''
Test writing a mesh.

'''
import os
from pathlib import Path
import sv
import sys
import vtk
from mesh_utils import setup_mesher

## Set some directory paths. 
script_path = Path(os.path.realpath(__file__)).parent
parent_path = Path(os.path.realpath(__file__)).parent.parent
data_path = parent_path / 'data'

## Create a mesher and load a model.
mesher = setup_mesher(sv.meshing.Kernel.TETGEN)

## Load a mesh. 
file_name = str(script_path / 'cylinder-mesh.vtu')
mesher.load_mesh(file_name)

## Write the mesh. 
file_name = str(script_path / 'cylinder-mesh-tmp.vtu')
mesher.write_mesh(file_name)

