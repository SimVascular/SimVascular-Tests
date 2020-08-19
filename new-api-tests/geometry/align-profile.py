'''Test aligining two profiles.
'''
from pathlib import Path
import sv
import sys
import vtk
sys.path.insert(1, '../graphics/')
import graphics as gr
import sv_contour 

radius = 0.05
win_width = 500
win_height = 500
renderer, renderer_window = gr.init_graphics(win_width, win_height)

num_samples = 30
num_samples = 60
num_samples = 20

## Read contours.
#
contours = sv_contour.read_contours()

## cont1 
#
cont1 = contours[10]
center = cont1.get_center()
cont1_polydata = cont1.get_polydata()
gr.create_contour_geometry(renderer, cont1)

# Create interpolated geometry for the contour.
cont1_ipd = sv.geometry.interpolate_closed_curve(cont1_polydata, num_samples)

# Get two points on interpolated curve.
pt = 3*[0.0]
cont1_ipd.GetPoints().GetPoint(0, pt)
gr.add_sphere(renderer, pt, radius, color=[1,0,0])

cont1_ipd.GetPoints().GetPoint(4, pt)
gr.add_sphere(renderer, pt, radius, color=[0,1,0])
gr.add_geometry(renderer, cont1_ipd)

## cont2 
#
cont2 = contours[11]
points2 = cont2.get_points()
cont2_polydata = cont2.get_polydata()
gr.create_contour_geometry(renderer, cont2)
cont2_ipd = sv.geometry.interpolate_closed_curve(cont2_polydata, num_samples)

## Align contours.
use_dist = False
use_dist = True
cont2_align_pd = sv.geometry.align_profile(cont1_ipd, cont2_ipd, use_dist)

# Get two points on aligned curve.
pt = 3*[0.0]
#cont2_ipd.GetPoints().GetPoint(0, pt)
#gr.add_sphere(renderer, pt, radius, color=[0,0,1])

cont2_align_pd.GetPoints().GetPoint(0, pt)
gr.add_sphere(renderer, pt, radius, color=[1,0,0])
#
cont2_align_pd.GetPoints().GetPoint(4, pt)
gr.add_sphere(renderer, pt, radius, color=[0,1,0])

gr.add_geometry(renderer, cont2_ipd)

## Show geometry.
#
camera = renderer.GetActiveCamera();
camera.Zoom(0.5)
#camera.SetPosition(center[0], center[1], center[2])
camera.SetFocalPoint(center[0], center[1], center[2])
gr.display(renderer_window)

