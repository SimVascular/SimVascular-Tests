'''Test Circle segmentation exceptions. 
'''
from sv import segmentation
import sys
import vtk
sys.path.insert(1, '../graphics/')
import graphics as gr

## Create a segmentation using the Circle class. 
#
print("Create circle segmentation ...")
radius = 1.0
center = [0.0, 0.0, 0.0]
#
plane = vtk.vtkPlane()
plane.SetOrigin(center);
plane_normal = [0.0, 1.0, 0.0]
plane.SetNormal(plane_normal)
#

try:
   #seg = segmentation.Circle(radius='a', center=[1.0,0.0,0.0], normal=[1.0, 0.0, 0.0])
   seg = segmentation.Circle(radius=1.0, center=[1.0,0.0,0.0], normal=[1.0])

except TypeError as err:
   print("TypeError: ", err)

except segmentation.Error as err:
   print("Exception type: ", type(err))
   print("Error: ", err)

except Exception as err:
   print("Unexpected error: ", err)
   print(type(err))

