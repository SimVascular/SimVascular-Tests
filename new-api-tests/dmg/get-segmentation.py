'''Test getting a segmentation from the SV Data Manager.

This is tested using the Demo Project.
'''

import sv
  
## Create a Python segmentation group object from the SV Data Manager 'Segmentations/aorta' node. 
#
seg_name = "aorta"
segmentation_group = sv.dmg.get_segmentation(seg_name)
num_segs = segmentation_group.number_of_segmentations()
print("Number of segmentations: {0:d}".format(num_segs))

## Get segmentations.
#
for i in range(num_segs):
    print("---------- segmentation {0:d} ----------".format(i))
    cont = segmentation_group.get_segmentation(i)
    center = cont.get_center()
    path_point = cont.get_path_point()
    try:
        control_points = cont.get_control_points()
    except:
        control_points = []
    segmentation_points = cont.get_points()
    print("Type: {0:s}".format(cont.get_type()))
    print("Center: {0:s}".format(str(center)))
    print("Path point: {0:s}".format(str(path_point)))
    print("Number of control points: {0:d}".format(len(control_points)))
    #for i,pt in enumerate(control_points): 
    #    print("  Control point {0:d}: {1:s}".format(i+1, str(pt)))
    print("Number of segmentation points: {0:d}".format(len(segmentation_points)))
    #for i,pt in enumerate(segmentation_points): 
    #    print("Contour point {0:d}: {1:s}".format(i+1, str(pt)))

