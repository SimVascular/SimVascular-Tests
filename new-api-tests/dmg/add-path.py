'''Test adding a path to the SV Data Manager.

   This is tested using the Demo Project.
'''
from pathlib import Path
import sv

## Create a PathSeries from an SV file.
#
mdir = "../data/"
file_name = "DemoProject/Paths/aorta.pth"
path_series = sv.pathplanning.Series(mdir+file_name)
print("Number of paths: {0:d}".format(path_series.get_num_times()))
print("Method: {0:s}".format(path_series.get_method()))

## Get the path at time 0.
#
print("Path at time 0:")
aorta_path = path_series.get_path(0)
control_points = aorta_path.get_control_points()
print("Number of control points: {0:d}".format(len(control_points)))

## Add the Python path object under the SV Data Manager 'Paths' nodes
#  as a new  node named 'new_aorta'.
#
sv.dmg.add_path("new_aorta", aorta_path)

