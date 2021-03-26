'''Test meshing a surface from a .vtk file with no ModelFaceID array.

   Usage:

      mesh-vtk-surf.py FILE_NAME.vtk

  Writes out FILE_NAME.vtu mesh file.
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

if len(sys.argv) != 2:
    print("Must give the name of a .vtk file")
    sys.exit(1)

file_name = sys.argv[1]
file_prefix = os.path.splitext(file_name)[0]

# Create a model and compute faces.
modeler = sv.modeling.Modeler(sv.modeling.Kernel.POLYDATA)
model = modeler.read(file_name)
face_ids = model.compute_boundary_faces(angle=60.0)
print("Model face IDs: " + str(face_ids))

# Create a TetGen mesher.
mesher = sv.meshing.TetGen()

# Set the model for the mesher.
mesher.set_model(model)

# Set meshing options.
print("Set meshing options ... ")
options = sv.meshing.TetGenOptions(global_edge_size=0.2, surface_mesh_flag=True, volume_mesh_flag=True)

# Generate the mesh. 
mesher.set_walls(face_ids)
mesher.generate_mesh(options)

# Get the mesh as a vtkUnstructuredGrid. 
mesh = mesher.get_mesh()
print("Mesh:");
print("  Number of nodes: {0:d}".format(mesh.GetNumberOfPoints()))
print("  Number of elements: {0:d}".format(mesh.GetNumberOfCells()))

# Write the mesh.
mesh_file = script_path / (file_prefix+'.vtu')
mesher.write_mesh(file_name=str(mesh_file))

## Create renderer and graphics window.
win_width = 500
win_height = 500
renderer, renderer_window = gr.init_graphics(win_width, win_height)

## Add model polydata.
model_pd = model.get_polydata()
#gr.add_geometry(renderer, model_pd, color=[0.0, 0.6, 0.0], wire=True, line_width=1)

# Add mesh surface.
mesh_surface = mesher.get_surface()
gr.add_geometry(renderer, mesh_surface, color=[1.0, 1.0, 1.0], wire=False, edges=True)

# Display window.
gr.display(renderer_window)


