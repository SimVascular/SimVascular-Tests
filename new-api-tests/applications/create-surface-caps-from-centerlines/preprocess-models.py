'''Preprocess .vtk models.
'''
import os
from pathlib import Path
import math
import sv
import sys
import vtk

## Set some directory paths. 
script_path = Path(os.path.realpath(__file__)).parent
parent_path = Path(os.path.realpath(__file__)).parent.parent

sys.path.insert(1, '../../../graphics/')
import graphics as gr

def identify_caps(model):
    #print("========== identify_caps ==========") 
    face_caps = []
    face_ids = model.get_face_ids()
    for face_id in face_ids:
        #print("----- face {0:d} -----".format(face_id))
        face_polydata = model.get_face_polydata(face_id=face_id)
        feature_edges = vtk.vtkFeatureEdges()
        feature_edges.SetInputData(face_polydata)
        feature_edges.BoundaryEdgesOn()
        feature_edges.ManifoldEdgesOff()
        feature_edges.NonManifoldEdgesOff()
        feature_edges.FeatureEdgesOff()
        feature_edges.ColoringOn()
        #feature_edges.SetFeatureAngle(self.params.angle);
        feature_edges.Update()

        boundary_edges = feature_edges.GetOutput()
        clean_filter = vtk.vtkCleanPolyData()
        boundary_edges_clean = clean_filter.SetInputData(boundary_edges)
        clean_filter.Update()
        cleaned_edges = clean_filter.GetOutput()

        conn_filter = vtk.vtkPolyDataConnectivityFilter()
        conn_filter.SetInputData(cleaned_edges)
        conn_filter.SetExtractionModeToSpecifiedRegions()
        boundary_edge_components = list()
        rid = 0

        while True:
            conn_filter.AddSpecifiedRegion(rid)
            conn_filter.Update()
            component = vtk.vtkPolyData()
            component.DeepCopy(conn_filter.GetOutput())
            if component.GetNumberOfCells() <= 0:
                break
            #print("{0:d}: Number of boundary lines: {1:d}".format(rid, component.GetNumberOfCells()))
            boundary_edge_components.append(component)
            conn_filter.DeleteSpecifiedRegion(rid)
            rid += 1

        if rid == 1:
            face_caps.append(True)
        else:
            face_caps.append(False)

        return face_caps

if __name__ == '__main__':
    file_name = sys.argv[1]
    file_prefix, file_extension = os.path.splitext(file_name)

    kernel = sv.modeling.Kernel.POLYDATA
    modeler = sv.modeling.Modeler(kernel)
    model = modeler.read(file_name)
    try:
        face_ids = model.get_face_ids()
    except:
        face_ids = model.compute_boundary_faces(angle=60.0)
    print("Face IDs: {0:s}".format(str(face_ids)))

    model_surf = model.get_polydata()
    num_cells = model_surf.GetNumberOfCells()
    points = model_surf.GetPoints()
    min_area = 1e6
    max_area = -1e6
    avg_area = 0.0

    for i in range(num_cells):
        cell = model_surf.GetCell(i)
        cell_pids = cell.GetPointIds()
        pid1 = cell_pids.GetId(0)
        pid2 = cell_pids.GetId(1)
        pid3 = cell_pids.GetId(2)

        pt1 = points.GetPoint(pid1)
        pt2 = points.GetPoint(pid2)
        pt3 = points.GetPoint(pid3)

        area = vtk.vtkTriangle.TriangleArea(pt1, pt2, pt3)
        avg_area += area

        if area < min_area:
            min_area = area
        elif area > max_area:
            max_area = area

    print("min area: {0:g}".format(min_area))
    print("max area: {0:g}".format(max_area))
    print("avg area: {0:g}".format(avg_area))

    length_scale = math.sqrt(2.0*avg_area) / 2.0
    print("length scale: {0:g}".format(length_scale))

    remeshed_model = sv.mesh_utils.remesh(model_surf, hmin=length_scale, hmax=length_scale)

    print("Number of cells: {0:d}".format(num_cells))
    num_cells = remeshed_model.GetNumberOfCells()
    print("Remshed model number of cells: {0:d}".format(num_cells))

    writer = vtk.vtkXMLPolyDataWriter()
    writer.SetFileName(file_prefix+"-remesh-surface.vtp")
    #writer.SetInputData(model_surf)
    writer.SetInputData(remeshed_model)
    writer.Update()
    writer.Write()

    ## Create renderer and graphics window.
    win_width = 500
    win_height = 500
    renderer, renderer_window = gr.init_graphics(win_width, win_height)

    #gr.add_geometry(renderer, model_surf, color=[1.0, 0.0, 0.0]) 
    gr.add_geometry(renderer, model_surf, color=[1.0, 0.0, 0.0], wire=True, line_width=4)
    #gr.add_geometry(renderer, remeshed_model, color=[0.0, 1.0, 0.0], wire=True)

    '''
    # Create a color lookup table.
    lut = vtk.vtkLookupTable()
    lut.SetTableRange(0, len(face_ids))
    lut.SetHueRange(0, 1)
    lut.SetSaturationRange(1, 1)
    lut.SetValueRange(1, 1)
    lut.Build()
    for face_id in face_ids:
        face_polydata = model.get_face_polydata(face_id=face_id)
        color = [0.0, 0.0, 0.0]
        lut.GetColor(face_id, color)
        gr.add_geometry(renderer, face_polydata, color=color)
    '''

    ## Display window.
    gr.display(renderer_window)

