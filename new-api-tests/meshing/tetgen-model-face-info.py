'''Test the TetGen class interface.

   Writes: 'cylinder-mesh.vtu'

   Note: Be careful with global_edge_size, must match model Remesh Size resolution.
'''
import sv
import sys
import vtk
sys.path.insert(1, '../graphics/')
import graphics as gr

## Create a TetGen mesher.
#
mesher = sv.meshing.TetGen()
# or 
#mesher = sv.meshing.create_mesher(sv.meshing.Kernel.TETGEN)

## Load solid model into the mesher.
#
#  Note: must load solid before setting certain options!
#
mdir = '../data//DemoProject/Models/'
file_name = 'demo.vtp'
mesher.load_model(mdir+file_name)

## Set the face IDs for model walls.
'''
face_ids = ['a']
face_ids = 1
face_ids = []
face_ids = [1]
mesher.set_walls(face_ids)
'''
if file_name == 'demo.vtp':
    face_ids = [1, 2]
elif file_name == 'cylinder-model.vtp':
    face_ids = [1]
elif file_name == 'cylinder-model.stl':
    face_ids = [1]

mesher.set_walls(face_ids)

## Compute model boundary faces.
if file_name == 'cylinder-model.stl':
    mesher.compute_model_boundary_faces(angle=60.0)
face_ids = mesher.get_model_face_ids()
print("Mesh face ids: " + str(face_ids))
print("Mesh face_ids[0]: {0:d}".format(face_ids[0]))

desc,face_info = mesher.get_model_face_info()
print("Mesh face info: " )
print("  Description: {0:s} ".format(desc))
print("  Face info: {0:s} ".format(str(face_info)))

