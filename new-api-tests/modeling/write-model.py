'''Test writting a model. 
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

## Create a modeler.
modeler = None
if len(sys.argv) == 2:
    if sys.argv[1] == 'o':
        modeler = sv.modeling.Modeler(sv.modeling.Kernel.OPENCASCADE)
        print("Create OPENCASCADE modeler")
        file_name = "cylinder-opencascade"
        file_format = "brep"
        file_format = "vtp"
    elif sys.argv[1] == 'p':
        modeler = sv.modeling.Modeler(sv.modeling.Kernel.PARASOLID)
        print("Create PARASOLID modeler")
        file_name = "cylinder-parasolid"

if modeler == None:
    modeler = sv.modeling.Modeler(sv.modeling.Kernel.POLYDATA)
    print("Create POLYDATA modeler")
    file_name = "cylinder-polydata"
    file_format = "vtp"

## Create a cylinder.
print("Create a cylinder ...")
center = [0.0, 0.0, 0.0]
axis = [0.0, 1.0, 0.0]
axis = [1.0, 0.0, 0.0]
radius = 2.0 
length = 4.0 
model = modeler.cylinder(center=center, axis=axis, radius=radius, length=length)
#
model.compute_boundary_faces(angle=60.0)
face_ids = model.get_face_ids()
print("Model Face IDs: {0:s}".format(str(face_ids)))

## Write the model.
model.write(file_name=str(script_path / file_name), format=file_format)

