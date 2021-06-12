'''Test getting segmentations from the SV Data Manager and computing radii.

   This is tested using the Demo Project.
'''
from math import sqrt
import sv
  
## Create a Python segmentation group object from the 
#  SV Data Manager 'Segmentations/aorta' node. 
#
seg_name = "aorta"
segmentations = sv.dmg.get_segmentations(seg_name)
print("Number of segmentations: {0:d}".format(len(segmentations)))

## Compute min/max segmentation radii.
#
min_radius = 1e6
max_radius = -1e6

for i,seg in enumerate(segmentations): 
    center = seg.get_center()
    path_point = seg.get_path_point()
    try:
        control_points = seg.get_control_points()
    except:
        control_points = []
    points = seg.get_points()
    radius = 0.0
    for pt in points:
        radius += sqrt(sum([(pt[i]-center[i])*(pt[i]-center[i]) for i in range(3)]))
    radius /= len(points)
    min_radius = min(min_radius, radius)
    max_radius = max(min_radius, radius)

print("Min segmentation radius: {0:g}".format(min_radius))
print("Max segmentation radius: {0:g}".format(max_radius))
