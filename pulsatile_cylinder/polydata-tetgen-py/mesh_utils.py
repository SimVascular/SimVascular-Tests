import os
import ctypes
try:
    import pyMeshObject
    import pyMeshTetgen
    import pyRepository
    import pySolid2
    import pySolidPolydata
except:
    from __init__ import *
import vtk
import pulsatile_cylinder as pc


gPolyDataFaceNames={}
gPolyDataFaceNamesInfo = {}
gDiscreteModelFaceNames = {}
guiPDvars = {}
guiTGvars = {}
guiMMvars = {}

def return_face_id (solid,facename):
  wallid = -1
  faceids = solid.GetFaceIds()
  for ids in faceids:
      if(gPolyDataFaceNames[str(ids)] ==facename):
          wallid=int(ids)
  return wallid
  
def PolyDataVMTKGetCenterIds(resObj,string):
    print("empty function for now.")
    return
    
def PolyDataVMTKCenterlines(cappedsolid, resObj, string):
    print("empty function for now.")
    return
    

def mesh_readTGS (filename,resObjName):
  #@author Fanwei Kong based on tetgen.tcl
  #@c This function processes a tetgen style meshing
  #@c script file.
  #@a filename:  script filename.
  #@a resObj:  resulting repository MeshObject.
  #@note resObj is not deleted, even if the script file
  #@note specifies deleteModel and deleteMesh.

  if (int(pyRepository.repos_exists(resObjName)) != 0):
    raise ValueError( "object" + resObjName + "already exists!")
    return

  solid  = "/tmp/mesh_readTGS/solid"
  try:
      pyRepository.repos_delete(solid)
  except:
      pass
  global guiMMvars
  guiMMvars['meshGenerateVolumeMesh'] = 0
  global guiPDvars
  global guiTGvars
  geom=pySolid2.pySolidModel()
  resObj=pyMeshObject.pyMeshObject()
  pyMeshObject.mesh_setKernel(pc.gOptions['meshing_kernel'])
  resObj.mesh_newObject(resObjName)
  resObj.SetSolidKernel(pc.gOptions['meshing_solid_kernel'])
  # lookup for type
  types = {}
  types[1]=1
  types[2]= 2
  types['absolute'] = 1
  types['relative'] = 2
  types['abs'] = 1
  types['rel'] = 2
  sides = {}
  sides['negative']= 0
  sides['positive']= 1
  sides['both']= 2
  sides[0]= 0
  sides[1]= 1
  sides[2]= 2
  fp = open(filename, 'r')
  for line in fp:
      # skip comment lines
      if (line[0:2] == "\#"):
         print("ignoring line: <$line>")
         continue
      # supported commands
      if (line.split()[0] == "logon"):
          pyMeshObject.mesh_logon(line.split()[1])
      elif (line.split()[0] == "logoff"):
          pyMeshObject.mesh_logoff
      elif (line.split()[0] == "newMesh"):
          resObj.NewMesh()
      elif (line.split()[0] == "generateMesh"):
          resObj.GenerateMesh()
      elif (line.split()[0] == "loadModel"):
          resObj.LoadModel(line.split()[1])
          try:
              pyRepository.repos_delete(solid)
          except:
              pass
          solidfn = line.split()[1]
          geom.solid_readNative(solid, solidfn)
      #set smasherInputName $solid
          if (pc.gOptions['meshing_solid_kernel'] == "PolyData"):
              global gPolyDataFaceNames
              global gPolyDataFaceNamesInfo
              if (os.path.isfile(line.split()[1]+'.facenames')):
                  with open(line.split()[1]+'.facenames') as f:
                      exec(f.read())
              #import hashlib
              #hashlib.md5(open(line.split()[1],'rb').read()).hexdigest()
             #if {$mymd5 != $gPolyDataFaceNamesInfo(model_file_md5)} {
             #  return -code error "ERROR: polydata model ([lrange $line 1 end]) file doesn't match one used to generate facenames ([lindex $line 1].facenames)!"
             #}
          else:
              print ("Getting Solid Boundaries...")
              gInputReturnVar = 50.0
              gInputReturnVar = input("Boundary Extraction" "Enter Boundary Extraction Angle (0-90 degrees):")
              guiPDvars['angleForBoundaries'] = gInputReturnVar
              geom.GetBoundaryFaces(gInputReturnVar)
              allids = geom.GetFaceIds()
              numfaces = len(allids)
              yesno = input("The number of surfaces found was: %i.  Is this the correct number of surfaces on your polydata? yes/no" % numfaces)
              if (yesno == "no"): 
                 raise ValueError("Try again with a different boundary extraction angle or check the surface of the polydata for deteriorated elements.")
                 return
              for newid in allids:
                 gPolyDataFaceNames[newid] = "noname_" + str(newid)
      elif (line.split()[0] == "setSolidModel"):
          solidPD ="/tmp/solid/pd"
          try:
              pyRepository.repos_delete(solidPD)
          except:
              pass
          #Set the polydatasolid in the mesh object to the current solid model
          geom.GetPolyData(solidPD)
          resObj.SetVtkPolyData(solidPD)
      elif (line.split()[0] == "localSize"):
          facename = line.split()[1]
          if (facename == ""):
              raise ValueError("ERROR: Must select a face to add local mesh size on !")
              return
          faceids = geom.GetFaceIds()
          for ids in faceids:
              if (gPolyDataFaceNames[ids] == facename):
                  regionid = ids
          resObj.SetMeshOptions("LocalEdgeSize", [float(line.split()[1])])
      elif (line.split()[0] == "useCenterlineRadius"):
          if (int(guiTGvars['meshWallFirst']) != 1):
              raise ValueError("ERROR: Must select wall faces for centerline extraction")
              return
          cappedsolid = "/tmp/solid/cappedpd"
          try:
              pyRepository.repos_delete(cappedsolid)
          except:
              pass
          cappedsolid = PolyDataVMTKGetCenterIds(resObj, "mesh") 
          polys = PolyDataVMTKCenterlines(cappedsolid, resObj, "mesh")
          resObj.SetVtkPolyData(polys[0])
      elif (line.split()[0] ==  "functionBasedMeshing"):
          resObj.SetSizeFunctionBasedMesh(float(line.split()[1]), float(line.split()[2]))
      elif (line.split()[0] == "sphereRefinement"):
          resObj.SetSphereRefinement(float(line.split()[1]),float(line.split()[2]),[float(i) for i in line.split()[3:]])
      elif (line.split()[0] == "wallFaces"):
          guiTGvars['meshWallFirst'] = 1
          resObj.SetMeshOptions("MeshWallFirst", [1])
          walls = []
          for i in range(1,len(line.split())):
              name  = line.split()[i]
              name_id =  return_face_id(geom, name)
              walls.append(name_id)
          resObj.SetWalls(walls)
      elif (line.split()[0] == "boundaryLayer"):
          if (guiTGvars['meshWallFirst'] != 1):
              raise ValueError("ERROR: Must select wall faces for boundary layer")
              return
          resObj.SetBoundaryLayer(0, 0, 0, int(line.split()[1]), [float(i) for i in line.split()[2:]])
      elif (line.split()[0] == "tolerance"):
          resObj.SetTolerance(float(line.split()[1]))
      elif (line.split()[0] == "quality"):
          resObj.SetQuality(line.split()[1])
      elif (line.split()[0] == "writeMesh"):
          resObj.WriteMesh(line.split()[1], int(line.split()[-1]))
      elif (line.split()[0] == "option"):
          if (len(line.split())== 3):
             if (line.split()[1]=="surface"):
               resObj.SetMeshOptions("SurfaceMeshFlag", [int(line.split()[2])])
             elif (line.split()[1] == "volume"):
               resObj.SetMeshOptions("VolumeMeshFlag" ,[int(line.split()[2])])
               guiMMvars['meshGenerateVolumeMesh'] = 1
             elif (line.split()[1] == "gsize"):
               resObj.SetMeshOptions("GlobalEdgeSize", [float(line.split()[2])])
             elif (line.split()[1] == "a"):
               resObj.SetMeshOptions("GlobalEdgeSize",[float(line.split()[2])])
             else:
               #lappend mylist [lindex $line 2]
               resObj.SetMeshOptions(line.split()[1],[float(line.split()[2])])
          else:
              for lineval in line.split():
                  resObj.SetMeshOptions(lineval, [1])
      elif (line.split()[0] == "getBoundaries"):
          resObj.GetBoundaryFaces(guiPDvars['angleForBoundaries'])
      else:
          print("ignoring line: " + line)
  fp.close()
  try:
      pyRepository.repos_delete(solid)
  except:
      pass
      
