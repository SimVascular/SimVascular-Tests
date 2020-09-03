'''Test TetGen sphere refinement. 

   [TODO:DaveP] this is broken.
'''
from pathlib import Path
import sv
import sys
import vtk
sys.path.insert(1, '../graphics/')
import graphics as gr

#print(dir(sv))
print(dir(sv.meshing))
print("Mesh generation kernel names: {0:s}".format(str(sv.meshing.Kernel.names)))

## Create a TetGen mesher.
#
mesher = sv.meshing.create_mesher(sv.meshing.Kernel.TETGEN)
print("Mesher: " + str(mesher))

## Load solid model into the mesher.
#  Note: must load solid before setting certain options!
#
print("Read model ... ")
model_name = "demo"
file_name = "../data/DemoProject/Models/" + model_name + ".vtp"
mesher.load_model(file_name)
print("Load model: " + file_name)

## Compute model boundary faces.
#
# If the model has faces already computed (i.e. has 'ModelFaceID' array) then
# don't call this, the face IDs will no longer match the original face IDs.
#mesher.compute_model_boundary_faces(angle=60.0)
face_ids = mesher.get_model_face_ids()
print("Mesh face info: " + str(face_ids))

## Set meshing options.
options = sv.meshing.TetGenOptions(global_edge_size=0.4, surface_mesh_flag=True, volume_mesh_flag=True)
options.optimization = 3
options.quality_ratio = 1.4
options.use_mmg = True
options.no_bisect = True

## Set sphere refinement options.
#
radius = 3.74711
center = [1.41902, -1.04231, 0.0785005]

sphere1 = { 'edge_size':0.2, 'radius':radius,  'center':center }
options.sphere_refinement.append( sphere1 ) 
options.sphere_refinement_on = True 

# Check errors.
#sphere2 = { 'bedge_size':0.2, 'radius':3.74711,  'center':[1.41902, -1.04231, 0.0785005] }
#sphere2 = { 'edge_size':0.2, 'radius':3.74711,  'center':[1.41902] }
#sphere2 = { 'edge_size':0.2, 'radius':'a',  'center':[1.41902, -1.04231, 0.0785005] }
#options.sphere_refinement.append( sphere2 ) 

## Print options.
print("Options values: ")
[ print("  {0:s}:{1:s}".format(key,str(value))) for (key, value) in sorted(options.get_values().items()) ]

## Set wall face IDs.
face_ids = [1, 2]
mesher.set_walls(face_ids)

## Generate the mesh. 
mesher.generate_mesh(options)

## Write the mesh.
mesher.write_mesh(file_name=model_name+'-sphere-refine-mesh.vtu')

## Get the mesh as a vtkUnstructuredGrid. 
mesh = mesher.get_mesh()
print("Mesh:");
print("  Number of nodes: {0:d}".format(mesh.GetNumberOfPoints()))
print("  Number of elements: {0:d}".format(mesh.GetNumberOfCells()))

## Show the mesh.
#
show_mesh = True
if show_mesh:
    win_width = 500
    win_height = 500
    renderer, renderer_window = gr.init_graphics(win_width, win_height)

    #mesh_polydata = gr.convert_ug_to_polydata(mesh)
    mesh_surface = mesher.get_surface()
    gr.add_geometry(renderer, mesh_surface, color=[1.0, 1.0, 1.0], wire=False, edges=True)

    gr.add_sphere(renderer, center, radius, color=[0,1,0], wire=True)

    gr.display(renderer_window)

