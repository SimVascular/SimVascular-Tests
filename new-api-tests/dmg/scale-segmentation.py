'''Test scaling segmentations and adding them to the SV Data Manager.

   This is tested using the Demo Project 'aorta' segmentation. 
   A new Segmentation group named 'new_aorta' is created.
'''
from pathlib import Path
import sv

def scale_points(points, center, scale, normal):
    '''Scale a list of 3D points around the given center.
       
       Control points must lie in a plane so project the scaled points onto
       the plane 'normal*center = dist'. The SV plane tolerance is 1e-6 
       (probably too small) so some points may fail this check.
    '''
    scaled_points = []
    dist = sum([normal[i] * center[i] for i in range(3)])
    for pt in points:
        scaled_pt = [center[i]  +  scale * (pt[i] - center[i]) for i in range(3)]
        d = sum([normal[i] * scaled_pt[i] for i in range(3)]) - dist
        scaled_pt = [scaled_pt[i] - d*normal[i] for i in range(3)]
        scaled_points.append(scaled_pt)
    return scaled_points

# Get the segmentations for 'aorta'.
segmentation_name = 'aorta'
path_name = 'aorta'
segmentations = sv.dmg.get_segmentations(segmentation_name)

# Scale the segmentations.
#
scaled_segmentations = []
scale = 0.5

for seg in segmentations:
    sid = seg.get_id()
    ctype = seg.get_type()
    #print('    ')
    #print('id: {0:d}'.format(sid))
    #print('type: {0:s}'.format(ctype))

    if ctype == "Contour":
        control_points = seg.get_points()
    else:
        control_points = seg.get_control_points()

    center = seg.get_center()
    normal = seg.get_normal()
    scaled_control_points = scale_points(control_points, center, scale, normal)

    if ctype == "Contour":
        seg.set_contour_points(scaled_control_points)
    else:
        seg.set_control_points(scaled_control_points)

    scaled_segmentations.append(seg)

## Add the new scaled segmentation group named 'new_aorta' 
#  under the SV Data Manager 'Segmentations' node.
#
sv.dmg.add_segmentation(name="new_aorta", path=path_name, segmentations=scaled_segmentations)

