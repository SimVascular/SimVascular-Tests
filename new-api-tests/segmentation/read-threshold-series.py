'''Test reading in an SV contour group file for threshold contours.
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

## Read an SV segmentation group file. 
#
home = str(Path.home())
file_name = str(data_path / 'DemoProject' / 'Segmentations' / 'threshold.ctgr')
print("Read SV ctgr file: {0:s}".format(file_name))
seg_series = sv.segmentation.Series(file_name)
num_times = seg_series.get_num_times()
print("Number of times: {0:d}".format(num_times))

## Create renderer and graphics window.
win_width = 500
win_height = 500
renderer, renderer_window = gr.init_graphics(win_width, win_height)

## Show contours.
for time in range(num_times):
    num_segs = seg_series.get_num_segmentations(time)
    for sid in range(num_segs):
        seg = seg_series.get_segmentation(sid, time)
        gr.create_segmentation_geometry(renderer, seg)

# Display window.
gr.display(renderer_window)

