'''Test nurbs lofting.
'''
from pathlib import Path
import sv
import sys
import vtk
sys.path.insert(1, '../graphics/')
import graphics as gr
import sv_contour 

win_width = 500
win_height = 500
renderer, renderer_window = gr.init_graphics(win_width, win_height)
radius = 0.05

## Read contours.
contours = sv_contour.read_contours()
num_contours = len(contours)
print("Number of contours {0:d}".format(num_contours))

## Set list of contours to loft.
#
# [TODO] Some values of num_profile_points produces bad surfaces.
#
# num_profile_points = 100   good
# num_profile_points = 60    bad
# num_profile_points = 50    bad
# num_profile_points = 40    bad
# num_profile_points = 30    bad
# num_profile_points = 25    good
# num_profile_points = 20    good
# num_profile_points = 10    good
num_profile_points = 25    
num_out_pts_along_length = 12 

# [TODO] use_distance = False does not work.
#use_distance = False
use_distance = True

## Get interpolated contour profiles and align them. 
#
contour_list = []
start_cid = 0
end_cid = num_contours
#
#start_cid = 15
#end_cid = 17
#
for cid in range(start_cid,end_cid):
    cont_ipd = sv_contour.get_profile_contour(gr, renderer, contours, cid, num_profile_points)
    if cid == start_cid:
        cont_align = cont_ipd
    else:
        cont_align = sv.geometry.align_profile(last_cont_align, cont_ipd, use_distance)
    contour_list.append(cont_align)
    sv_contour.add_sphere(gr, renderer, cont_align, radius)
    last_cont_align = cont_align

## Set options. 
#
# u: logitudinal direction: 
# v: circumferential direction: 
# 
# KnotSpanTypes: average, derivative, equal 
# 
# ParametricSpanType: centripetal, chord, equal
# 
# Linear degree 1, quadratic degree 2, cubic degree 3, and quintic degree 5.
#
options = sv.geometry.LoftNurbsOptions()

## Loft surface.
#
loft_surf = sv.geometry.loft_nurbs(polydata_list=contour_list, loft_options=options)
gr.add_geometry(renderer, loft_surf, color=[0.5, 0.0, 0.0], wire=True)

## Show geometry.
#
camera = renderer.GetActiveCamera();
camera.Zoom(0.5)
#camera.SetPosition(center[0], center[1], center[2])
cont1 = contours[10]
center = cont1.get_center()

camera.SetFocalPoint(center[0], center[1], center[2])
gr.display(renderer_window)

