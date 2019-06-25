#import module
from sv import *

#Check if contours exist:
assert Repository.Exists('ctp'), "Contour ctp doesn't exist"
assert Repository.Exists('ct2p'),"Contour ct2p doesn't exist"
# resample contour points
numOutPtsInSegs = 60
Geom.SampleLoop('ctp',numOutPtsInSegs,'ctps')
Geom.SampleLoop('ct2p',numOutPtsInSegs,'ct2ps')
#align contours
Geom.AlignProfile('ctps','ct2ps','ct2psa',0)
#loft contours
srcList = ['ctps','ct2psa']
dstName='loft'
numOutPtsAlongLength = 12
numPtsInLinearSampleAlongLength = 240
numLinearPtsAlongLength = 120
numModes = 20
useFFT = 0
useLinearSampleAlongLength = 1
Geom.LoftSolid(srcList,dstName,numOutPtsInSegs,numOutPtsAlongLength,numLinearPtsAlongLength,numModes,useFFT,useLinearSampleAlongLength)
#visualizing solid
GUI.ImportPolyDataFromRepos('loft')
