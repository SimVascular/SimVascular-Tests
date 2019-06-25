#import modules
from sv import *
import os

#Check if objects exist
assert Repository.Exists('loft'), "Object loft doesn't exist"
#Cap the cylinder
VMTKUtils.Cap_with_ids('loft','cap',0,0)

#Set solid kernel
Solid.SetKernel('PolyData')
#Create model from polydata
solid = Solid.pySolidModel()
solid.NewObject('cyl')
solid.SetVtkPolyData('cap')
#Extract boundary faces
solid.GetBoundaryFaces(90)
print ("Creating model: \nFaceID found: " + str(solid.GetFaceIds()))
#Write to file 
solid.WriteNative(os.getcwd() + "/cylinder.vtp")
#visualize solid
GUI.ImportPolyDataFromRepos('cap')
