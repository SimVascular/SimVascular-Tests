try:
    import Repository
    import Solid
except:
    from __init__ import *

def demo_create_model (dstdir):
  # just copy the model for now
  # hardcode path for testing purpose
  try:
      Repository.repos_delete("bifurcation")
  except:
      pass
  cyl=Solid.pySolidModel()
  cyl.ReadNative("bifurcation","bifurcation.vtp")
  from shutil import copyfile
  copyfile("bifurcation.vtp",dstdir + "/bifurcation.vtp")
  copyfile("bifurcation.vtp.facenames",dstdir + "/bifurcation.vtp.facenames")  
  return dstdir+"/bifurcation.vtp"
