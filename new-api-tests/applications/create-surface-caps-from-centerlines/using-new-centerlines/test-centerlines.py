'''Test vmtk.centerlines() method.

   The centerlines geometry is written to 'centerlines-result.vtp'.
'''
import os
from pathlib import Path
import sv
import sys
import vtk

# Create a modeler.
kernel = sv.modeling.Kernel.POLYDATA
modeler = sv.modeling.Modeler(kernel)

# Read model geometry.
model_file = "mel-surface.vtp"
model = modeler.read(model_file)
model_polydata = model.get_polydata()
print("Model: num nodes: {0:d}".format(model_polydata.GetNumberOfPoints()))
print("Model: num faces: {0:d}".format(model_polydata.GetNumberOfCells()))

'''
file_name = "mel-surface.vtp"
reader = vtk.vtkXMLPolyDataReader()
reader.SetFileName(file_name)
reader.Update()
model_polydata = reader.GetOutput()
print("num nodes: {0:d}".format(model_polydata.GetNumberOfPoints()))
print("num faces: {0:d}".format(model_polydata.GetNumberOfCells()))
'''

## Calculate centelines. 
#
# Use node IDs.
inlet_ids = [1560]
outlet_ids = [2304, 729]
centerlines_polydata = sv.vmtk.centerlines(model_polydata, inlet_ids, outlet_ids)

# Write the capped surface.
file_name = 'test-centerlines.vtp'
writer = vtk.vtkXMLPolyDataWriter()
writer.SetFileName(file_name)
writer.SetInputData(centerlines_polydata)
writer.Update()
writer.Write()


