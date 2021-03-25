'''Test creating a polygon segmentation using a set of control points.
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

## Define control points.
#
points = [ 
  [-3.0, 0.0, 1.0],
  [ -1.0, 0.0, 1.0],
  [ -1.0, 0.0, -1.0],
  [ -3.0, 0.0, -1.0]
]
 
## Create a segmentation using the Polygon class. 
#
print("Create spline poylgon segmentation ...")
if True:
    seg = sv.segmentation.SplinePolygon(control_points=points)
else:
    print("Set control points.")
    seg = sv.segmentation.SplinePolygon(control_points=points)
    seg.set_control_points(control_points=points)

## Set spline subdivision parameters.
seg.set_subdivision_params(type=sv.segmentation.SubdivisionType.CONSTANT_SPACING)
subd_type, subd_spacing, subd_number = seg.get_subdivision_params()
print("  Subdivision type: {0:s}".format(subd_type))
print("              spacing: {0:f}".format(subd_spacing))
print("              number: {0:d}".format(subd_number))
#
center = seg.get_center()
print("  Center: {0:g} {1:g} {2:g}".format(center[0], center[1], center[2]))
#
normal = seg.get_normal()
print("  Normal: {0:g} {1:g} {2:g}".format(normal[0], normal[1], normal[2]))
#
control_points = seg.get_control_points()
num_control_pts = len(control_points)
print("  Number of control_points: {0:d}".format(num_control_pts))
print("  Control points: ")
for pt in control_points:
    print("  {0:s}".format(str(pt)))
#
points = seg.get_points()
num_pts = len(points)
print("  Number of contour points: {0:d}".format(num_pts))

## Create renderer and graphics window.
win_width = 500
win_height = 500
renderer, renderer_window = gr.init_graphics(win_width, win_height)
center = seg.get_center()
## Show plane.
plane = vtk.vtkPlane()
plane.SetOrigin(center)
plane.SetNormal(normal)
#
#gr.add_plane(renderer, center, normal, color=[1,0,1])

## Show contour.
gr.create_segmentation_geometry(renderer, seg)

# Display window.
gr.display(renderer_window)


