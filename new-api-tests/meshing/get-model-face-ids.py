'''Test getting mesh model face ids.
'''
import sv
import sys
import vtk
from mesh_utils import setup_mesher

## Create a mesher and load a model.
mesher = setup_mesher(sv.meshing.Kernel.TETGEN)

## Get the face IDs for model walls.
#face_ids = [1, 2]
#mesher.set_walls(face_ids)

## Compute model boundary faces.
#
#mesher.compute_model_boundary_faces(angle=60.0)
face_ids = mesher.get_model_face_ids()
print("Mesh model face ids: " + str(face_ids))

