import pyRepository
import pySolid2

def demo_create_model (dstdir):
  # just copy the model for now
  # hardcode path for testing purpose
  try:
      pyRepository.repos_delete("bifurcation")
  except:
      pass
  cyl=pySolid2.pySolidModel()
  cyl.solid_readNative("bifurcation","bifurcation.vtp")
  from shutil import copyfile
  copyfile("bifurcation.vtp",dstdir + "/bifurcation.vtp")
  copyfile("bifurcation.vtp.facenames",dstdir + "/bifurcation.vtp.facenames")  
  return dstdir+"/bifurcation.vtp"