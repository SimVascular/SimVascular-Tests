'''Test the geometry.interpolate_closed_curve() function.
'''
import os
from pathlib import Path
import sv
import sys
import vtk
import sv_contour 

## Set some directory paths. 
script_path = Path(os.path.realpath(__file__)).parent
parent_path = Path(os.path.realpath(__file__)).parent.parent
data_path = parent_path / 'data'

try:
    sys.path.insert(1, str(parent_path / 'graphics'))
    import graphics as gr
except:
    print("Can't find the new-api-tests/graphics package.")

win_width = 500
win_height = 500
renderer, renderer_window = gr.init_graphics(win_width, win_height)

## Read contours.
contours = sv_contour.read_contours()
contour = contours[10]
center = contour.get_center()
contour_polydata = contour.get_polydata()
gr.create_contour_geometry(renderer, contour)
print("contour_polydata type: " + str(type(contour_polydata)))

## Interpolate a contour.
int_polydata = sv.geometry.interpolate_closed_curve(polydata=contour_polydata, number_of_points=4)
print("int_polydata type: " + str(type(int_polydata)))
gr.add_geometry(renderer, int_polydata, color=[0.5, 0.0, 0.0])

## Show geometry.
#
camera = renderer.GetActiveCamera();
camera.Zoom(0.5)
#camera.SetPosition(center[0], center[1], center[2])
camera.SetFocalPoint(center[0], center[1], center[2])
gr.display(renderer_window)

