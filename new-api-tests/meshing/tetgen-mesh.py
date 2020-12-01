'''Test the TetGen class interface.

   Writes: 'cylinder-mesh.vtu'

   Note: Be careful with global_edge_size, must match model Remesh Size resolution.

   Note: Loading an STL model does not work because the 'ModelFaceID' vtk array is not 
         set in compute_model_boundary_faces(). 
'''
import sv
import sys
import vtk
sys.path.insert(1, '../graphics/')
import graphics as gr

## Create a TetGen mesher.
mesher = sv.meshing.TetGen()
# or 
#mesher = sv.meshing.create_mesher(sv.meshing.Kernel.TETGEN)

## Load solid model into the mesher.
#
#  Note: must load solid before setting certain options!
#
if False:
    mdir = '../data/DemoProject/Models/'
    file_name = 'demo.vtp'
else:
    mdir = '../data/models/'
    file_name = 'cylinder.stl'

mesher.load_model(mdir+file_name)

## Compute model boundary faces.
if file_name == 'cylinder.stl':
    print("Compute boundary faces ...")
    mesher.compute_model_boundary_faces(angle=60.0)
    print("Done")

print("Get model face IDs ...")
face_ids = mesher.get_model_face_ids()
print("Mesh face ids: " + str(face_ids))

## Set the face IDs for model walls.
if file_name == 'demo.vtp':
    face_ids = [1, 2]
elif file_name == 'cylinder.stl':
    face_ids = [1]
mesher.set_walls(face_ids)

## Set meshing options.
#
# Note: Be careful with global_edge_size, must match model Remesh Size resolution.
print("Set meshing options ... ")
options = sv.meshing.TetGenOptions(global_edge_size=0.4, surface_mesh_flag=True, volume_mesh_flag=True)
#options.minimum_dihedral_angle = 10.0

## Generate the mesh. 
mesher.generate_mesh(options)

## Get the mesh as a vtkUnstructuredGrid. 
mesh = mesher.get_mesh()
print("Mesh:");
print("  Number of nodes: {0:d}".format(mesh.GetNumberOfPoints()))
print("  Number of elements: {0:d}".format(mesh.GetNumberOfCells()))

## Write the mesh.
mesher.write_mesh(file_name='cylinder-mesh.vtu')

## Show the mesh.
#
show_mesh = True
if show_mesh:
    ## Create renderer and graphics window.
    win_width = 500
    win_height = 500
    renderer, renderer_window = gr.init_graphics(win_width, win_height)

    #mesh_polydata = gr.convert_ug_to_polydata(mesh)
    mesh_surface = mesher.get_surface()
    gr.add_geometry(renderer, mesh_surface, color=[1.0, 1.0, 1.0], wire=True, edges=True)
    #gr.add_geometry(renderer, mesh_polydata, color=[1.0, 1.0, 1.0], wire=False, edges=True)

    #mesh_model_polydata = mesher.get_model_polydata()
    #gr.add_geometry(renderer, mesh_model_polydata, color=[0.0, 1.0, 1.0], wire=True, edges=True)

    face1_polydata = mesher.get_face_polydata(1)
    gr.add_geometry(renderer, face1_polydata, color=[1.0, 0.0, 0.0], wire=False, edges=True)

    face2_polydata = mesher.get_face_polydata(2)
    gr.add_geometry(renderer, face2_polydata, color=[0.0, 1.0, 0.0], wire=False, edges=True)

    face3_polydata = mesher.get_face_polydata(3)
    gr.add_geometry(renderer, face3_polydata, color=[0.0, 0.0, 1.0], wire=False, edges=True)

    gr.display(renderer_window)



