'''Test lofting and unioning two vessels. 
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

def get_profile_contour(gr, renderer, contours, cid, npts):
    '''Interpolate a contour profile to the given numner of points.
    '''
    cont = contours[cid]
    use_control_points = False

    # Get the profile from the control points (very coarse).
    #
    if use_control_points:
        cont_pd = cont.get_polydata()
        cont_ipd = sv.geometry.interpolate_closed_curve(polydata=cont_pd, number_of_points=npts)

    # Get the profile from the sampled points (very smooth).
    #
    else:
        coords = cont.get_points()
        num_coords = len(coords)
        points = vtk.vtkPoints()
        points.SetNumberOfPoints(num_coords)
        lines = vtk.vtkCellArray()

        for i in range(len(coords)):
            pt = coords[i]
            points.SetPoint(i, pt[0], pt[1], pt[2])
            if i > 0 and i < num_coords:
                cell = [i-1,i]
                lines.InsertNextCell(2,cell)

        cell = [num_coords-1,0]
        lines.InsertNextCell(2,cell)
        lines.InsertCellPoint(0)

        cont_pd = vtk.vtkPolyData()
        cont_pd.SetPoints(points)
        cont_pd.SetLines(lines)

    gr.add_geometry(renderer, cont_pd, color=[0,0,1], line_width=2.0)

    cont_ipd = sv.geometry.interpolate_closed_curve(polydata=cont_pd, number_of_points=npts)

    return cont_ipd

def read_contours(name):
    '''Read an SV contour group file.
    '''
    file_name = str(data_path / 'DemoProject' / 'Segmentations' / str(name+'.ctgr'))
    print("Read SV ctgr file: {0:s}".format(file_name))
    contour_group = sv.segmentation.Series(file_name)
    num_conts = contour_group.get_num_segmentations()
    contours = []

    for i in range(num_conts):
        cont = contour_group.get_segmentation(i)
        contours.append(cont)

    return contours

def align_contours(gr, renderer, contours):
    '''Create new contours that have their start points aligned.
    '''
    curve_list = [] 
    start_cid = 0
    end_cid = len(contours)
    use_distance = True
    num_profile_points = 25
    tolerance = 1e-3
    aligned_contours = []

    for cid in range(start_cid,end_cid):
        cont_ipd = get_profile_contour(gr, renderer, contours, cid, num_profile_points)

        if cid == start_cid:
            cont_align = cont_ipd 
        else:
            cont_align = sv.geometry.align_profile(last_cont_align, cont_ipd, use_distance)

        last_cont_align = cont_align
        aligned_contours.append(cont_align)

        # Show the contour's start point marked by a sphere.
        points = last_cont_align.GetPoints()
        center = points.GetPoint(0)
        gr.add_sphere(renderer, center=center, radius=0.1, color=[1.0, 1.0, 1.0])

    return aligned_contours
                
def create_lofted_surface(gr, renderer, contours):
    '''Create a lofted surface passing through a set of contours. 
    '''
    print("Create lofted surface ...")
    options = sv.geometry.LoftOptions()
    options.interpolate_spline_points = True
    options.num_spline_points = 400 # contols number of elements along vessel length
    options.num_long_points = 200 # controls how well matches initial geometry (more curved vessels requires greater values)
    lofted_surface = sv.geometry.loft(polydata_list=contours, loft_options=options)
    lofted_capped = sv.vmtk.cap(surface=lofted_surface, use_center=False)
    #gr.add_geometry(renderer, lofted_capped, color=[1.0,0.0,0.0])

    normals = vtk.vtkPolyDataNormals()
    normals.SplittingOff()
    normals.ConsistencyOn()
    normals.AutoOrientNormalsOn()
    normals.ComputeCellNormalsOn()
    normals.ComputePointNormalsOff()
    normals.SetInputData(lofted_capped)
    normals.Update()

    oriented_surface = normals.GetOutput()
    return oriented_surface 

def union_surfaces(surface1, surface2):
    '''Union two surfaces into a single solid model.
    '''
    model1 = sv.modeling.PolyData()
    model1.set_surface(surface1)

    model2 = sv.modeling.PolyData()
    model2.set_surface(surface2)

    modeler = sv.modeling.Modeler(sv.modeling.Kernel.POLYDATA)
    union_model = modeler.union(model1=model1, model2=model2)

    return union_model 

# Create a graphics window.
win_width = 1000
win_height = 1000
renderer, renderer_window = gr.init_graphics(win_width, win_height)

# Create a lofted and capped surface for the aorta segmentations (contours).
aorta_contours = read_contours('aorta')
aorta_contours_aligned = align_contours(gr, renderer, aorta_contours)
aorta_surface = create_lofted_surface(gr, renderer, aorta_contours_aligned)
gr.add_geometry(renderer, aorta_surface, color=[1,0,0], wire=True)

# Create a lofted and capped surface for the right_iliac segmentations (contours).
iliac_contours = read_contours('right_iliac')
iliac_contours_aligned = align_contours(gr, renderer, iliac_contours)
iliac_surface = create_lofted_surface(gr, renderer, iliac_contours_aligned)
gr.add_geometry(renderer, iliac_surface, color=[0,1,0], wire=True)

# Union the two surfaces.
union_model = union_surfaces(aorta_surface, iliac_surface)
union_surface = union_model.get_polydata()
gr.add_geometry(renderer, union_surface, color=[1,1,0])

# Write the model. 
file_name = "union-vessels"
union_model.write(file_name=file_name, format="vtp")

gr.display(renderer_window)

