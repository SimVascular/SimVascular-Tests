'''Test getting segmentations from the SV Data Manager.

   This is tested using the Demo Project.
'''
import sv
  
## Create a Python segmentation group object from the SV Data Manager 'Segmentations/aorta' node. 
#
seg_name = "aorta"
segmentations = sv.dmg.get_segmentations(seg_name)
print("Number of segmentations: {0:d}".format(len(segmentations)))

## Get segmentations.
#
for i,seg in enumerate(segmentations): 
    print("---------- segmentation {0:d} ----------".format(i))
    center = seg.get_center()
    path_point = seg.get_path_point()
    try:
        control_points = seg.get_control_points()
    except:
        print("Exception getting control points.".format(i))
        control_points = []
    points = seg.get_points()
    print("Type: {0:s}".format(seg.get_type()))
    print("Center: {0:s}".format(str(center)))
    print("Path point: {0:s}".format(str(path_point)))
    print("Number of control points: {0:d}".format(len(control_points)))
    #for i,pt in enumerate(control_points): 
    #    print("  Control point {0:d}: {1:s}".format(i+1, str(pt)))
    print("Number of segmentation points: {0:d}".format(len(points)))
    #for i,pt in enumerate(segmentation_points): 
    #    print("Contour point {0:d}: {1:s}".format(i+1, str(pt)))

