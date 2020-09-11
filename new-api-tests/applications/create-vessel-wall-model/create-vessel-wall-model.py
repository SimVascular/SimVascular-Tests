'''This script is used to create a model of a vessel wall by performing a Boolean 
   subtract operation between models of the inner and outer vessel contours.
'''
import os, pwd
import sys
import sv
import vtk
from math import sqrt
sys.path.insert(1, '../../graphics/')
import graphics as gr

def translate_polydata(polydata, normal, scale=1.0):
    '''Translate polydata in a direction given by 'normal'.
    '''
    transform = vtk.vtkTransform()
    tx = scale * normal[0]
    ty = scale * normal[1]
    tz = scale * normal[2]
    transform.Translate(tx, ty, tz)
    transformFilter = vtk.vtkTransformFilter()
    transformFilter.SetInputData(polydata)
    transformFilter.SetTransform(transform)
    transformFilter.Update()
    return transformFilter.GetOutput()

def expand_polydata(polydata, center, dist=1.0):
    '''Create a polydata object such that its points are 'dist' distance from the 
       points of the given 'polydata'. 
    '''
    num_pts = polydata.GetNumberOfPoints()
    num_cells = polydata.GetNumberOfCells()
    polydata_pts = polydata.GetPoints()
    polydata_cells = polydata.GetLines()

    points = vtk.vtkPoints()
    points.SetNumberOfPoints(num_pts)
    lines = vtk.vtkCellArray()
    n = 0
    pt = 3*[0.0]
    spt = 3*[0.0]
    v = 3*[0.0]
    for i in range(num_pts):
        polydata_pts.GetPoint(i, pt)
        v = [ pt[j] - center[j] for j in range(3) ]
        mag = sqrt(sum([v[j]*v[j] for j in range(3)]))
        s = dist / mag
        spt = [ pt[j] + s*v[j] for j in range(3) ]
        points.SetPoint(n, spt[0], spt[1], spt[2])
        n += 1

    scaled_polydata = vtk.vtkPolyData()
    scaled_polydata.SetPoints(points)
    scaled_polydata.SetLines(polydata_cells)
    scaled_polydata.BuildLinks()

    return scaled_polydata 

def create_lofted_solid(renderer, segmentations, scale_contours=False, wall_thickness=0.0):
    '''Create a lofted solid from a list of segmentations.
    '''
    num_contours = len(segmentations)
    num_profile_points = 25
    num_profile_points = 60
    num_profile_points = 80
    use_distance = True
    contour_list = []

    for i,seg in enumerate(segmentations):
        cont_pd = seg.get_polydata()
        cont_ipd = sv.geometry.interpolate_closed_curve(polydata=cont_pd, number_of_points=num_profile_points)

        if scale_contours: 
            center = seg.get_center()
            cont_ipd = expand_polydata(cont_ipd, center, wall_thickness)
        else:
            if i == 0:
                normal = seg.get_normal()
                cont_ipd = translate_polydata(cont_ipd, normal, scale=-1.0)
            elif i == len(segmentations) - 1:
                normal = seg.get_normal()
                cont_ipd = translate_polydata(cont_ipd, normal, scale=1.0)

        if i == 0:
            cont_align = cont_ipd
        else:
            cont_align = sv.geometry.align_profile(last_cont_align, cont_ipd, use_distance)
        contour_list.append(cont_align)
        last_cont_align = cont_align

    ## Create lofted surface. 
    #
    loft_with_nurbs = False
    loft_with_nurbs = True

    if loft_with_nurbs:
        print("Creating a lofted surface using NURBS.")
        options = sv.geometry.LoftNurbsOptions()
        loft_surf = sv.geometry.loft_nurbs(polydata_list=contour_list, loft_options=options, num_divisions=12)

    else:
        ## Set lofting options.
        options = sv.geometry.LoftOptions()

        # Use linear interpolation between spline sample points.
        #loft_options.interpolate_spline_points = False
        options.interpolate_spline_points = True
        # Set the number of points to sample a spline if 
        # using linear interpolation between sample points.
        options.num_spline_points = 50
        # The number of longitudinal points used to sample splines.
        options.num_long_points = 100

        ## Create a lofted surface. 
        loft_surf = sv.geometry.loft(polydata_list=contour_list, loft_options=options)
        #gr.add_geometry(renderer, loft_surf, color=[0.8, 0.8, 0.8], wire=False)
        #gr.add_geometry(renderer, loft_surf, color=[0.8, 0.8, 0.8], wire=True)

    ## Create a capped lofted surface. 
    loft_capped = sv.vmtk.cap(surface=loft_surf, use_center=False)
    #gr.add_geometry(renderer, loft_solid, color=[0.8, 0.8, 0.8], wire=False)
    return loft_capped

## Create renderer and graphics window.
win_width = 500
win_height = 500
renderer, renderer_window = gr.init_graphics(win_width, win_height)

## Read in segmentations.
model_name = 'aorta'
model_name = 'right_iliac'
file_name = "../../data/DemoProject/Segmentations/" + model_name + ".ctgr"
print("Read SV ctgr file: {0:s}".format(file_name))
series = sv.segmentation.Series(file_name)

