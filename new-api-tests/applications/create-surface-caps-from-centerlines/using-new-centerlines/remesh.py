'''Test remeshing models.
'''
import os
from pathlib import Path
import sv
import sys
import vtk

## Set some directory paths. 
script_path = Path(os.path.realpath(__file__)).parent
parent_path = Path(os.path.realpath(__file__)).parent.parent

sys.path.insert(1, '../../../graphics/')
import graphics as gr

'''
file_name = 'mel-surface.vtp'
reader = vtk.vtkXMLPolyDataReader()
reader.SetFileName(file_name)
reader.Update()
geometry = reader.GetOutput()

cleaner = vtk.vtkCleanPolyData()
cleaner.SetInputData(geometry)
cleaner.PointMergingOn()
cleaner.ConvertPolysToLinesOn()
tol = 0.010
cleaner.SetAbsoluteTolerance(tol)
cleaner.Update()
cleaned_geometry = cleaner.GetOutput()

surface_filter = vtk.vtkDataSetSurfaceFilter()
surface_filter.SetInputData(cleaner.GetOutput())
surface_filter.Update()
cleaned_geometry = surface_filter.GetOutput()

num_cells = cleaned_geometry.GetNumberOfCells()
points = cleaned_geometry.GetPoints()
min_area = 1e6

for i in range(num_cells):
    cell = cleaned_geometry.GetCell(i)
    cell_pids = cell.GetPointIds()
    pid1 = cell_pids.GetId(0)
    pid2 = cell_pids.GetId(1)
    pid3 = cell_pids.GetId(2)

    pt1 = points.GetPoint(pid1)
    pt2 = points.GetPoint(pid2)
    pt3 = points.GetPoint(pid3)

    area = vtk.vtkTriangle.TriangleArea(pt1, pt2, pt3)

    if area < min_area:
        min_area = area
    
print("min area: {0:g}".format(min_area))
remeshed_geometry = sv.mesh_utils.remesh(cleaned_geometry, hmin=0.4, hmax=0.4)

#writer = vtk.vtkXMLPolyDataWriter()
#writer.SetFileName("cleaned-surface.vtp")
#writer.SetInputData(cleaned_geometry)
#writer.Update()
#writer.Write()
'''

kernel = sv.modeling.Kernel.POLYDATA
modeler = sv.modeling.Modeler(kernel)
file_name = 'mel-surface.vtp'
model = modeler.read(file_name)
try:
    face_ids = model.get_face_ids()
except:
    face_ids = model.compute_boundary_faces(angle=60.0)

model_surf = model.get_polydata()
remesh_model = sv.mesh_utils.remesh(model.get_polydata(), hmin=0.2, hmax=0.2)


writer = vtk.vtkXMLPolyDataWriter()
writer.SetFileName("mel-remesh-surface.vtp")
writer.SetInputData(remesh_model)
writer.Update()
writer.Write()

