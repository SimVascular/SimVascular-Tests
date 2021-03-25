'''Test adding control points. 
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

## Control points.
cpt1 = [2.0, 0.0, 0.0] 
cpt2 = [3.0, 0.0, 0.0] 
cpt3 = [4.0, 0.0, 0.0] 
cpt4 = [5.0, 0.0, 0.0] 

## Create Path object.
path = sv.pathplanning.Path()

## Add control points.
path.add_control_point(cpt1)
path.add_control_point(cpt2)
path.add_control_point(cpt3)
path.add_control_point(cpt4)

## Insert at location.
#
#  0 <= location <= number of control points - 1
cpt5 = [6.0, 0.0, 0.0] 
#path.add_control_point(cpt5, 1)   # front of list.
#path.add_control_point(cpt5, 3) 

## Insert at location closests to current control points.
#
cpt6 = [3.5, 0.0, 0.0] 
path.add_control_point(cpt6) 

## Error tests.
# 
# Duplicate control points.
# path.add_control_point(cpt4)
#

## Get control points.
control_points = path.get_control_points()
print("Number of control points: {0:d}".format(len(control_points)))

for i,pt in enumerate(control_points):
    print("i: {0:d}  point: {1:s}".format(i+1, str(pt)))

## Create renderer and graphics window.
win_width = 500
win_height = 500
renderer, renderer_window = gr.init_graphics(win_width, win_height)

# Create path geometry.
gr.create_path_geometry(renderer, path)

# Display window.
gr.display(renderer_window)



