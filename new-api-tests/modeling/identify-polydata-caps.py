''' Test identifying caps for a POLYDATA model.

    This seems to mostly work except with healthy pulmonary model blended_discrete.vtp
    seems to have a couple of internal faces?
'''
import sv
import sys
import vtk
sys.path.insert(1, '../graphics/')
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

    print("Done.") 
    return face_caps

## Create renderer and graphics window.
win_width = 500
win_height = 500
renderer, renderer_window = gr.init_graphics(win_width, win_height)

## Create a modeler.
file_name = "../data/models/cylinder.stl"
file_name = "../data/DemoProject/Models/demo.vtp"
file_name = "./blended_discrete.vtp"
modeler = sv.modeling.Modeler(sv.modeling.Kernel.POLYDATA)
model = modeler.read(file_name)
print("Model type: " + str(type(model)))

## Compute model face IDs for STL file.
if 'stl' in file_name:
    face_ids = model.compute_boundary_faces(angle=60.0)
face_ids = model.get_face_ids()
print("Number of model Face IDs: {0:d}".format(len(face_ids)))
#print("Model Face IDs: {0:s}".format(str(face_ids)))

## Test another way to identify caps just using vtk.
face_caps = identify_caps(model)

## Show the caps.
num_caps = 0
for face_id,is_cap in zip(face_ids, face_caps):
    face_polydata = model.get_face_polydata(face_id=face_id)
    if is_cap:
        gr.add_geometry(renderer, face_polydata, color=[1.0, 0.0, 0.0], wire=False)
        num_caps += 1
    else:
        gr.add_geometry(renderer, face_polydata, color=[0.0, 1.0, 0.0], wire=True)

print("Number of caps: " + str(num_caps))

# Display window.
gr.display(renderer_window)

