'''Test reading in a segmentation .cgtr file containing circle segmentations.
'''
from pathlib import Path
import sv
import sys
import vtk
sys.path.insert(1, '../graphics/')
import graphics as gr

## Read an SV segmentation group file. 
#
home = str(Path.home())
file_name = "../data/DemoProject/Segmentations/circle.ctgr"
print("Read SV ctgr file: {0:s}".format(file_name))
seg_series = sv.segmentation.Series(file_name)
num_times = seg_series.get_num_times()
print("  Number of time points : {0:d}".format(num_times))

## Create renderer and graphics window.
win_width = 500
win_height = 500
renderer, renderer_window = gr.init_graphics(win_width, win_height)

## Show contours.
segs = []
for time in range(num_times):
    print(" ")
    print("----------- Time {0:d} -------- ".format(time))
    num_segs = seg_series.get_num_segmentations(time)
    print("Number of segmentationspoints : {0:d}".format(num_segs))

    for sid in range(num_segs):
        print("----------- Segmentation {0:d} -------- ".format(sid))
        print("get_segmentation")
        seg = seg_series.get_segmentation(sid, time)
        print("create_segmentation_geometry")
        gr.create_segmentation_geometry(renderer, seg)
        segs.append(seg)

    print("done ")

# Display window.
gr.display(renderer_window)

