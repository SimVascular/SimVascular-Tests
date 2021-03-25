'''Test the TetGen class interface.

   Writes: 'cylinder-mesh.vtu'

   Note: Be careful with global_edge_size, must match model Remesh Size resolution.
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

## Create a TetGen mesher.
#
mesher = sv.meshing.TetGen()
# or 
#mesher = sv.meshing.create_mesher(sv.meshing.Kernel.TETGEN)

## Load solid model into the mesher.
#
#  Note: must load solid before setting certain options!
#
file_name = str(data_path / 'DemoProject' / 'Models' / 'demo.vtp')
mesher.load_model(file_name)

## Set the face IDs for model walls.
'''
face_ids = ['a']
face_ids = 1
face_ids = []
face_ids = [1]
mesher.set_walls(face_ids)
'''
if 'demo.vtp' in file_name:
    face_ids = [1, 2]
elif 'cylinder-model.vtp' in file_name:
    face_ids = [1]
elif 'cylinder-model.stl' in file_name:
    face_ids = [1]

mesher.set_walls(face_ids)

## Compute model boundary faces.
if 'cylinder-model.stl' in file_name:
    mesher.compute_model_boundary_faces(angle=60.0)
face_ids = mesher.get_model_face_ids()
print("Mesh face ids: " + str(face_ids))
print("Mesh face_ids[0]: {0:d}".format(face_ids[0]))

face_info = mesher.get_model_face_info()
print("Mesh face info: " )
print("  Face info: {0:s} ".format(str(face_info)))

