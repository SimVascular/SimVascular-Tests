'''Test nurbs lofting.
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
num_profile_points = 134
num_profile_points = 60

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
    #print("----- align cont {0:d} ----- ".format(cid))
    #print("  Number of points: " + str(cont_align.GetNumberOfPoints()))
    #print("  Number of cells: " + str(cont_align.GetNumberOfCells()))

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
loft_surf = sv.geometry.loft_nurbs(polydata_list=contour_list, loft_options=options, num_sections=12)
print("Loft surface: ")
print("  Number of points: " + str(loft_surf.GetNumberOfPoints()))
print("  Number of cells: " + str(loft_surf.GetNumberOfCells()))
loft_capped = sv.vmtk.cap(surface=loft_surf, use_center=False)
#gr.add_geometry(renderer, loft_capped, color=[1.0, 1.0, 1.0], edges=True)
#gr.add_geometry(renderer, loft_surf, color=[1.0, 1.0, 1.0], wire=False)
print("Capped loft surface: ")
print("  Number of points: " + str(loft_capped.GetNumberOfPoints()))
print("  Number of cells: " + str(loft_capped.GetNumberOfCells()))
file_name = str(script_path / "capped-loft-surface.vtp")
writer = vtk.vtkXMLPolyDataWriter()
writer.SetFileName(file_name)
writer.SetInputData(loft_capped)
writer.Update()
writer.Write()

## Remesh suface.
#
modeler = sv.modeling.Modeler(sv.modeling.Kernel.POLYDATA)
model = sv.modeling.PolyData()
model.set_surface(surface=loft_capped)
model.compute_boundary_faces(angle=60.0)
remesh_model = sv.mesh_utils.remesh(model.get_polydata(), hmin=0.2, hmax=0.2)
model.set_surface(surface=remesh_model)
model.compute_boundary_faces(angle=60.0)
model.write("loft-nurb-test", format="vtp")
polydata = model.get_polydata()
gr.add_geometry(renderer, polydata, color=[1.0, 1.0, 1.0], edges=True)
print("Model: ")
print("  Number of points: " + str(polydata.GetNumberOfPoints()))
print("  Number of cells: " + str(polydata.GetNumberOfCells()))

## Show geometry.
#
camera = renderer.GetActiveCamera();
camera.Zoom(0.5)
#camera.SetPosition(center[0], center[1], center[2])
cont1 = contours[10]
center = cont1.get_center()

camera.SetFocalPoint(center[0], center[1], center[2])
gr.display(renderer_window)

