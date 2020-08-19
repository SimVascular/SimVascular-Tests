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
num_segs = seg_series.num_segmentations(time=0)
print("Number of segmentations: {0:d}".format(num_segs))
segmentations = []
for i in range(num_segs):
    #print("---------- segmentation {0:d} ----------".format(i))
    segmentation = aorta_segmentations.get_segmentation(i, time=0)
    segmentations.append(segmentation)

## Add the Python segmentation objects under the SV Data Manager 'Segmentations' nodes
#  as a new  node named 'new_aorta'.
#
sv.dmg.add_segmentation(name="new_aorta", path="aorta", segmentations=segmentations)

