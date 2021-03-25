'''Test the Parasolid class loft method.
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

win_width = 500
win_height = 500
renderer, renderer_window = gr.init_graphics(win_width, win_height)

def get_profile_contour(gr, renderer, contours, cid, npts):
    cont = contours[cid]
    #gr.create_contour_geometry(renderer, cont)
    cont_pd = cont.get_polydata()
    cont_ipd = sv.geometry.interpolate_closed_curve(polydata=cont_pd, number_of_points=npts)
    #gr.add_geometry(renderer, cont_ipd)
    return cont_ipd

def read_contours():
    '''Read an SV contour group file.
    '''
    file_name = str(data_path / 'DemoProject' / 'Segmentations' / 'aorta.ctgr')
    print("Read SV ctgr file: {0:s}".format(file_name))
    contour_group = sv.segmentation.Series(file_name)
    num_conts = contour_group.get_num_segmentations()
    contours = []

    for i in range(num_conts):
        cont = contour_group.get_segmentation(i)
        contours.append(cont)

    return contours

## Create a Parasolid modeler.
#
modeler = sv.modeling.Modeler(sv.modeling.Kernel.PARASOLID)

## Read in segmentations (contours) to loft.
#
contours = read_contours()
num_contours = len(contours)
print("Number of contours {0:d}".format(num_contours))

## Align contours and create curves from them. 
#
curve_list = [] 
start_cid = 0
end_cid = num_contours
#end_cid = 4
use_distance = True
num_profile_points = 25
tolerance = 1e-3

for cid in range(start_cid,end_cid):
    cont_ipd = get_profile_contour(gr, renderer, contours, cid, num_profile_points)
    if cid == start_cid:
        cont_align = cont_ipd 
    else:
        cont_align = sv.geometry.align_profile(last_cont_align, cont_ipd, use_distance)

    curve = modeler.interpolate_curve(cont_align)
    #curve = modeler.approximate_curve(cont_align, tolerance)
    curve_pd = curve.get_polydata()
    gr.add_geometry(renderer, curve_pd, color=[1.0, 0.0, 0.0])
    curve_list.append(curve) 
    #add_sphere(gr, renderer, cont_align, radius)
    last_cont_align = cont_align


## Create a lofted surface. 
#
print("Create lofted surface ...")
loft_surf = modeler.loft(curve_list=curve_list)
#gr.add_geometry(renderer, loft_surf.get_polydata(), color=[0.8, 0.8, 0.8], wire=False)

## Cap the lofted surface. 
#
print("Cap the lofted surface ...")
capped_loft_surf = modeler.cap_surface(loft_surf)
capped_loft_surf.write(file_name=str(script_path / 'loft-parasolid-test'))
face_ids = capped_loft_surf.get_face_ids()
print("  Face IDs: {0:s}".format(str(face_ids)))
gr.add_geometry(renderer, capped_loft_surf.get_polydata(), color=[0.8, 0.8, 0.8], wire=False)

## Show geometry.
#
camera = renderer.GetActiveCamera();
camera.Zoom(0.5)
#camera.SetPosition(center[0], center[1], center[2])
cont1 = contours[start_cid]
center = cont1.get_center()
camera.SetFocalPoint(center[0], center[1], center[2])
gr.display(renderer_window)

