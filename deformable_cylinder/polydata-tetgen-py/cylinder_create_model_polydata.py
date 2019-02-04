try:
    import Repository
    import Solid
except:
    from __init__ import *

def demo_create_model (dstdir):
  # just copy the model for now
  # hardcode path for testing purpose
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