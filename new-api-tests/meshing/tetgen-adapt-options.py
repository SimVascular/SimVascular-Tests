'''Test TetGen adaptive meshing options interface.
'''
import sv

## Create a TetGen Adaptive mesher.
adaptive_mesher = sv.meshing.create_adaptive_mesher(sv.meshing.AdaptiveKernel.TETGEN)
print("Mesher: " + str(adaptive_mesher))


## Set meshing options.
print("Set meshing options ... ")
options = adaptive_mesher.create_options()

options.error_reduction_factor = 0.4

print("options values: ")
[ print("  {0:s}:{1:s}".format(key,str(value))) for (key, value) in sorted(options.get_values().items()) ]

