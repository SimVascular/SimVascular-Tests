'''Creating a box for testing.
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

sys.path.insert(1, '../../../graphics/')
import graphics as gr

# Create a modeler.
modeler = sv.modeling.Modeler(sv.modeling.Kernel.POLYDATA)
## Create a box.
print("Create a box ...")
center = [0.0, 0.0, 0.0]
width = 2.0 
length = 4.0 
height = 6.0
box = modeler.box(center, width=width, length=length, height=height)
print("  Box type: " + str(type(box)))
try:
    face_ids = box.get_face_ids()
except:
    face_ids = box.compute_boundary_faces(angle=60.0)
print("Face IDs: {0:s}".format(str(face_ids)))
box_pd = box.get_polydata()

cleaner = vtk.vtkCleanPolyData()
cleaner.SetInputData(box_pd);
cleaner.PieceInvariantOn();
cleaner.Update();
box_pd = cleaner.GetOutput()
box_pd.BuildLinks()

print("  Box: num nodes: {0:d}".format(box_pd.GetNumberOfPoints()))
#box.write(file_name="box", format='vtp')

length_scale = 2.0
remeshed_model = sv.mesh_utils.remesh(box_pd, hmin=length_scale, hmax=length_scale)
num_cells = remeshed_model.GetNumberOfCells()
print("Remesh number of cells: {0:d}".format(num_cells))

#writer = vtk.vtkXMLPolyDataWriter()
#writer.SetFileName(file_prefix+"-remesh-surface.vtp")
#writer.SetInputData(model_surf)
#writer.SetInputData(remeshed_model)
#writer.Update()
#writer.Write()


normals = vtk.vtkPolyDataNormals()
normals.SetInputData(box_pd)
normals.SplittingOff()
normals.ComputeCellNormalsOn()
normals.ComputePointNormalsOn()
normals.ConsistencyOn()
normals.AutoOrientNormalsOn()
normals.Update()
normals_pd = normals.GetOutput()
normals_pd.BuildLinks()

#cleaner = vtk.vtkCleanPolyData()
#cleaner.SetInputData(normals_pd);
#cleaner.Update();
#normals_pd = cleaner.GetOutput()
#normals_pd.BuildLinks()

print("  normals_pd: num nodes: {0:d}".format(normals_pd.GetNumberOfPoints()))

writer = vtk.vtkXMLPolyDataWriter()
writer.SetFileName("box.vtp")
writer.SetInputData(normals_pd)
#writer.SetInputData(box_pd)
writer.Update()
writer.Write()

writer = vtk.vtkPolyDataWriter()
writer.SetFileName("box.vtk")
writer.SetInputData(normals_pd)
writer.Update()
writer.Write()

#
## Create renderer and graphics window.
win_width = 500
win_height = 500
renderer, renderer_window = gr.init_graphics(win_width, win_height)

## Add model polydata.
gr.add_geometry(renderer, normals_pd, color=[0.0, 1.0, 0.0])
#gr.add_geometry(renderer, box_pd, color=[0.0, 1.0, 0.0])
#gr.add_geometry(renderer, box_pd, color=[0.0, 1.0, 0.0], wire=True, edges=False)

# Display window.
gr.display(renderer_window)


