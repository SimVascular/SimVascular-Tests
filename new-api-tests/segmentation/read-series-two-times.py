'''Test reading in a segmentation group with two time steps.
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

## Read an SV segmentation group file. 
#
home = str(Path.home())
file_name = str(data_path / 'DemoProject' / 'Segmentations' / 'circle-two-times.ctgr')
print("Read SV ctgr file: {0:s}".format(file_name))
seg_series = sv.segmentation.Series(file_name)

time = 0
print("Time: {0:d}".format(time))
num_segs = seg_series.get_num_segmentations(time)
print("  Number of segmentations: {0:d}".format(num_segs))

time = 1
print("Time: {0:d}".format(time))
num_segs = seg_series.get_num_segmentations(time)
print("  Number of segmentations: {0:d}".format(num_segs))

