'''This script demonstrates checking a POLYDATA model. 
'''
import sv
import vtk

import os
from pathlib import Path
import sv
import sys
import vtk

def compute_triangle_areas(surface):
    '''Compute the surface triangle areas.
    '''
    num_cells = surface.GetNumberOfCells()
    points = surface.GetPoints()
    min_area = 1e6
    max_area = -1e6
    avg_area = 0.0

    cell_areas = vtk.vtkDoubleArray()
    cell_areas.SetName("cell_areas")
    cell_areas.SetNumberOfComponents(1)
    cell_areas.SetNumberOfTuples(num_cells)

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
        cell_areas.SetValue(i, area)

        avg_area += area

        if area < min_area:
            min_area = area
        elif area > max_area:
            max_area = area

    return cell_areas, min_area, max_area

def extract_edges(surface):
    '''Extract the surface boundary edges.

       For a closed surface the number of boundary edges = 0.
    '''
    print("========== extract edges ========== ")
    angle = 50.0

    feature_edges = vtk.vtkFeatureEdges()
    feature_edges.SetInputData(surface)
    feature_edges.BoundaryEdgesOn();
    #feature_edges.BoundaryEdgesOff();
    feature_edges.ManifoldEdgesOff();
    feature_edges.NonManifoldEdgesOff();
    feature_edges.FeatureEdgesOff();
    #feature_edges.FeatureEdgesOn();
    #feature_edges.SetFeatureAngle(angle);
    feature_edges.Update()

    boundary_edges = feature_edges.GetOutput()
    clean_filter = vtk.vtkCleanPolyData()
    boundary_edges_clean = clean_filter.SetInputData(boundary_edges)
    clean_filter.Update();
    cleaned_edges = clean_filter.GetOutput()

    conn_filter = vtk.vtkPolyDataConnectivityFilter()
    conn_filter.SetInputData(cleaned_edges)
    conn_filter.SetExtractionModeToSpecifiedRegions()

    boundary_edges = []
    rid = 1
    while True:
        conn_filter.AddSpecifiedRegion(rid)
        conn_filter.Update()
        component = vtk.vtkPolyData()
        component.DeepCopy(conn_filter.GetOutput())
        if component.GetNumberOfCells() <= 0:
            break
        boundary_edges.append(component)
        conn_filter.DeleteSpecifiedRegion(rid)
        rid += 1

    print("Number of boundary edges: {0:d}".format(len(boundary_edges)))
    return boundary_edges

# Set some directory paths. 
script_path = Path(os.path.realpath(__file__)).parent
parent_path = Path(os.path.realpath(__file__)).parent.parent
data_path = parent_path / 'data'

try:
    sys.path.insert(1, str(parent_path / 'graphics'))
    import graphics as gr
except:
    print("Can't find the new-api-tests/graphics package.")

# Create renderer and graphics window.
win_width = 500
win_height = 500
renderer, renderer_window = gr.init_graphics(win_width, win_height)

# Create a modeler.
kernel = sv.modeling.Kernel.POLYDATA
modeler = sv.modeling.Modeler(kernel)

# Read a model.
print("Read modeling model file ...")
file_name = str(data_path / 'DemoProject' / 'Models' / 'demo.vtp')
model = modeler.read(file_name)
print("Model type: " + str(type(model)))

# Compute boundary faces if needed.
try:
    face_ids = model.get_face_ids()
except:
    face_ids = model.compute_boundary_faces(angle=60.0)
print("Model face IDs: " + str(face_ids))
min_face_id = min(face_ids)
max_face_id = max(face_ids)

# Get model polydata.
model_surface = model.get_polydata()

# Extract edges.
model_edges = extract_edges(model_surface)
for edge in model_edges:
    gr.add_geometry(renderer, edge, color=[1,1,1], wire=False, line_width=4)

# Compute cell areas.
cell_areas, min_area, max_area = compute_triangle_areas(model_surface)
area_range = [min_area, max_area]
model_surface.GetCellData().SetScalars(cell_areas)

# Show surface cells colored by area.
area_lut = vtk.vtkLookupTable()
area_lut.SetTableRange(max_area, min_area)
area_lut.SetHueRange(0,1)
#area_lut.SetHueRange(0.667,0.0)
area_lut.SetSaturationRange(1, 1)
area_lut.SetValueRange(1, 1)
area_lut.Build()

mapper = vtk.vtkPolyDataMapper()
mapper.SetInputData(model_surface)
mapper.SetScalarVisibility(True)
mapper.SetScalarModeToUseCellFieldData()
mapper.SetScalarRange(area_range)
mapper.SetScalarModeToUseCellData()
mapper.SetLookupTable(area_lut)

actor = vtk.vtkActor()
actor.SetMapper(mapper)
actor.GetProperty().EdgeVisibilityOn();
renderer.AddActor(actor)

'''
# Show faces.
lut = vtk.vtkLookupTable()
lut.SetTableRange(min_face_id, max_face_id+1)
lut.SetHueRange(0, 1)
lut.SetSaturationRange(1, 1)
lut.SetValueRange(1, 1)
lut.Build()

for face_id in face_ids:
    face_color = [0.0, 0.0, 0.0]
    lut.GetColor(face_id, face_color)
    face_polydata = model.get_face_polydata(face_id)
    gr.add_geometry(renderer, face_polydata, color=face_color, wire=True)
'''

# Display window.
gr.display(renderer_window)


