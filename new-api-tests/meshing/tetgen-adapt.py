'''Test TetGen adaptive meshing interface.
'''
import sv
import sys
import vtk
sys.path.insert(1, '../graphics/')
import graphics as gr

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
results_file_name = '../data/meshing/all_results.vtu'
model_file_name = '../data/meshing/cylinder-model.vtp'
adaptive_mesher.generate_mesh(results_file=results_file_name, model_file=model_file_name, options=options, log_file='mesher.log')

## Get the mesh.
#
mesh = adaptive_mesher.get_mesh()
print("Number of adaptive mesh nodes: {0:d}".format(mesh.GetNumberOfPoints()))
print("Number of adaptive mesh elements: {0:d}".format(mesh.GetNumberOfCells()))

