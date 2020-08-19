'''Test creating a contour segmentation using contour points.
'''
import json
import sv
import sys
import vtk
sys.path.insert(1, '../graphics/')
import graphics as gr

## Read in contour points.
#
with open('level-set-contour-points.json') as json_file:
    contour_points = json.load(json_file)
print("Read {0:d} contour points.".format(len(contour_points)))

## Create a segmentation using the Contour class. 
#
print("Create contour segmentation ...")
set_points = False
set_points = True
if set_points:
    print("Set contour points.")
    seg = sv.segmentation.Contour()
    seg.set_contour_points(contour_points)
else:
    seg = sv.segmentation.Contour(contour_points)

center = seg.get_center()
print("  Center: {0:g} {1:g} {2:g}".format(center[0], center[1], center[2]))
#
normal = seg.get_normal()
print("  Normal: {0:g} {1:g} {2:g}".format(normal[0], normal[1], normal[2]))
#
points = seg.get_points()
num_pts = len(points)
print("  Number of contour points: {0:d}".format(num_pts))

## Create renderer and graphics window.
win_width = 500
win_height = 500
renderer, renderer_window = gr.init_graphics(win_width, win_height)

## Show plane.
plane = vtk.vtkPlane()
plane.SetOrigin(center)
plane.SetNormal(normal)
#
gr.add_plane(renderer, center, normal, color=[1,0,1])

## Show contour.
gr.create_segmentation_geometry(renderer, seg)

# Display window.
gr.display(renderer_window)