def mesh_writeCompleteMesh (meshName, solidName, prefix, outdir):
  global guiMMvars
  global gFilenames
  solid = pySolid2.pySolidModel()
  solid.solid_getModel(solidName)
  kernel = solid.GetKernel()
  
  mesh =pyMeshObject.pyMeshObject()
  mesh.mesh_getMesh(meshName)
  
  try:
    os.mkdir(outdir + '/mesh-surfaces')
    os.mkdir(outdir +'/misc')
  except:
      pass

  ug  =   "myug"
  pd  =   "mypd"
  facepd = "myfacepd"

  try:
      pyRepository.repos_delete(ug)
  except: 
      pass
  try:
      pyRepository.repos_delete(pd)
  except: 
      pass 
  try:
      pyRepository.repos_delete(facepd)
  except: 
      pass 
      
  if (kernel == "PolyData"  and guiMMvars['meshGenerateVolumeMesh'] != 1):
      pass
  else:
    mesh.GetUnstructuredGrid(ug)
    ugwriter = vtk.vtkXMLUnstructuredGridWriter()
    ugwriter.SetCompressorTypeToZLib()
    ugwriter.EncodeAppendedDataOff()
    ugwriter.SetInputDataObject(pyRepository.repos_exportToVtk(ug))
    ugwriter.SetFileName(outdir+ '/'+ prefix+'.mesh.vtu')
    ugwriter.Write()
    del ugwriter

  mesh.GetPolyData(pd)

  pdwriter = vtk.vtkXMLPolyDataWriter()
  pdwriter.SetCompressorTypeToZLib()
  pdwriter.EncodeAppendedDataOff()
  pdwriter.SetInputDataObject(pyRepository.repos_exportToVtk(pd))
  pdwriter.SetFileName(outdir+'/'+prefix+'.exterior.vtp')
  pdwriter.Write()

  foundWall = 0
  appender = vtk.vtkAppendPolyData()
  appender.UserManagedInputsOff()

  foundStent = 0
  Sappender = vtk.vtkAppendPolyData()
  Sappender.UserManagedInputsOff()

  name_to_identifier = {}
  identifier_to_name = {}
  facestr = mesh.GetModelFaceInfo()
  facename=""
  for faceinfo in facestr.split("  "):
      faceinfo = faceinfo.replace(" ","")
      faceinfo = faceinfo.replace("{","")
      faceinfo = faceinfo.replace("}","")
      i = faceinfo[0]
      ident = faceinfo[1]
      if (kernel == "Parasolid"):
          try:
            facename = faceinfo[2]
          except:
             pass
      elif (kernel == "Discrete"):
          global gDiscreteModelFaceNames
          try:
              facename = gDiscreteModelFaceNames[i]
          except:
              pass
      elif (kernel == "PolyData"):
          global gPolyDataFaceNames
          try:
              facename = gPolyDataFaceNames[i]
          except:
              pass
      else:
          raise ValueError("ERROR: invalid solid kernel" + kernel )
          return
      if (facename == ""):
          facename = "missing_" + i+ "\_" + ident
      elif ("noname" in facename.lower()):
          print(facename + " is not being written because it has no_name")
      else:
          name_to_identifier[facename] = ident
          identifier_to_name[ident] = facename
          try:
              pyRepository.repos_delete(facepd)
          except:
              pass
      try:
          mesh.GetFacePolyData(facepd, int(i))
      except:
          print ("Warning face %s not found, skipping face" % i)
          pass
      pdwriter.SetInputDataObject(pyRepository.repos_exportToVtk(facepd))
      pdwriter.SetFileName(outdir+'/mesh-surfaces/'+facename+'.vtp')
      pdwriter.Write()
      if "wall" in facename:
          foundWall = 1
          appender.AddInputData(pyRepository.repos_exportToVtk(facepd))
      if "stent" in facename:
          foundStent = 1
          Sappender.AddInputData(pyRepository.repos_exportToVtk(facepd))
      try:
          pyRepository.repos_delete(facepd)
      except:
          pass
          
  if (foundWall):
    appender.Update()
    cleaner =vtk.vtkCleanPolyData()
    cleaner.PointMergingOn()
    cleaner.PieceInvariantOff()
    cleaner.SetInputDataObject(appender.GetOutput())
    cleaner.Update()
    pdwriter.SetFileName(outdir+ '/walls_combined.vtp')
    pdwriter.SetInputDataObject(cleaner.GetOutput())
    pdwriter.Write()
    del cleaner
    del appender

  if (foundStent):
    Sappender.Update()
    Scleaner = vtk.vtkCleanPolyData()
    Scleaner.PointMergingOn()
    Scleaner.PieceInvariantOff()
    Scleaner.SetInputDataObject(Sappender.GetOutput())
    Scleaner.Update()
    pdwriter.SetFileName(outdir+'/stent_combined.vtp')
    pdwriter.SetInputDataObject(Scleaner.GetOutput())
    del pdwriter
    del Scleaner
  del Sappender

  #$mesh WriteMetisAdjacency -file $outdir/$prefix.xadj
  #mesh_kernel = mesh.GetKernel()
  #if (mesh_kernel == "TetGen"):
  #  gFilenames['tet_mesh_script_file'] = outdir+ "/" + prefix
  #  guiMMcreateTetGenScriptFile
  #elif (mesh_kernel == "MeshSim"):
  #  gFilenames['mesh_script_file'] = outdir + "/" + prefix
  #  guiMMcreateMeshSimScriptFile
  #  mesh.WriteMesh(outdir+'/'+prefix+'.sms')

  try:
      pyRepository.repos_delete(ug)
  except:
      pass
  try:
      pyRepository.repos_delete(pd)
  except:
      pass 
  try:
      pyRepository.repos_delete(facepd)
  except:
      pass


    

