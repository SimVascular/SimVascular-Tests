try:
    import Repository
    import Solid
    import Contour
    import CircleContour
    import Path
    import Geom
    import VMTKUtils
except:
    from __init__ import *

def demo_create_model (dstdir):
  # just copy the model for now
  try:
      Repository.Delete("cyl")
  except:
      pass
  cyl=Solid.pySolidModel()
  cyl.ReadNative("cyl","cylinder.vtp")
  from shutil import copyfile
  copyfile("cylinder.vtp",dstdir + "/cylinder.vtp")
  copyfile("cylinder.vtp.facenames",dstdir + "/cylinder.vtp.facenames")  
  return dstdir+"/cylinder.vtp"
  
  
def demo_create_cylinder (dstdir):
  # hardcode path for testing purpose
  try:
      Repository.Delete("cyl")
      Repository.Delete("resultCyl")
  except:
      pass
  cyl=Solid.pySolidModel()
  ctrL=[0.,0.,15.]
  axisL=[0.,0.,1.]
  cyl.Cylinder('cyl',2.,30.,ctrL,axisL)
  cyl.GetPolyData('resultCyl',0.5)
  cyl.GetBoundaryFaces(90)
  print ("Creating model: \nFaceID found: " + str(cyl.GetFaceIds()))
  cyl.WriteNative(dstdir + "/cylinder.vtp")
  from shutil import copyfile
  copyfile("cylinder.vtp.facenames2",dstdir + "/cylinder.vtp.facenames")  
  return dstdir+"/cylinder.vtp"
  
  
def demo_loft_cylinder(dstdir):
    Contour.SetContourKernel('Circle')
    try:
        Repository.Delete('path')
        Repository.Delete('ct')
        Repository.Delete('ct2')
    except:
        pass
    #generate path
    p = Path.pyPath()
    p.NewObject('path')
    p.AddPoint([0.,0.,0.])
    p.AddPoint([0.,0.,30.])
    p.CreatePath()
    num = p.GetPathPtsNum()
    
    #create two contours
    c = Contour.pyContour()
    c.NewObject('ct','path',0)
    c.SetCtrlPtsByRadius([0.,0.,0.],2)
    c.Create()
    print ("Contour created: area is: " + str(c.Area()) + "; center is: " +str(c.Center()))
    
    c2 = Contour.pyContour()
    c2.NewObject('ct2','path',num-1)
    c2.SetCtrlPtsByRadius([0.,0.,30.],2)
    c2.Create()
    print ("Contour created: area is: " + str(c2.Area()) + "; center is: " +str(c2.Center()))
    c.GetPolyData('ctp')
    c2.GetPolyData('ct2p')
    
    #processing the contours
    numOutPtsAlongLength = 12
    numPtsInLinearSampleAlongLength = 240
    numLinearPtsAlongLength = 120
    dstName='loft'
    numOutPtsInSegs = 60
    numModes = 20
    useFFT = 0
    useLinearSampleAlongLength = 1

    Geom.SampleLoop('ctp',numOutPtsInSegs,'ctps')
    Geom.SampleLoop('ct2p',numOutPtsInSegs,'ct2ps')
    Geom.AlignProfile('ctps','ct2ps','ct2psa',0)

    srcList = ['ctps','ct2psa']
    Geom.LoftSolid(srcList,dstName,numOutPtsInSegs,numOutPtsAlongLength,numLinearPtsAlongLength,numModes,useFFT,useLinearSampleAlongLength)
    #cap the cylinder
    VMTKUtils.Cap_with_ids(dstName,'cap',0,0)

    solid = Solid.pySolidModel()
    solid.NewObject('cyl')
    solid.SetVtkPolyData('cap')
    solid.GetBoundaryFaces(90)
    print ("Creating model: \nFaceID found: " + str(solid.GetFaceIds()))
    solid.WriteNative(dstdir + "/cylinder.vtp")
    
    Repository.Delete('ctp')
    Repository.Delete('ct2p')
    Repository.Delete('ct2ps')
    Repository.Delete(dstName)
    Repository.Delete('cap')
    Repository.Delete('path')
    
    from shutil import copyfile
    copyfile("cylinder.vtp.facenames2",dstdir + "/cylinder.vtp.facenames")  
    return dstdir+"/cylinder.vtp"
