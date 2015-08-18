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
  
  return

}

proc cylinder_create_mesh_TetGen {dstdir pulsatile_mesh_option} {

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
  puts $fp "option a 1.0"
  puts $fp "wallFaces wall"
  if {$pulsatile_mesh_option == 2} {
    puts $fp "boundaryLayer 4 0.4 0.5"
  }
  puts $fp "option q 1.4"
  puts $fp "option Y"
  puts $fp "generateMesh"
  if {$pulsatile_mesh_option == 2} {
    puts $fp "getBoundaries"
  }
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

proc cylinder_run_adaptor_TetGen {adaptdir fullrundir adapt_step num_procs} {

  #
  #  Run the adaptor
  #
  #  Parameter Setup
  set out_mesh_file [file join $adaptdir adapted-cylinder.vtu]
  set out_surface_mesh_file [file join $adaptdir adapted-cylinder.vtp]
  set mesh_file [file join $fullrundir mesh-complete/cylinder.mesh.vtu]
  set surface_mesh_file [file join $fullrundir mesh-complete/cylinder.exterior.vtp]
  set discreteFlag 0
  set adaptorsphere {-1 0 0 0 0}
  set maxRefineFactor 0.01
  set maxCoarseFactor 1.0
  set reductionRatio 0.2
  if {$num_procs > 1} {
    set solution [file join $fullrundir "restart.$adapt_step.0"]
  } else {
    set solution [file join $fullrundir "restart.$adapt_step.1"]
  }
  
  #set error_file [file join $fullsimdir "ybar.$adapt_step.0"]
  set out_solution [file join $adaptdir restart.$adapt_step.1]
  set stepNumber $adapt_step
  
  file delete [file join $fullrundir adaptor_done_running]
  set fp [open [file join $fullrundir run_adaptor.log] w]
  puts $fp "Start running adaptor..."
  
  #  Call the Adaptor
  global TETADAPTOR
  puts $fp "exec $TETADAPTOR -surface_mesh_file $surface_mesh_file -mesh_file $mesh_file -solution_file $solution -out_mesh_file $out_mesh_file -out_surface_mesh_file $out_surface_mesh_file -out_solution_file $out_solution -out_sn $stepNumber -ratio $reductionRatio -hmax $maxCoarseFactor -hmin $maxRefineFactor"
  
  catch {exec $TETADAPTOR -surface_mesh_file $surface_mesh_file -mesh_file $mesh_file -solution_file $solution -out_mesh_file $out_mesh_file -out_surface_mesh_file $out_surface_mesh_file -out_solution_file $out_solution -out_sn $stepNumber -ratio $reductionRatio -hmax $maxCoarseFactor -hmin $maxRefineFactor &; } msg 
  puts $fp $msg
  close $fp
  
  after 5000
  
  #
  # Second run through with solver 
  #
  global gObjects
  
  set adaptmesh /tmp/new/mesh
  
  catch {repos_delete -obj $adaptmesh}
  
  file mkdir [file join $adaptdir mesh-complete]
  file mkdir [file join $adaptdir mesh-complete mesh-surfaces]
  
  #
  # Create new mesh object for adapted mesh
  #
  global gOptions
  mesh_newObject -result $adaptmesh
  $adaptmesh SetSolidKernel -name $gOptions(meshing_solid_kernel)
  $adaptmesh LoadModel -file [file join $fullrundir cylinder.vtp]
  $adaptmesh NewMesh  
  $adaptmesh LoadMesh -file [file join $adaptdir adapted-cylinder.vtu] -surfile [file join $adaptdir adapted-cylinder.vtp]
  
  #
  # Create boundary condition and complete mesh files for solver
  #
  mesh_writeCompleteMesh $adaptmesh cyl cylinder [file join $adaptdir mesh-complete]
}

