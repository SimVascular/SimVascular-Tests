'''Test TetGen radius-based meshing.  

   Writes 'MODEL-radius-mesh.vtu'

   [TODO:DaveP] this is not writing out a mesh.
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

#print(dir(sv))
print(dir(sv.meshing))
print("Mesh generation kernel names: {0:s}".format(str(sv.meshing.Kernel.names)))

## Create a TetGen mesher.
#
mesher = sv.meshing.create_mesher(sv.meshing.Kernel.TETGEN)

## Load solid model into the mesher.
#  Note: must load solid before setting certain options!
#
print("Read model ... ")
model_name = "demo"
file_name = str(data_path / 'DemoProject' / 'Models' / (model_name + ".vtp"))
mesher.load_model(file_name)
print("Load model: " + file_name)

## Compute model boundary faces.
#
# If the model has faces already computed (i.e. has 'ModelFaceID' array) then
# don't call this, the face IDs will no longer match the original face IDs.
#mesher.compute_model_boundary_faces(angle=60.0)
face_ids = mesher.get_model_face_ids()
print("Mesh face info: " + str(face_ids))

# Read centerlines. 
centerlines_file = str(data_path / 'meshing' / 'demo-centerlines.vtp')
reader = vtk.vtkXMLPolyDataReader()
reader.SetFileName(centerlines_file) 
reader.Update()
centerlines = reader.GetOutput()

## Set general meshing options.
options = sv.meshing.TetGenOptions(global_edge_size=0.4, surface_mesh_flag=True, volume_mesh_flag=True)
options.optimization = 3
options.quality_ratio = 1.4
#options.use_mmg = True
options.no_bisect = True

## Set radius-based meshing options.
options.radius_meshing_centerlines = centerlines
options.radius_meshing_scale = 0.4 
options.radius_meshing_on = True

## Print options.
print("Options values: ")
[ print("  {0:s}:{1:s}".format(key,str(value))) for (key, value) in sorted(options.get_values().items()) ]

## Set wall face IDs.
face_ids = [1, 2]
mesher.set_walls(face_ids)

## Generate the mesh. 
mesher.generate_mesh(options)

## Write the mesh.
file_name = str(script_path / (model_name+'-radius-mesh.vtu'))
mesher.write_mesh(file_name)

## Get the mesh as a vtkUnstructuredGrid. 
mesh = mesher.get_mesh()
print("Mesh:");
print("  Number of nodes: {0:d}".format(mesh.GetNumberOfPoints()))
print("  Number of elements: {0:d}".format(mesh.GetNumberOfCells()))

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

