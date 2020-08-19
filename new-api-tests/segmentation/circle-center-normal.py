'''Test creating a circle segmentation using a center and a normal.
'''
import sv
import sys
import vtk
sys.path.insert(1, '../graphics/')
import graphics as gr

## Create a segmentation using the Circle class. 
#
print("Create circle segmentation ...")
radius = 1.0
center = [0.0, 0.0, 0.0]
#
plane = vtk.vtkPlane()
plane.SetOrigin(center);
plane_normal = [0.0, 1.0, 0.0]
plane.SetNormal(plane_normal)
#
seg = sv.segmentation.Circle(radius=radius, center=center, normal=plane_normal)

# Error test;
#seg = sv.segmentation.Circle(radius=radius)
#seg = sv.segmentation.Circle(radius=radius, center=center)
#path_frame = sv.pathplanning.PathFrame()
#seg = sv.segmentation.Circle(radius=radius, center=center, frame=path_frame)
center = seg.get_center()
print("  Center: {0:g} {1:g} {2:g}".format(center[0], center[1], center[2]))
#
points = seg.get_points()
num_pts = len(points)
print("  Number of points: {0:d}".format(num_pts))

## Create renderer and graphics window.
win_width = 500
win_height = 500
renderer, renderer_window = gr.init_graphics(win_width, win_height)

## Show plane.
gr.add_plane(renderer, center, plane_normal, color=[1,0,1])

## Show contour.
gr.create_segmentation_geometry(renderer, seg)

## Set the circle center.
center = [1.0, 0.0, 0.0]
seg.set_center(center)
gr.create_segmentation_geometry(renderer, seg, color=[1,0,0])

## Set the circle normal.
normal = [1.0, 0.0, 0.0]
seg.set_normal(normal)
gr.create_segmentation_geometry(renderer, seg, color=[0,1,1])

# Display window.
gr.display(renderer_window)


