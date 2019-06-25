#import modules
from sv import *
import PathDemo

#Check if path exists
assert Repository.Exists('path1'), "Path not found"
#Set contour type
Contour.SetContourKernel('Circle')
#Create new contour 
c =Contour.pyContour()
c.NewObject('ct','path1',0)
#Set control points
c.SetCtrlPtsByRadius([0.,0.,0.],2)
#Creat contour
c.Create()
print ("Contour created: area is: " + str(c.Area()) +
       "; center is: " +str(c.Center()))
#Get PolyData
c.GetPolyData('ctp')


#Another contour
num = PathDemo.p.GetPathPtsNum()
c2 = Contour.pyContour()
c2.NewObject('ct2','path1',num-1)
c2.SetCtrlPtsByRadius([0.,0.,30.],2)
c2.Create()
print ("Contour created: area is: " + str(c2.Area()) + "; center is: " +str(c2.Center()))
c2.GetPolyData('ct2p')

#visualize in GUI
srcList = ['ct','ct2']
GUI.ImportContoursFromRepos('contours',srcList,'path1')




