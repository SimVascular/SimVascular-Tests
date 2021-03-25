'''Test the geometry.loft method.
'''
import os
from pathlib import Path
import sv
import sys
import vtk
import sv_contour

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
radius = 0.05

## Read contours.
contours = sv_contour.read_contours()
num_contours = len(contours)
print("Number of contours {0:d}".format(num_contours))

## Set list of contours to loft.
#
# num_profile_points: the number of contour profile points 
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
num_profile_points = 10    
num_profile_points = 25    

## Get interpolated contour profiles and align them. 
#
# [TODO] use_distance = False does not work.
#use_distance = False
use_distance = True
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

## Set loft options.
#
print("Set optons ...")
options = sv.geometry.LoftOptions()

# Use linear interpolation between spline sample points.
#loft_options.interpolate_spline_points = False
options.interpolate_spline_points = True 

# Set the number of points to sample a spline if 
# using linear interpolation between sample points.
options.num_spline_points = 50 
 
# The number of longitudinal points used to sample splines.
options.num_long_points = 200 

## Loft solid. 
#
print("Loft solid ...")
loft_surf = sv.geometry.loft(polydata_list=contour_list, loft_options=options)
#gr.add_geometry(renderer, loft_surf, color=[0.8, 0.8, 0.8], wire=True)
gr.add_geometry(renderer, loft_surf, color=[0.8, 0.8, 0.8], wire=False)

## Write the lofted surface.
#
if options.interpolate_spline_points: 
    file_name = str(script_path / 'loft-test-interpolate.vtp')
else:
    file_name = str(script_path / 'loft-test.vtp')

writer = vtk.vtkXMLPolyDataWriter()
writer.SetFileName(file_name)
writer.SetInputData(loft_surf)
writer.Update()
writer.Write()

## Show geometry.
#
camera = renderer.GetActiveCamera();
camera.Zoom(0.5)
#camera.SetPosition(center[0], center[1], center[2])
cont1 = contours[start_cid]
center = cont1.get_center()
camera.SetFocalPoint(center[0], center[1], center[2])
gr.display(renderer_window)

