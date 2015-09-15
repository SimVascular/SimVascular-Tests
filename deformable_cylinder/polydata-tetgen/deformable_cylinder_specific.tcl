#
#   Copyright (c) 2015 Stanford University
#   All rights reserved.  
#
#   Portions of the code Copyright (c) 2009-2012 Open Source Medical Software Corporation
#
#  This script requires the following files:
#     solver.inp
#  and should be sourced interactively from SimVascular
#

proc cylinder_create_model_PolyData {dstdir} {

  # just copy the model for now

  catch {repos_delete -obj cyl}
  solid_readNative -file cylinder.vtp -obj cyl

  file copy cylinder.vtp $dstdir
  file copy cylinder.vtp.facenames $dstdir
  
}

proc cylinder_create_mesh_TetGen {dstdir} {

  #
  #  Mesh the solid
  #

  puts "Creating mesh."

  # create meshsim style script file
  set fp [open [file join $dstdir cylinder.tgs] w]
  fconfigure $fp -translation lf
  puts $fp "msinit"
  puts $fp "logon [file join $dstdir cylinder.logfile]"
  puts $fp "loadModel [file join $dstdir cylinder.vtp]"
  puts $fp "setSolidModel"
  puts $fp "newMesh"
  puts $fp "option surface 1"
  puts $fp "option volume 1"
  puts $fp "option GlobalEdgeSize 0.4"
  puts $fp "wallFaces wall"
  puts $fp "option QualityRatio 1.4"
  puts $fp "option NoBisect 1"
  puts $fp "generateMesh"
  puts $fp "writeMesh [file join $dstdir cylinder.sms] vtu 0"
  puts $fp "deleteMesh"
  puts $fp "deleteModel"
  puts $fp "logoff"
  close $fp

  catch {repos_delete -obj mymesh}
  mesh_readTGS [file join $dstdir cylinder.tgs] mymesh

  puts "Writing out mesh surfaces."
  file mkdir [file join $dstdir mesh-complete]
  file mkdir [file join $dstdir mesh-complete mesh-surfaces]

  mesh_writeCompleteMesh mymesh cyl cylinder [file join $dstdir mesh-complete]
}


