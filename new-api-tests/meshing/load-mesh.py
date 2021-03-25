'''Test load mesh methods.

   It is not clear what use it is to load a mesh. This might used for boundary layer
   meshing?
'''
import os
from pathlib import Path
import sv
import vtk
from mesh_utils import setup_mesher

## Set some directory paths. 
script_path = Path(os.path.realpath(__file__)).parent
parent_path = Path(os.path.realpath(__file__)).parent.parent
data_path = parent_path / 'data'

## Create a mesher and load a model.
mesher = setup_mesher(sv.meshing.Kernel.TETGEN)

## Load a mesh. 
file_name = str(data_path / 'meshing' / 'cylinder-mesh.vtu')
mesher.load_mesh(volume_file=file_name)

# Error test.
# mesher.load_mesh(volume_file=file_name, surface_file=file_name)

