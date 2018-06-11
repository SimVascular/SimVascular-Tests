import pyRepository
import pySolid2

def demo_create_model (dstdir):
  # just copy the model for now
  # hardcode path for testing purpose
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