
proc bifurcation_create_mesh_TetGen {solidfn bifurcation_mesh_option dstdir} {

  #
  #  Mesh the solid
  #

  puts "Creating mesh."

  # create meshsim style script file
  set fp [open [file join $dstdir bifurcation.tgs] w]
  fconfigure $fp -translation lf
  puts $fp "msinit"
  puts $fp "logon [file join $dstdir bifurcation.logfile]"
  puts $fp "loadModel $solidfn"
  puts $fp "setSolidModel"
  puts $fp "newMesh"
  puts $fp "option surface 1"
  puts $fp "option volume 1"
  if {$bifurcation_mesh_option == 1} {
    puts $fp "option a 1.2"
    puts $fp "wallFaces wall"
  } elseif {$bifurcation_mesh_option == 2} {
    puts $fp "option a 1.2"
    puts $fp "wallFaces wall"
    puts $fp "sphereRefinement 0.5 10.0 16.0 0.0 -95.0"
  } elseif {$bifurcation_mesh_option == 3} {
    puts $fp "option a 0.75"
    puts $fp "wallFaces wall"
  }
  puts $fp "option q 1.4"
  puts $fp "option Y"
  puts $fp "generateMesh"
  puts $fp "writeMesh [file join $dstdir bifurcation.sms] vtu 0"
  puts $fp "deleteMesh"
  puts $fp "deleteModel"
  puts $fp "logoff"
  close $fp

  #puts $fp "option O1"

  catch {repos_delete -obj mymesh}
  mesh_readTGS [file join $dstdir bifurcation.tgs] mymesh

  puts "Writing out mesh surfaces."
  file mkdir [file join $dstdir mesh-complete]
  file mkdir [file join $dstdir mesh-complete mesh-surfaces]

  mesh_writeCompleteMesh mymesh bifurcation bifurcation [file join $dstdir mesh-complete]

}
