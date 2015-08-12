
proc steady_cylinder_create_mesh_MeshSim {solidfn dstdir} {

  puts "Creating mesh."

  # create meshsim style script file
  set fp [open [file join $dstdir cylinder.mss] w]
  fconfigure $fp -translation lf
  puts $fp "msinit"
  puts $fp "logon [file join $dstdir cylinder.logfile]"
  puts $fp "loadModel [file join $dstdir $solidfn]"
  puts $fp "newMesh"
  puts $fp "option surface optimization 1"
  puts $fp "option surface smoothing 3"
  puts $fp "option volume optimization 1"
  puts $fp "option volume smoothing 3"
  puts $fp "option surface 1"
  puts $fp "option volume 1"
  puts $fp "gsize absolute 1"
  puts $fp "generateMesh"
  puts $fp "writeMesh [file join $dstdir cylinder.sms] sms 0"
  puts $fp "writeStats [file join $dstdir cylinder.sts]"
  puts $fp "deleteMesh"
  puts $fp "deleteModel"
  puts $fp "logoff"
  close $fp

  catch {repos_delete -obj mymesh}
  mesh_readMSS [file join $dstdir cylinder.mss] mymesh

  puts "Writing out mesh surfaces."
  file mkdir [file join $dstdir mesh-complete]
  file mkdir [file join $dstdir mesh-complete mesh-surfaces]

  mesh_writeCompleteMesh mymesh cyl cylinder [file join $dstdir mesh-complete]

}
