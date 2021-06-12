
from math import sqrt
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

## Read an SV segmentation group file. 
#
file_name = str(data_path / 'DemoProject' / 'Segmentations' / 'aorta.ctgr')
print("Read SV ctgr file: {0:s}".format(file_name))
seg_series = sv.segmentation.Series(file_name)
num_times = seg_series.get_num_times()
print("Number of time points: {0:d}".format(num_times))

## Create renderer and graphics window.
win_width = 500
win_height = 500
renderer, renderer_window = gr.init_graphics(win_width, win_height)

# Compute min/max radius.
min_radius = 1e6
max_radius = -1e6
for time in range(num_times):
    num_segs = seg_series.get_num_segmentations(time)
    for sid in range(num_segs):
        seg = seg_series.get_segmentation(sid, time)
        try:
            control_points = seg.get_control_points()
        except:
            control_points = []
        center = seg.get_center()
        points = seg.get_points()
        radius = 0.0
        for pt in points:
            radius += sqrt(sum([(pt[i]-center[i])*(pt[i]-center[i]) for i in range(3)]))
        radius /= len(points)
        min_radius = min(min_radius, radius)
        max_radius = max(min_radius, radius)
        #gr.add_sphere(renderer, center, radius)
        gr.create_segmentation_geometry(renderer, seg)

print("Min segmentation radius: {0:g}".format(min_radius))
print("Max segmentation radius: {0:g}".format(max_radius))

# Display window.
gr.display(renderer_window)

