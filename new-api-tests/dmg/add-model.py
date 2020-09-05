'''Test adding a model to the SV Data Manager.

    This is tested using the Demo Project.
'''
from pathlib import Path
import sv

## Create a cylinder model.
#
modeler = sv.modeling.Modeler(sv.modeling.Kernel.POLYDATA)
cylinder = modeler.cylinder(center=[0.0,0.0,0.0], axis=[1.0,0.0,0.0], radius=4.0, length=16.0)
cylinder.compute_boundary_faces(angle=60.0)

## Add the Python model object under the SV Data Manager 'Model' nodes
#  as a new  node named 'new_demo'.
#
sv.dmg.add_model("cylinder", cylinder)

## Error checking.
#sv.dmg.add_model("cylinder", modeler)
