'''Test TetGen adaptive meshing interface.
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

#print(dir(sv))
print(dir(sv.meshing))
print("Mesh generation adaptive kernel names: {0:s}".format(str(sv.meshing.AdaptiveKernel.names)))

## Create a TetGen Adaptive mesher.
#
adaptive_mesher = sv.meshing.create_adaptive_mesher(sv.meshing.AdaptiveKernel.TETGEN)
print("Mesher: " + str(adaptive_mesher))

## Set meshing options.
#
print("Set meshing options ... ")
options = adaptive_mesher.create_options()
#help(sv.meshing.TetGenAdaptiveOptions)
#options.start_step = 100
#options.end_step = 100
options.step = 100

# options.use_isotropic_meshing = False; 

print("options values: ")
[ print("  {0:s}:{1:s}".format(key,str(value))) for (key, value) in sorted(options.get_values().items()) ]

## Generate an adpative mesh. 
#
results_file_name = str(data_path / 'meshing' / 'all_results.vtu')
model_file_name = str(data_path / 'meshing' / 'cylinder-model.vtp')
adaptive_mesher.generate_mesh(results_file=results_file_name, model_file=model_file_name, options=options, log_file='mesher.log')

## Get the mesh.
#
mesh = adaptive_mesher.get_mesh()
print("Number of adaptive mesh nodes: {0:d}".format(mesh.GetNumberOfPoints()))
print("Number of adaptive mesh elements: {0:d}".format(mesh.GetNumberOfCells()))

