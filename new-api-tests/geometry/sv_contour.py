
import os
from pathlib import Path
import sv
import vtk

## Set some directory paths. 
script_path = Path(os.path.realpath(__file__)).parent
parent_path = Path(os.path.realpath(__file__)).parent.parent
data_path = parent_path / 'data'

def get_profile_contour(gr, renderer, contours, cid, npts):
    cont = contours[cid]
    gr.create_contour_geometry(renderer, cont)
    cont_pd = cont.get_polydata()
    cont_ipd = sv.geometry.interpolate_closed_curve(polydata=cont_pd, number_of_points=npts)
    gr.add_geometry(renderer, cont_ipd)
    return cont_ipd

def add_sphere(gr, renderer, cont_pd, radius):
    """ Show two points on a profile.
    """
    pt = 3*[0.0]
    cont_pd.GetPoints().GetPoint(0, pt)
    gr.add_sphere(renderer, pt, radius)
    cont_pd.GetPoints().GetPoint(4, pt)
    gr.add_sphere(renderer, pt, radius, color=[0,1,0])

## Read an SV contour group file. 
#
def read_contours():
    file_name = str(data_path / 'DemoProject' / 'Segmentations' / 'aorta.ctgr')
    print("Read SV ctgr file: {0:s}".format(file_name))
    contour_group = sv.segmentation.Series(file_name)
    num_conts = contour_group.get_num_segmentations()
    contours = []

    for i in range(num_conts):
        cont = contour_group.get_segmentation(i)
        contours.append(cont)

    print("Number of contours: {0:d}".format(num_conts))
    return contours

def get_polydata(contour):
    return contour.get_polydata()
    '''
    coords = contour.get_contour_points()
    num_pts = len(coords)

    ## Create contour geometry points and line connectivity.
    #
    points = vtk.vtkPoints()
    points.SetNumberOfPoints(num_pts)
    lines = vtk.vtkCellArray()
    lines.InsertNextCell(num_pts)
    n = 0
    for pt in coords:
        points.SetPoint(n, pt[0], pt[1], pt[2])
        lines.InsertCellPoint(n)
        n += 1
    #_for pt in coords

    geom = vtk.vtkPolyData()
    geom.SetPoints(points)
    geom.SetLines(lines)
    return geom
    '''

