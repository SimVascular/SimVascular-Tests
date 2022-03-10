'''Test scaling segmentations read in from a .ctgr file. 

   This is tested using the Demo Project. A new Segmenation group 
   named 'new_aorta' is created.
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

try:
    sys.path.insert(1, str(parent_path / 'graphics'))
    import graphics as gr
except:
    print("Can't find the new-api-tests/graphics package.")

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
file_name = str(data_path / 'DemoProject' / 'Segmentations' / 'aorta.ctgr')
print("Read SV ctgr file: {0:s}".format(file_name))
seg_series = sv.segmentation.Series(file_name)
num_times = seg_series.get_num_times()
print("Number of times: {0:d}".format(num_times))

# The SV Segmentation class names don't match class types so create a map here.
ctype_map = { "Circle":"CIRCLE", "Contour":"CONTOUR", "LevelSet":"LEVEL_SET", "Polygon":"POLYGON", "SplinePolygon":"SPLINE_POLYGON"} 

# Scale the segmentations.
#
time = 0
num_segs = seg_series.get_num_segmentations(time)
segmentations = []
scaled_segmentations = []
scale = 0.5

for sid in range(num_segs):
    seg = seg_series.get_segmentation(sid, time)
    sid = seg.get_id()
    ctype = seg.get_type()
    print(' ') 
    print('id: {0:d}'.format(sid))
    print('type: {0:s}'.format(ctype))

    if ctype == "Contour":
        control_points = seg.get_points()
    else:
        control_points = seg.get_control_points()

    center = seg.get_center()
    normal = seg.get_normal()
    scaled_control_points = scale_points(control_points, center, scale, normal)

    # Create a new scaled segmentation.
    scaled_seg = sv.segmentation.create(ctype_map[ctype])

    if ctype == "Contour":
        scaled_seg.set_contour_points(scaled_control_points)
    else:
        scaled_seg.set_control_points(scaled_control_points)

    scaled_segmentations.append(scaled_seg)
    segmentations.append(seg)

## Create renderer and graphics window.
win_width = 500
win_height = 500
renderer, renderer_window = gr.init_graphics(win_width, win_height)

## Show segmentation contours.
for seg in segmentations:
    gr.create_segmentation_geometry(renderer, seg, color=[0,1,0])

## Show scaled segmentation contours.
for seg in scaled_segmentations:
    gr.create_segmentation_geometry(renderer, seg, color=[1,0,0])

# Display window.
gr.display(renderer_window)


