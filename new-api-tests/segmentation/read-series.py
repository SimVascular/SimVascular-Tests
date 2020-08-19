from pathlib import Path
import sv
import sys
import vtk
sys.path.insert(1, '../graphics/')
import graphics as gr

## Read an SV segmentation group file. 
#
home = str(Path.home())
file_name = home + "/SimVascular/DemoProject/Segmentations/aorta.ctgr"
#file_name = home + "/SimVascular/DemoProject/Segmentations/aorta.ctg"
print("Read SV ctgr file: {0:s}".format(file_name))
seg_series = sv.segmentation.Series(file_name)
num_times = seg_series.get_num_times()
print("Number of time points: {0:d}".format(num_times))

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

