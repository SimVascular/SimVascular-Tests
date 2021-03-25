'''Test the sv.geometry.local_blend() function. 
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

def compute_junction_center(renderer, model):
    '''Compute center of union junction.
    '''
    num_points = model.GetPoints().GetNumberOfPoints()
    points = model.GetPoints()
    data = model.GetPointData().GetArray("GlobalBoundaryPoints")
    num_data = data.GetNumberOfTuples()
    bnd_pts = []
    print("GlobalBoundaryPoints num data: ", num_data)
    print("  Num data: ", num_data)
    for i in range(num_data):
        flag = data.GetValue(i)
        if flag == 1.0:
            pt = 3*[0.0]
            points.GetPoint(i, pt)
            bnd_pts.append(pt)

    print("  Num boundary points: ", len(bnd_pts))
    center = [0.0, 0.0, 0.0]
    for pt in bnd_pts:
        center[0] += pt[0]
        center[1] += pt[1]
        center[2] += pt[2]

    # Show junction.
    if False:
        points = vtk.vtkPoints()
        vertices = vtk.vtkCellArray()
        for pt in bnd_pts:
            pid = points.InsertNextPoint(pt)
            vertices.InsertNextCell(1)
            vertices.InsertCellPoint(pid)
        points_pd = vtk.vtkPolyData()
        points_pd.SetPoints(points)
        points_pd.SetVerts(vertices)
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(points_pd)
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        marker_color = [1.0, 0.0, 0.0]
        actor.GetProperty().SetColor(marker_color[0], marker_color[1], marker_color[2])
        actor.GetProperty().SetPointSize(8)
        renderer.AddActor(actor)

    return [c/len(bnd_pts) for c in center]

## Initialize graphics.
#
win_width = 500
win_height = 500
renderer, renderer_window = gr.init_graphics(win_width, win_height)

## Create blend options.
options = sv.geometry.BlendOptions()
print("\n\nOptions values: ")
[ print("  {0:s}:{1:s}".format(key,str(value))) for (key, value) in sorted(options.get_values().items()) ]
print("\n\n")

## Read in a model used to visualize the blend radius.
file_name = str(data_path / 'geometry' / 'two-cyls-with-GlobalBoundaryPoints.vtp')
reader = vtk.vtkXMLPolyDataReader()
reader.SetFileName(file_name) 
reader.Update()
bnd_model = reader.GetOutput()
 
## Compute center of union junction and visualize the blend radius.
blend_radius = 1.0
center = compute_junction_center(renderer, bnd_model)
gr.add_sphere(renderer, center, blend_radius, color=[0.0, 1.0, 0.0], wire=True)

## Read model to blend.
file_name = str(data_path / 'geometry' / 'two-cyls.vtp')
reader = vtk.vtkXMLPolyDataReader()
reader.SetFileName(file_name) 
reader.Update()
model = reader.GetOutput()

## Set faces to blend.
if "two-cyls.vtp" in file_name:
    blend_faces = [ { 'radius': blend_radius, 'face1':1, 'face2':2 } ]

## Perform the blend operation.
blend = sv.geometry.local_blend(surface=model, faces=blend_faces, options=options)
gr.add_geometry(renderer, blend, wire=True)

## Write the blended surface.
file_name = str(script_path / str("blended-" + file_name))
writer = vtk.vtkXMLPolyDataWriter()
writer.SetFileName(file_name)
writer.SetInputData(blend)
writer.Update()
writer.Write()

## Show geometry.
gr.display(renderer_window)


