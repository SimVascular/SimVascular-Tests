'''Test TetGen boundary layer meshing.

   Writes out 'cylinder-boundary-layer-mesh.vtu'.
'''
import sv
import sys
import vtk
sys.path.insert(1, '../graphics/')
import graphics as gr
from mesh_utils import setup_mesher

## Create a TetGen mesher.
#
mesher = sv.meshing.create_mesher(sv.meshing.Kernel.TETGEN)

## Set meshing options.
#
print("Set meshing options ... ")
options = sv.meshing.TetGenOptions(global_edge_size=0.8, surface_mesh_flag=True, volume_mesh_flag=True) 

# These are set in SV.
#
# These are now default values.
#
#options.optimization = 3
#options.quality_ratio = 1.4
#options.use_mmg = True
#options.no_bisect = True

## Load solid model into the mesher.
#  Note: must load solid before setting certain options!
#
print("Read model ... ")
mdir = "../data/meshing/"
file_name = mdir + 'cylinder-model.vtp'
mesher.load_model(file_name)

## Set the face IDs for model walls.
wall_face_ids = [1]
mesher.set_walls(wall_face_ids)

## Compute model boundary faces.
mesher.compute_model_boundary_faces(angle=60.0)
face_ids = mesher.get_model_face_ids()
print("Mesh face ids: " + str(face_ids))

## Set boundary layer meshing options
print("Set boundary layer meshing options ... ")
mesher.set_boundary_layer_options(number_of_layers=2, edge_size_fraction=0.5, layer_decreasing_ratio=0.8, constant_thickness=False)
#options.boundary_layer_inside = False
options.no_bisect = False

## Print options.
print("Options values: ")
[ print("  {0:s}:{1:s}".format(key,str(value))) for (key, value) in sorted(options.get_values().items()) ]

## Generate the mesh. 
mesher.generate_mesh(options)

## Get the mesh as a vtkUnstructuredGrid. 
mesh = mesher.get_mesh()
print("Mesh:");
print("  Number of nodes: {0:d}".format(mesh.GetNumberOfPoints()))
print("  Number of elements: {0:d}".format(mesh.GetNumberOfCells()))

## Write the mesh.
mesher.write_mesh(file_name='cylinder-boundary-layer-mesh.vtu')

## Show the mesh.
#
if True:
    win_width = 500
    win_height = 500
    renderer, renderer_window = gr.init_graphics(win_width, win_height)

    #mesh_polydata = gr.convert_ug_to_polydata(mesh)
    mesh_surface = mesher.get_surface()
    gr.add_geometry(renderer, mesh_surface, color=[1.0, 1.0, 1.0], wire=False, edges=True)
    gr.display(renderer_window)



