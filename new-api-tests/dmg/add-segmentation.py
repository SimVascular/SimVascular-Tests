'''Test adding a segmentation to the SV Data Manager.

   This is tested using the Demo Project.
'''
from pathlib import Path
import sv

## Create a Segmentation Group from an SV file.
#
# Read an SV segmentation .ctgr file. 
#
home = str(Path.home())
file_name = home + "/SimVascular/DemoProject/Segmentations/aorta.ctgr"
print("Read SV ctgr file: {0:s}".format(file_name))
seg_series = sv.segmentation.Series(file_name)
num_times = seg_series.get_num_times()
print("Number of times: {0:d}".format(num_times))

time = 0
num_segs = seg_series.get_num_segmentations(time)
segmentations = []

for sid in range(num_segs):
    seg = seg_series.get_segmentation(sid, time)
    ctype = seg.get_type()
    segmentations = []
    print('Segmentation type: {0:s}'.format(ctype))

## Add the Python segmentation objects under the SV Data Manager 'Segmentations' nodes
#  as a new  node named 'new_aorta'.
#
sv.dmg.add_segmentation(name="new_aorta", path="aorta", segmentations=segmentations)

