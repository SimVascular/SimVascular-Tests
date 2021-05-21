'''Test remeshing a POLYDATA model faces. 
'''
from math import sqrt
import os
from pathlib import Path
import sv
import sys
import vtk

def compute_scale(surface):
    '''Compute a length scale for a vtkPolyData surface.
    '''
    num_cells = surface.GetNumberOfCells()
    points = surface.GetPoints()
    min_area = 1e6
    max_area = -1e6
    avg_area = 0.0

    for i in range(num_cells):
        cell = surface.GetCell(i)
        cell_pids = cell.GetPointIds()
        pid1 = cell_pids.GetId(0)
        pt1 = points.GetPoint(pid1)
        pid2 = cell_pids.GetId(1)
        pt2 = points.GetPoint(pid2)
        pid3 = cell_pids.GetId(2)
        pt3 = points.GetPoint(pid3)

        area = vtk.vtkTriangle.TriangleArea(pt1, pt2, pt3)
        avg_area += area

        if area < min_area:
            min_area = area
        elif area > max_area:
            max_area = area
    #_for i in range(num_cells)

    avg_area /= num_cells
    length_scale = sqrt(2.0 * avg_area)
    return length_scale 

## Set some directory paths. 
script_path = Path(os.path.realpath(__file__)).parent
parent_path = Path(os.path.realpath(__file__)).parent.parent
data_path = parent_path / 'data'
try:
    sys.path.insert(1, str(parent_path / 'graphics'))
    import graphics as gr
except:
    print("Can't find the new-api-tests/graphics package.")

## Create a modeler.
kernel = sv.modeling.Kernel.POLYDATA 
modeler = sv.modeling.Modeler(kernel)

## Create a cylinder.
print("Create a cylinder ...")
center = [0.0, 0.0, 0.0]
axis = [0.0, 1.0, 0.0]
axis = [1.0, 0.0, 0.0]
radius = 1.0
length = 6.0
model = modeler.cylinder(center=center, axis=axis, radius=radius, length=length)
model.compute_boundary_faces(angle=60.0)

## Create renderer and graphics window.
win_width = 500
win_height = 500
renderer, renderer_window = gr.init_graphics(win_width, win_height)

## Get model polydata.
model_pd = model.get_polydata()
num_cells = model_pd.GetNumberOfCells()
print('Number of model polygons: {0:d}'.format(num_cells))
model_pd_copy = vtk.vtkPolyData()
model_pd_copy.DeepCopy(model_pd)
gr.add_geometry(renderer, model_pd_copy, color=[0.0, 0.6, 0.0], wire=True, line_width=6)
length_scale = compute_scale(model_pd)
print('Length scale: {0:g}'.format(length_scale))

## Remsh the model.
msize = length_scale / 4.0
print('Remesh size: {0:g}'.format(msize))
face_ids = [3]
remeshed_model = sv.mesh_utils.remesh_faces(model_pd, face_ids, edge_size=msize)
num_cells = remeshed_model.GetNumberOfCells()
print('Number of remeshed model polygons: {0:d}'.format(num_cells))
#gr.add_geometry(renderer, remeshed_model, color=[0.8, 0.8, 0.8])
#gr.add_geometry(renderer, remeshed_model, color=[0.8, 0.8, 0.8], edges=True)
gr.add_geometry(renderer, remeshed_model, color=[0.8, 0.8, 0.8], wire=True)

## Create a model from the remeshed surface.
model = sv.modeling.PolyData(surface=remeshed_model)
face_ids = model.compute_boundary_faces(angle=60.0)
print("Model face IDs: " + str(face_ids))

## Create a TetGen mesher.
mesher = sv.meshing.TetGen()
mesher.set_model(model)
face_ids = mesher.get_model_face_ids()
print("Mesh face ids: " + str(face_ids))

## Set mesher the wall face IDs.
face_ids = [1]
mesher.set_walls(face_ids)

# Set meshing options.
options = sv.meshing.TetGenOptions(global_edge_size=msize, surface_mesh_flag=True, volume_mesh_flag=True)

# Generate the mesh.
mesher.generate_mesh(options)
mesh = mesher.get_mesh()
print("Mesh:");
print("  Number of nodes: {0:d}".format(mesh.GetNumberOfPoints()))
print("  Number of elements: {0:d}".format(mesh.GetNumberOfCells()))
mesh_surface = mesher.get_surface()
gr.add_geometry(renderer, mesh_surface, color=[1.0, 0.0, 0.0], edges=True)

## Create a mouse interactor for selecting faces.
picking_keys = ['s']
event_table = {}
interactor = gr.init_picking(renderer_window, renderer, model_pd, picking_keys, event_table)

## Display window.
interactor.Start()

