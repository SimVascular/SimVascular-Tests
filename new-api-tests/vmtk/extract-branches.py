'''Extract branch geometry from an SV centerlines .vtp file.

   Branch geometry is extracted using the 'BranchIdTmp' point array.

   Execute the 'centerlines.py' script to create the 'centerlines-result.vtp' file.
   The geometry for each branch is written to a separate .vtp file.
'''
from collections import defaultdict 
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

win_width = 500
win_height = 500
renderer, renderer_window = gr.init_graphics(win_width, win_height)

# Read centerlines geometry.
file_name = str(script_path / 'centerlines-result.vtp')
reader = vtk.vtkXMLPolyDataReader()
reader.SetFileName(file_name)
reader.Update()
centerlines = reader.GetOutput()

# Get branch IDs.
data_name = 'BranchIdTmp'
branch_ids = centerlines.GetPointData().GetArray(data_name)
vrange = branch_ids.GetRange()
min_id = int(vrange[0])
max_id = int(vrange[1])
num_ids = max_id - min_id + 1
print("[extract-branches] Min branch id: " + str(min_id))
print("[extract-branches] Max branch id: " + str(max_id))

# Create a color lookup table.
lut = vtk.vtkLookupTable()
lut.SetTableRange(min_id, max_id+1)
lut.SetHueRange(0, 1)
lut.SetSaturationRange(1, 1)
lut.SetValueRange(1, 1)
lut.Build()

## Extract branch geometry based on 'BranchIdTmp' ID.
#
for bid in range(min_id,max_id+1):
    thresh = vtk.vtkThreshold()
    thresh.SetInputData(centerlines)
    thresh.ThresholdBetween(bid, bid)
    thresh.SetInputArrayToProcess(0, 0, 0, "vtkDataObject::FIELD_ASSOCIATION_POINTS", data_name)
    thresh.Update()

    surfacefilter = vtk.vtkDataSetSurfaceFilter()
    surfacefilter.SetInputData(thresh.GetOutput())
    surfacefilter.Update()
    geometry = surfacefilter.GetOutput()

    color = [0.0, 0.0, 0.0]
    lut.GetColor(bid, color)
    gr.add_geometry(renderer, geometry, color=color, line_width=4)

    # Write branch geometry.
    file_name = script_path / str('branch_' + str(bid) + '.vtp')
    writer = vtk.vtkXMLPolyDataWriter()
    writer.SetFileName(str(file_name))
    writer.SetInputData(geometry)
    writer.Update()
    writer.Write()

## Show geometry.
gr.display(renderer_window)

