'''Test capping a PolyData surface with IDs.

   Writes: 'cylinder-surface-capped-with-ids.vtp'
'''
import sv
import sys
import vtk
sys.path.insert(1, '../graphics/')
import graphics as gr

win_width = 500
win_height = 500
renderer, renderer_window = gr.init_graphics(win_width, win_height)

# Create a modeler.
kernel = sv.modeling.Kernel.POLYDATA
modeler = sv.modeling.Modeler(kernel)

## Read cylinder geometry as a model.
#
if True:
    print("Read surface model file ...")
    mdir = "../data/vmtk/"
    file_name = "cylinder-surface.vtp"
    cylinder_model = modeler.read(mdir+file_name)
    model_polydata = cylinder_model.get_polydata()
    print("Cylinder model: num nodes: {0:d}".format(model_polydata.GetNumberOfPoints()))

## Read cylinder geometry as PolyData.
#
else:
    print("Read PolyData file ...")
    reader = vtk.vtkXMLPolyDataReader()
    reader.SetFileName("../data/models/loft-test-interpolate.vtp")
    #reader.SetFileName(mdir+file_name) 
    reader.Update()
    model_polydata = reader.GetOutput()

## Print model array names.
#
num_cells = model_polydata.GetNumberOfCells()
num_arrays = model_polydata.GetCellData().GetNumberOfArrays()
print("model_polydata: ")
print("  Num data arrays: {0:d}".format(num_arrays))

for i in range(num_arrays):
    data_type = model_polydata.GetCellData().GetArray(i).GetDataType()
    data_name = model_polydata.GetCellData().GetArrayName(i)
    cell_data = model_polydata.GetCellData().GetArray(data_name)
    print("  Data name: {0:s}".format(data_name))
    if (data_name == "CapID") or (data_name == "ModelFaceID"):
      ids = set()
      for cell_id in range(num_cells):
          value = cell_data.GetValue(cell_id)
          ids.add(value)
      print("  Number of IDs: {0:d}".format(len(ids)))
      print("  IDs: {0:s}".format(str(ids)))

# Get model center.
com_filter = vtk.vtkCenterOfMass()
com_filter.SetInputData(model_polydata)
com_filter.SetUseScalarsAsWeights(False)
com_filter.Update()
center = com_filter.GetCenter()

## Cap the cylinder surface.
#
#  Creates 'CapID' data array. 
#

## If increment_id=False 
#     1) No 'ModelFaceID' array need be defined
#     2) caps are given an ID = 'fill_id' argument.
#     3) the 'CapID' is created 
#

if False:
    capped_cylinder = sv.vmtk.cap_with_ids(surface=model_polydata, fill_id=2, increment_id=False)

## If increment_id=True
#     1) A 'ModelFaceID' array must be defined
#     2) caps are given an ID = 'fill_id' argument
#     3) the 'CapID' is created 
#
else:
    ## CapIDs = {1, 2, -1}
    #capped_cylinder = sv.vmtk.cap_with_ids(surface=model_polydata)

    ## CapID = {1, -1}
    #capped_cylinder = sv.vmtk.cap_with_ids(surface=model_polydata, fill_id=1, increment_id=False)

    ## CapID = {2, 3, -1},  ModelFaceID = {1, 2, 3} 
    #capped_cylinder = sv.vmtk.cap_with_ids(surface=model_polydata, fill_id=1, increment_id=True)

    ## CapID = {1, 2, -1},  ModelFaceID = {1, 2} 
    capped_cylinder = sv.vmtk.cap_with_ids(surface=model_polydata, fill_id=0, increment_id=True)

    ## CapID = {2, 3, -1},  ModelFaceID = {1, 2, 3} 
    #capped_cylinder = sv.vmtk.cap_with_ids(surface=model_polydata, fill_id=1, increment_id=True)

    ## CapID = {3, 4, -1},  ModelFaceID = {1, 3, 4} 
    #capped_cylinder = sv.vmtk.cap_with_ids(surface=model_polydata, fill_id=2, increment_id=True)

print("Capped cylinder model: num nodes: {0:d}".format(capped_cylinder.GetNumberOfPoints()))
num_cells = capped_cylinder.GetNumberOfCells()
num_arrays = capped_cylinder.GetCellData().GetNumberOfArrays()
print("Capped cylinder model: num data arrays: {0:d}".format(num_arrays))

for i in range(num_arrays):
  data_type = capped_cylinder.GetCellData().GetArray(i).GetDataType()
  data_name = capped_cylinder.GetCellData().GetArrayName(i)
  cell_data = capped_cylinder.GetCellData().GetArray(data_name)
  print("Data name: {0:s}".format(data_name))
  if (data_name == "CapID") or (data_name == "ModelFaceID"):
      ids = set()
      for cell_id in range(num_cells):
          value = cell_data.GetValue(cell_id)
          ids.add(value)
      print("  Number of IDs: {0:d}".format(len(ids)))
      print("  IDs: {0:s}".format(str(ids)))

## Write the capped surface.
file_name = "cylinder-surface-capped-with-ids.vtp"
writer = vtk.vtkXMLPolyDataWriter()
writer.SetFileName(file_name)
writer.SetInputData(capped_cylinder)
writer.Update()
writer.Write()

# Add geometry to vtk renderer.
gr.add_geometry(renderer, model_polydata, color=[0.5, 0.0, 0.0], wire=True)
gr.add_geometry(renderer, capped_cylinder, color=[0.0, 1.0, 0.0], wire=False)

## Show geometry.
#
camera = renderer.GetActiveCamera();
#camera.Zoom(0.5)
#camera.SetPosition(center[0], center[1], center[2])
camera.SetFocalPoint(center[0], center[1], center[2])
gr.display(renderer_window)



