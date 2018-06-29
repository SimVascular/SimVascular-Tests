import pyRepository
import pySolid2
import pyContour
import pyCircleContour
import pyPath
import pyGeom
import pyVMTKUtils

def demo_create_model (dstdir):
  # just copy the model for now
  try:
      pyRepository.repos_delete("cyl")
  except:
      pass
  cyl=pySolid2.pySolidModel()
  cyl.solid_readNative("cyl","cylinder.vtp")
  from shutil import copyfile
  copyfile("cylinder.vtp",dstdir + "/cylinder.vtp")
  copyfile("cylinder.vtp.facenames",dstdir + "/cylinder.vtp.facenames")  
  return dstdir+"/cylinder.vtp"
  
  
def demo_create_cylinder (dstdir):
  # hardcode path for testing purpose
  try:
      pyRepository.repos_delete("cyl")
      pyRepository.repos_delete("resultCyl")
  except:
      pass
  cyl=pySolid2.pySolidModel()
  ctrL=[0.,0.,15.]
  axisL=[0.,0.,1.]
  cyl.solid_cylinder('cyl',2.,30.,ctrL,axisL)
  cyl.GetPolyData('resultCyl',0.5)
  cyl.GetBoundaryFaces(90)
  print "Creating model: \nFaceID found: " + str(cyl.GetFaceIds())
  cyl.WriteNative(dstdir + "/cylinder.vtp")
  from shutil import copyfile
  copyfile("cylinder.vtp.facenames2",dstdir + "/cylinder.vtp.facenames")  
  return dstdir+"/cylinder.vtp"
  
  
def demo_loft_cylinder(dstdir):
    pyContour.SetContourKernel('Circle')
    try:
        pyRepository.repos_delete('path')
        pyRepository.repos_delete('ct')
        pyRepository.repos_delete('ct2')
    except:
        pass
    #generate path
    p = pyPath.pyPath()
    p.path_newObject('path')
    p.path_addPoint([0.,0.,0.])
    p.path_addPoint([0.,0.,30.])
    p.path_createPath()
    num = p.path_getPathPtsNum()
    
    #create two contours
    c = pyContour.pyContour()
    c.contour_newObject('ct','path',0)
    c.contour_setCtrlPtsByRadius([0.,0.,0.],2)
    c.contour_create()
    print "Contour created: area is: " + str(c.contour_area()) + "; center is: " +str(c.contour_center())
    
    c2 = pyContour.pyContour()
    c2.contour_newObject('ct2','path',num-1)
    c2.contour_setCtrlPtsByRadius([0.,0.,30.],2)
    c2.contour_create()
    print "Contour created: area is: " + str(c2.contour_area()) + "; center is: " +str(c2.contour_center())
    c.contour_getPolyData('ctp')
    c2.contour_getPolyData('ct2p')
    
    #processing the contours
    numOutPtsAlongLength = 12
    numPtsInLinearSampleAlongLength = 240
    numLinearPtsAlongLength = 120
    dstName='loft'
    numOutPtsInSegs = 60
    numModes = 20
    useFFT = 0
    useLinearSampleAlongLength = 1

    pyGeom.geom_sampleLoop('ctp',numOutPtsInSegs,'ctps')
    pyGeom.geom_sampleLoop('ct2p',numOutPtsInSegs,'ct2ps')
    pyGeom.geom_alignProfile('ctps','ct2ps','ct2psa',0)

    
    srcList = ['ctps','ct2psa']
    pyGeom.geom_loftSolid(srcList,dstName,numOutPtsInSegs,numOutPtsAlongLength,numLinearPtsAlongLength,numModes,useFFT,useLinearSampleAlongLength)
    #cap the cylinder
    pyVMTKUtils.geom_cap_with_ids(dstName,'cap',0,0)

    solid = pySolid2.pySolidModel()
    solid.solid_newObject('cyl')
    solid.SetVtkPolyData('cap')
    solid.GetBoundaryFaces(90)
    print "Creating model: \nFaceID found: " + str(solid.GetFaceIds())
    solid.WriteNative(dstdir + "/cylinder.vtp")
    
    pyRepository.repos_delete('ctp')
    pyRepository.repos_delete('ct2p')
    pyRepository.repos_delete('ct2ps')
    pyRepository.repos_delete(dstName)
    pyRepository.repos_delete('cap')
    pyRepository.repos_delete('path')
    
    from shutil import copyfile
    copyfile("cylinder.vtp.facenames2",dstdir + "/cylinder.vtp.facenames")  
    return dstdir+"/cylinder.vtp"