'''Test setting different subdivision methods. 
'''
import json
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

# Create graphics window.
win_width = 500
win_height = 500
renderer, renderer_window = gr.init_graphics(win_width, win_height)

# Read control points.
with open(str(script_path / 'aorta-control-points.json')) as json_file:
    control_points = json.load(json_file)

# Create Path object.
path = sv.pathplanning.Path()

# Add control points.
for pt in control_points:
    path.add_control_point(pt)

## Print subdivision method, default it TOTAL.
#
print("Path:")
num_subdiv = path.get_num_subdivisions()
subdiv_method = path.get_subdivision_method()
print("  Number of subdivisions: {0:d}".format(num_subdiv))
print("  Subdivision method: {0:s}".format(subdiv_method))

## Get control points.
control_points = path.get_control_points()
print("  Number of control points: {0:d}".format(len(control_points)))

## Get path curve points.
curve_points = path.get_curve_points()
print("  Number of curve points: {0:d}".format(len(curve_points)))
# Show path.
gr.create_path_geometry(renderer, path)

## Set subdivision method. 
# 
# SubdivisionMethod: SPACING, SUBDIVISION or TOTAL.
#
# Default is TOTAL.
#
print("\nPath: set new subdivision method: ")
#
#path.set_subdivision_method(method=sv.path.SubdivisionMethod.SPACING, spacing=0.5)
#path.set_subdivision_method(method=sv.path.SubdivisionMethod.SUBDIVISION, num_div=10)
path.set_subdivision_method(method=sv.pathplanning.SubdivisionMethod.TOTAL, num_total=20)
#
num_subdiv = path.get_num_subdivisions()
subdiv_method = path.get_subdivision_method()
spacing = path.get_subdivision_spacing()
print("  Number of subdivisions: {0:d}".format(num_subdiv))
print("  Spacing: {0:f}".format(spacing))
print("  Subdivision method: {0:s}".format(subdiv_method))
curve_points = path.get_curve_points()
print("  Number of curve points: {0:d}".format(len(curve_points)))
'''
for i,pt in enumerate(curve_points):
    print("{0:d} {1:s}".format(i, str(pt)))
'''

# Show path.
gr.create_path_geometry(renderer, path, line_color=[1.0,0.0,0.0])

# Display window.
gr.display(renderer_window)


