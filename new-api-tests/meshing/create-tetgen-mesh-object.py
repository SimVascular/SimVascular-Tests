'''Test creating a TetGen object. 
'''
import sv
import sys
import vtk
sys.path.insert(1, '../graphics/')
import graphics as gr

## Create a TetGen mesher.
#
mesher = sv.meshing.TetGen()

# or 
#mesher = sv.meshing.create_mesher(sv.meshing.Kernel.TETGEN)

print("Mesher: " + str(mesher))
print("Mesher kernel: " + str(mesher.get_kernel()))

