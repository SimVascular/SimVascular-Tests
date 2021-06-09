'''This script tests reading a legacy path planning .path file containing multiple paths.
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

## Create a Paths object from an SV file.
#
home = str(Path.home())
path_name = "aorta-legacy"
path_name = "aorta-legacy-multiple-paths"
file_name = str(data_path / 'DemoProject' / 'Paths' / (path_name + ".paths"))

# Read path files using a class method. 
path_series_list = sv.pathplanning.Series.read_legacy(file_name)
print("Number of path series read: {0:d}".format(len(path_series_list)))

## Create renderer and graphics window.
win_width = 500
win_height = 500
renderer, renderer_window = gr.init_graphics(win_width, win_height)

for path_series in path_series_list: 
    print("----------  Name: {0:s} ----------".format(path_series.get_name()))
    print("  Number of time steps: {0:d}".format(path_series.get_num_times()))
    print("  Path at time 0:")
    path = path_series.get_path(0)
    control_points = path.get_control_points()
    print("  Number of control points: {0:d}".format(len(control_points)))
    curve_points = path.get_curve_points()
    print("  Number of curve points: {0:d}".format(len(curve_points)))
    #
    point = path.get_curve_point(20)
    print("  Point 20: {0:s}".format(str(point)))
    tangent = path.get_curve_tangent(20)
    print("  Tangent 20: {0:s}".format(str(tangent)))
    normal = path.get_curve_normal(20)
    print("  Normal 20: {0:s}".format(str(normal)))
    #
    num_subdiv = path.get_num_subdivisions()
    print("  Number of subdivisions: {0:d}".format(num_subdiv))
    subdiv_method = path.get_subdivision_method()
    print("  Subdivision method: {0:s}".format(subdiv_method))

    # Create path geometry.
    gr.create_path_geometry(renderer, path)

# Display window.
gr.display(renderer_window)


