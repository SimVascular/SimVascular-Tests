'''This script tests smoothing a path. 
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

## Create a PathSeries from an SV file.
#
file_name = str(data_path / 'DemoProject' / 'Paths' / 'aorta.pth')
path_series = sv.pathplanning.Series(file_name)
print("Number of time steps: {0:d}".format(path_series.get_num_times()))
print("Method: {0:s}".format(path_series.get_method()))
print("Aorta path:")
aorta_path = path_series.get_path(0)
control_points = aorta_path.get_control_points()
print("  Number of control points: {0:d}".format(len(control_points)))
curve_points = aorta_path.get_curve_points()
print("  Number of curve points: {0:d}".format(len(curve_points)))

## Smooth the path.
print("Smoothed the aorta path:")
sample_rate = 20
num_modes = 40
smooth_control_pts = True
smooth_control_pts = False
print("  sample_rate: " + str(sample_rate))
print("  num_modes: " + str(num_modes))
smoothed_path = aorta_path.smooth(sample_rate=sample_rate, num_modes=num_modes, smooth_control_pts=smooth_control_pts)
control_points = smoothed_path.get_control_points()
curve_points = smoothed_path.get_curve_points()
print("  Number of control points: {0:d}".format(len(control_points)))
print("  Number of curve points: {0:d}".format(len(curve_points)))

## Create renderer and graphics window.
win_width = 500
win_height = 500
renderer, renderer_window = gr.init_graphics(win_width, win_height)

# Create path geometry.
gr.create_path_geometry(renderer, aorta_path)
gr.create_path_geometry(renderer, smoothed_path, line_color=[0.6,0.0,0.0], marker_color=[0.0,0.6,0.0])

# Display window.
gr.display(renderer_window)