## Get segmentations.
time = 0
num_segs = series.get_num_segmentations(time)
segmentations = [ series.get_segmentation(sid, time) for sid in range(num_segs) ] 
print("Number of segmentations: {0:d}".format(len(segmentations)))

show_models = True
show_models = False

## Create inner lofted solid.
inner_surface = create_lofted_solid(renderer, segmentations, scale_contours=False)
print("Inner loft surface: ")
print("  Number of points: " + str(inner_surface.GetNumberOfPoints()))
print("  Number of cells: " + str(inner_surface.GetNumberOfCells()))

if show_models:
    gr.add_geometry(renderer, inner_surface, color=[0.8, 0.0, 0.0], wire=False)
# Write the surface.
'''
file_name = "inner-surface.vtp"
writer = vtk.vtkXMLPolyDataWriter()
writer.SetFileName(file_name)
writer.SetInputData(inner_surface)
writer.Update()
writer.Write()
'''

## Create outer lofted solid.
wall_thickness = 0.25
outer_surface = create_lofted_solid(renderer, segmentations, scale_contours=True, wall_thickness=wall_thickness)
if show_models:
    gr.add_geometry(renderer, outer_surface, color=[0.0, 0.8, 0.0], wire=False)
# Write the surface. 
'''
file_name = "outer-surface.vtp"
writer = vtk.vtkXMLPolyDataWriter()
writer.SetFileName(file_name)
writer.SetInputData(outer_surface)
writer.Update()
writer.Write()
'''

## Create solid models from the lofted surfaces. 
modeler = sv.modeling.Modeler(sv.modeling.Kernel.POLYDATA)
inner_model = sv.modeling.PolyData()
inner_model.set_surface(surface=inner_surface)
face_ids = inner_model.compute_boundary_faces(angle=60.0)
edge_size = 1.0
edge_size = 0.2
remesh_inner_model = sv.mesh_utils.remesh(inner_model.get_polydata(), hmin=edge_size, hmax=edge_size)
inner_model.set_surface(surface=remesh_inner_model)
inner_model.compute_boundary_faces(angle=60.0)
#inner_model.write("inner-model", format="vtp")
print("Inner_model: ")
print("  Number of points: " + str(inner_model.get_polydata().GetNumberOfPoints()))
print("  Number of cells: " + str(inner_model.get_polydata().GetNumberOfCells()))
#
outer_model = sv.modeling.PolyData()
outer_model.set_surface(surface=outer_surface)
outer_model.compute_boundary_faces(angle=60.0)
remesh_outer_model = sv.mesh_utils.remesh(outer_model.get_polydata(), hmin=0.2, hmax=0.2)
outer_model.set_surface(surface=remesh_outer_model)
outer_model.compute_boundary_faces(angle=60.0)
#outer_model.write("outer-model", format="vtp")

## Perform a Boolean subtract.
do_subtract = False
do_subtract = True
if do_subtract:
    vessel_wall = modeler.subtract(main=outer_model, subtract=inner_model)
    # Not computing boundary faces returns three faces: inner and outer surface are one face.
    face_ids = vessel_wall.get_face_ids()
    print("Vessel wall model face IDs (before compute_boundary_faces): " + str(face_ids))
    vessel_wall.compute_boundary_faces(angle=60.0)
    face_ids = vessel_wall.get_face_ids()
    print("Vessel wall model face IDs: " + str(face_ids))
    vessel_wall_pd = vessel_wall.get_polydata()
    vessel_wall.write(model_name+"-model", format="vtp")
    '''
    remesh_vessel_wall = sv.mesh_utils.remesh(vessel_wall_pd, hmin=0.2, hmax=0.2)
    vessel_wall.set_surface(surface=remesh_vessel_wall)
    vessel_wall.compute_boundary_faces(angle=60.0)
    vessel_wall_pd = vessel_wall.get_polydata()
    '''

    '''
    for faceID in face_ids:
        face_polydata = vessel_wall.get_face_polydata(face_id=faceID)
        print("----- face {0:d} -----".format(faceID))
        print("  Num points: " + str(face_polydata.GetNumberOfPoints()))
        print("  Num cells: " + str(face_polydata.GetNumberOfCells()))
    '''

    gr.add_geometry(renderer, vessel_wall_pd, color=[0.0, 0.5, 0.8], edges=True, wire=False)
    file_name = "vessel-wall.vtp"
    writer = vtk.vtkXMLPolyDataWriter()
    writer.SetFileName(file_name)
    writer.SetInputData(vessel_wall_pd)
    writer.Update()
    writer.Write()

## Show segmentations.
for seg in segmentations:
    gr.create_segmentation_geometry(renderer, seg, color=[1.0,1.0,1.0])
    center = seg.get_center()
    #cont_pd = seg.get_polydata()
    #gr.add_geometry(renderer, cont_pd, color=[1.0,0.0,0.0])
    #scont_ipd = expand_polydata(cont_pd, center, 2.0)
    #gr.add_geometry(renderer, scont_ipd, color=[1.0,0.0,0.0])

## Display window.
gr.display(renderer_window)

