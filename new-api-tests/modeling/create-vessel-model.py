'''Test creating a solid model of the contours from two vessels. 
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

def create_mesh(model):
  print("========== create mesh ==========")
  mesher = sv.meshing.TetGen()

  # Set the model for the mesher.
  mesher.set_model(model)
  face_ids = mesher.get_model_face_ids()
  print("Face IDs: {}".format(face_ids))

  # Set the wall IDs.
  caps = model.identify_caps()
  print("Cap ids: {}".format(caps))
  wall_ids = [face_ids[i] for i in range(len(caps)) if not caps[i]]
  print("Wall ids are {}".format(wall_ids))
  mesher.set_walls(wall_ids)

  edge_size = 0.9259
  print("Set meshing options ... ")
  options = sv.meshing.TetGenOptions(global_edge_size=edge_size, surface_mesh_flag=True, volume_mesh_flag=True)
  #options.radius_meshing_on = False
  #options.boundary_layer_inside = True
  #options.radius_meshing_scale = 0.4 

  # Generate the mesh. 
  mesher.generate_mesh(options)

  # Get the mesh as a vtkUnstructuredGrid. 
  mesh = mesher.get_mesh()
  print("Mesh:")
  print("  Number of nodes: {0:d}".format(mesh.GetNumberOfPoints()))
  print("  Number of elements: {0:d}".format(mesh.GetNumberOfCells()))
  return mesher.get_surface()

def read_contours(name):
    '''Read an SV contour group file.
    '''
    file_name = str(data_path / 'DemoProject' / 'Segmentations' / str(name+'.ctgr'))
    contour_group = sv.segmentation.Series(file_name)
    num_conts = contour_group.get_num_segmentations()
    contours = []

    for i in range(num_conts):
        cont = contour_group.get_segmentation(i)
        contours.append(cont)

    return contours

def get_contours_points(contours):

    points_list = []

    for cont in contours:
        cont_pts = cont.get_points()
        num_pts = len(cont_pts)

        points = vtk.vtkPoints()
        points.SetNumberOfPoints(num_pts)
        lines = vtk.vtkCellArray()

        for i in range(num_pts):
            pt = cont_pts[i]
            points.SetPoint(i, pt[0], pt[1], pt[2])
            if i > 0 and i < num_pts:
                cell = [i-1,i]
                lines.InsertNextCell(2,cell)

        cell = [num_pts-1,0]
        lines.InsertNextCell(2,cell)
        lines.InsertCellPoint(0)

        cont_pd = vtk.vtkPolyData()
        cont_pd.SetPoints(points)
        cont_pd.SetLines(lines)

        points_list.append(cont_pd)

    return points_list 

# Create a graphics window.
win_width = 1000
win_height = 1000
renderer, renderer_window = gr.init_graphics(win_width, win_height)

aorta_contours = read_contours('aorta')
aorta_points_list = get_contours_points(aorta_contours)

iliac_contours = read_contours('right_iliac')
iliac_points_list = get_contours_points(iliac_contours)
points_list = [aorta_points_list, iliac_points_list]

loft_opts = sv.LoftOptions()
loft_opts.linear_multiplier = 10
loft_opts.method = "nurbs"
loft_opts.num_out_pts_in_segs = 60
loft_opts.sample_per_segment = 12
loft_opts.u_knot_span_type = "average"
loft_opts.v_knot_span_type = "average"
loft_opts.u_parametric_span_type = "chord"
loft_opts.v_parametric_span_type = "chord"


model = sv.modeling.PolyData()
model.create_vessel_model(contour_list=points_list, num_sampling_pts=60, loft_options=loft_opts)
vessel_model_pd = model.get_polydata()
gr.add_geometry(renderer, vessel_model_pd, color=[1,0,0], edges=True)

model.write(file_name="vessel-model", format="vtp")

# Mesh the model.
#mesh = create_mesh(model)
#gr.add_geometry(renderer, mesh, color=[1,0,0], edges=True)

gr.display(renderer_window)

