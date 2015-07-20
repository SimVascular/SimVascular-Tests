
proc bifurcation_create_mesh_MeshSim {solidfn pulsatile_mesh_option dstdir} {

  puts "Creating mesh."

  # create meshsim style script file
  set fp [open [file join $dstdir bifurcation.mss] w]
  fconfigure $fp -translation lf
  puts $fp "msinit"
  puts $fp "logon [file join $dstdir bifurcation.logfile]"
  puts $fp "loadModel $solidfn"
  puts $fp "newMesh"
  puts $fp "option surface optimization 1"
  puts $fp "option surface smoothing 3"
  puts $fp "option volume optimization 1"
  puts $fp "option volume smoothing 3"
  puts $fp "option surface 1"
  puts $fp "option volume 1"
  if {$pulsatile_mesh_option == 1} {
    puts $fp "gsize absolute 3"
  } elseif {$pulsatile_mesh_option == 2} {
    puts $fp "gsize absolute 3"
    puts $fp "sphereRefinement 1 10.0 16 0 -95"
    puts $fp "size lt_iliac absolute 1"
    puts $fp "size rt_iliac absolute 1"
    puts $fp "sphereRefinement 2 10.0 0 0 -75"
  } elseif {$pulsatile_mesh_option == 3} {
    puts $fp "gsize absolute 1"
    puts $fp "sphereRefinement 0.5 10.0 16 0 -95"
    puts $fp "sphereRefinement 0.5 10.0 0 0 -75"
  } else {
    return -code error "ERROR: invalid pulsatile_mesh_option ($pulsatile_mesh_option)"
  }
  puts $fp "generateMesh"
  puts $fp "writeMesh [file join $dstdir bifurcation.sms] sms 0"
  puts $fp "writeStats [file join $dstdir bifurcation.sts]"
  puts $fp "deleteMesh"
  puts $fp "deleteModel"
  puts $fp "logoff"
  close $fp

  catch {repos_delete -obj mymesh}
  mesh_readMSS [file join $dstdir bifurcation.mss] mymesh

  puts "Writing out mesh surfaces."
  file mkdir [file join $dstdir mesh-complete]
  file mkdir [file join $dstdir mesh-complete mesh-surfaces]

  mesh_writeCompleteMesh mymesh bifurcation bifurcation [file join $dstdir mesh-complete]

}
