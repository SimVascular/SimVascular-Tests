'''Test vmtk.cap() method.

   Writes: 'cylinder-surface-capped.vtp'
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

## Create a graphics window.
#
win_width = 500
win_height = 500
renderer, renderer_window = gr.init_graphics(win_width, win_height)

## Read cylinder geometry as a model.
#
print("Read surface model file ...")
file_name = str(data_path / 'vmtk' / 'cylinder-surface.vtp')
modeler = sv.modeling.Modeler(sv.modeling.Kernel.POLYDATA)
cylinder_model = modeler.read(file_name)
cylinder_polydata = cylinder_model.get_polydata()
cylinder_polydata.GetCellData().RemoveArray('ModelFaceID')
print("Cylinder model: num nodes: {0:d}".format(cylinder_polydata.GetNumberOfPoints()))
print("Cylinder model: num cells: {0:d}".format(cylinder_polydata.GetNumberOfCells()))
file_name = str(script_path / "cylinder_polydata.vtp")
writer = vtk.vtkXMLPolyDataWriter()
writer.SetFileName(file_name)
writer.SetInputData(cylinder_polydata)
writer.Update()
writer.Write()

## Get cylinder center.
#
com_filter = vtk.vtkCenterOfMass()
com_filter.SetInputData(cylinder_polydata)
com_filter.SetUseScalarsAsWeights(False)
com_filter.Update()
center = com_filter.GetCenter()

## Cap the cylinder surface.
#
print("Cap cylinder ... ")
#capped_cylinder = sv.vmtk.cap(surface=cylinder_polydata, use_center=False)
capped_cylinder = sv.vmtk.cap(surface=cylinder_polydata, use_center=True)
print("Capped cylinder model: num nodes: {0:d}".format(capped_cylinder.GetNumberOfPoints()))
num_cells = capped_cylinder.GetNumberOfCells()
num_arrays = capped_cylinder.GetCellData().GetNumberOfArrays()
print("Capped cylinder model: num data arrays: {0:d}".format(num_arrays))

for i in range(num_arrays):
  data_type = capped_cylinder.GetCellData().GetArray(i).GetDataType()
  data_name = capped_cylinder.GetCellData().GetArrayName(i)
  cell_data = capped_cylinder.GetCellData().GetArray(data_name)
  print("  Data name: {0:s}".format(data_name))
  if data_name == "CenterlineCapID" or data_name == "ModelFaceID":
      ids = set()
      for cell_id in range(num_cells):
          value = cell_data.GetValue(cell_id)
          ids.add(value)
      print("  Number of IDs: {0:d}".format(len(ids)))
      print("  IDs: {0:s}".format(str(ids)))

## Write the capped surface.
#
print("Write the capped surface.")
file_name = str(script_path / "cylinder-surface-capped.vtp")
writer = vtk.vtkXMLPolyDataWriter()
writer.SetFileName(file_name)
writer.SetInputData(capped_cylinder)
writer.Update()
writer.Write()

## Create a model from the capped surface.
print("Create a model from the capped surface.")
capped_model = sv.modeling.PolyData()
capped_model.set_surface(surface=capped_cylinder)
face_ids = capped_model.compute_boundary_faces(angle=60.0)
print("Model face IDs: " + str(face_ids))
capped_model.write("cylinder-surface-capped-model", "vtp")

# Add geometry to vtk renderer.
#gr.add_geom(renderer, cylinder_polydata, color=[0.5, 0.0, 0.0], wire=True)
gr.add_geometry(renderer, capped_cylinder, color=[0.0, 1.0, 0.0], wire=True)

## Show geometry.
#
camera = renderer.GetActiveCamera();
#camera.Zoom(0.5)
#camera.SetPosition(center[0], center[1], center[2])
camera.SetFocalPoint(center[0], center[1], center[2])
gr.display(renderer_window)



