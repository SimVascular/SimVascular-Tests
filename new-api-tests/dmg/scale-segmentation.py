'''Test scaling segmentations and adding them to the SV Data Manager.

   This is tested using the Demo Project. A new Segmenation group 
   named 'new_aorta' is created.
'''
from pathlib import Path
import sv

def scale_points(points, center, scale, normal):
    '''Scale a list of 3D points.
       
       Control points must lie in a plane so also project the scaled points onto
       the plane 'normal*center = dist'. The SV plane tolerance is probably too 
       small (1e-6).
    '''
    scaled_points = []
    dist = sum([normal[i] * center[i] for i in range(3)])
    for pt in points:
        scaled_pt = [center[i]  +  scale * (pt[i] - center[i]) for i in range(3)]
        d = sum([normal[i] * scaled_pt[i] for i in range(3)]) - dist
        scaled_pt = [scaled_pt[i] - d*normal[i] for i in range(3)]
        scaled_points.append(scaled_pt)
    return scaled_points

# Read an SV segmentation .ctgr file. 
#
home = str(Path.home())
file_name = home + "/SimVascular/DemoProject/Segmentations/aorta.ctgr"
print("Read SV ctgr file: {0:s}".format(file_name))
seg_series = sv.segmentation.Series(file_name)
num_times = seg_series.get_num_times()
print("Number of times: {0:d}".format(num_times))

# Scale the segmentations.
#
time = 0
num_segs = seg_series.get_num_segmentations(time)
segmentations = []
scale = 0.5

for sid in range(num_segs):
    seg = seg_series.get_segmentation(sid, time)
    ctype = seg.get_type()
    print('Segmentation type: {0:s}'.format(ctype))

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

    segmentations.append(seg)

## Add the Python segmentation objects under the SV Data Manager 'Segmentations' nodes
#  as a new  node named 'new_aorta'.
#
sv.dmg.add_segmentation(name="new_aorta", path="aorta", segmentations=segmentations)

