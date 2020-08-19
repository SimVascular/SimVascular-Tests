'''Test the Modeler class. 
'''
import sv
import sys
import vtk
sys.path.insert(1, '../graphics/')
import graphics as gr

# Create a modeler.
modeler = sv.modeling.Modeler(sv.modeling.Kernel.POLYDATA)
print("Modeler type: " + str(type(modeler)))
print("Modeler kernel: " + str(modeler.kernel))


