
proc steady_cylinder_create_mesh_TetGen {solidfn dstdir} {

  #
  #  Mesh the solid
  #

  puts "Creating mesh."

  # create meshsim style script file
  set fp [open [file join $dstdir cylinder.tgs] w]
  fconfigure $fp -translation lf
  puts $fp "msinit"
  puts $fp "logon [file join $dstdir cylinder.logfile]"
  puts $fp "loadModel $solidfn"
  puts $fp "setSolidModel"
  puts $fp "newMesh"
  puts $fp "option surface 1"
  puts $fp "option volume 1"
  puts $fp "option a 0.75"
  puts $fp "wallFaces wall"
  puts $fp "option q 1.4"
  puts $fp "option Y"
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
