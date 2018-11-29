#import modules
from sv import *

#Create new path object
p = Path.pyPath()
p.NewObject('path1')

#Control point operations
p.AddPoint([0.,0.,0.])
p.AddPoint([0.,0.,20.])
p.RemovePoint(1)
p.AddPoint([0.,0.,25])
p.MovePoint([0.,0.,30.],1)
p.PrintPoints()

#Generate path points
p.CreatePath()

#Check if exist in repository
print(Repository.Exists('path1'))
print(Repository.List())

#import to visualize in the repository
GUI.ImportPathFromRepos('path1')
GUI.ImportPathFromRepos('path1','Paths')

#export existing path to repository
#GUI.ExportPathToRepos('aorta','aortaPath')
#q = Path.pyPath()
#q.GetObject('aortaPath')
#q.PrintPoints()
