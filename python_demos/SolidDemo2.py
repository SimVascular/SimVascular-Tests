#import modules
from sv import *

#Set solid kernel
Solid.SetKernel('PolyData')
#create fisrt cylinder
ctr=[0,0,0]
axis = [0.,0.,1.]
cyl = Solid.pySolidModel()
cyl.Cylinder('solidcyl',1.5,10,ctr,axis)
#create second cylinder
cyl2 = Solid.pySolidModel()
cyl2.Cylinder('solidcyl2',1.,10,ctr,axis)
#Boolean operations
vessel=Solid.pySolidModel()
vessel.Subtract('vessel','solidcyl','solidcyl2')
vessel.GetPolyData('vesselpoly',0)
#visualize polydata
GUI.ImportPolyDataFromRepos('vesselpoly')
