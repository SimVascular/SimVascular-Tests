'''Test generating a mesh from a model in the SV Data Manager.
  
   This is tested using the Cylinder Project.
'''
import sv
import vtk

# Get cylinder model.
cylinder = sv.dmg.get_model("cylinder")

# Create mesher.
mesher = sv.meshing.create_mesher(sv.meshing.Kernel.TETGEN)
mesher.set_model(cylinder)
options = sv.meshing.TetGenOptions(global_edge_size=0.4, surface_mesh_flag=True, volume_mesh_flag=True)

# Set the face IDs for model walls.
face_ids = [1]
mesher.set_walls(face_ids)
#mesher.set_walls(mesher.get_model_face_ids())

# Generate mesh.
mesher.generate_mesh(options)

# Get the volume and surface meshes. 
volume_mesh = mesher.get_mesh()
surface_mesh = mesher.get_surface()
print("Mesh:");
print("  Number of nodes: {0:d}".format(volume_mesh.GetNumberOfPoints()))
print("  Number of elements: {0:d}".format(volume_mesh.GetNumberOfCells()))

# Add an SV Mesh Node.
sv.dmg.add_mesh(name="python-mesh", volume=volume_mesh, surface=surface_mesh, model="cylinder")

