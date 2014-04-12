
proc demo_create_model {dstdir} {

   catch {repos_delete -obj bifurcation}
   solid_readNative -file [file join $dstdir bifurcation.vtp] -obj bifurcation

   file copy bifurcation.vtp $dstdir
   file copy bifurcation.vtp.facenames $dstdir

   return

}


proc demo_create_mesh {dstdir pulsatile_mesh_option} {

  #
  #  Mesh the solid
  #

  puts "Creating mesh."

  # create meshsim style script file
  set fp [open [file join $dstdir bifurcation.tgs] w]
  fconfigure $fp -translation lf
  puts $fp "msinit"
  puts $fp "logon [file join $dstdir bifurcation.logfile]"
  puts $fp "loadModel [file join $dstdir bifurcation.vtp] 50.0"
  puts $fp "extractBoundaries 50.0"
  puts $fp "newMesh"
  puts $fp "option surface optimization 1"
  puts $fp "option surface smoothing 3"
  puts $fp "option volume optimization 1"
  puts $fp "option volume smoothing 3"
  puts $fp "option surface 1"
  puts $fp "option volume 1"
  puts $fp "gsize 1 2.0"

  #puts $fp "option O1"

  if {$pulsatile_mesh_option == 1} {
    puts $fp "gsize absolute 1.0"
  } elseif {$pulsatile_mesh_option == 2} {
    puts $fp "gsize absolute 1.0"
  #  puts $fp "sphereRefinement 1 10.0 16 0 -95"
  #  puts $fp "size lt_iliac absolute 1"
  #  puts $fp "size rt_iliac absolute 1"
  #  puts $fp "sphereRefinement 2 10.0 0 0 -75"
  } elseif {$pulsatile_mesh_option == 3} {
    puts $fp "gsize absolute 1.0"
  #  puts $fp "sphereRefinement 0.5 10.0 16 0 -95"
  #  puts $fp "sphereRefinement 0.5 10.0 0 0 -75"
  } else {
    return -code error "ERROR: invalid pulsatile_mesh_option ($pulsatile_mesh_option)"
  }

  puts $fp "quality 2.0"
  puts $fp "generateMesh"
  puts $fp "writeMesh [file join $dstdir bifurcation.vtu] vtu 0"
  puts $fp "deleteMesh"
  puts $fp "deleteModel"
  puts $fp "logoff"
  close $fp

  catch {repos_delete -obj mymesh}
  mesh_readTGS [file join $dstdir bifurcation.tgs] mymesh

  puts "Writing out mesh surfaces."
  file mkdir [file join $dstdir mesh-complete]
  file mkdir [file join $dstdir mesh-complete mesh-surfaces]

  mesh_writeCompleteMesh mymesh bifurcation bifurcation [file join $dstdir mesh-complete]

}


proc demo_create_bc_files {dstdir} {

  set T 1.1
  set viscosity 0.004
  set density 0.00106

  #
  #  write out bct.dat.inflow

  #
  puts "Write bct.dat files."
  global gBC
  global guiABC
  global gFilenames

  # load in the solid used for meshing
  set gFilenames(atdb_solid_file) [file join $dstdir bifurcation.vtp]
  wormGUIloadSolidModel

  # set params
  set gBC(period) $T
  set guiABC(viscosity) $viscosity
  set guiABC(density) $density
  set guiABC(type_of_profile) womersley

  set guiABC(mesh_face_file) ""
  set guiABC(flow_rate_file) ""
  set guiABC(bct_dat_file)   ""
  set guiABC(face_name) {inflow}
  set guiABC(mesh_face_file) [file join $dstdir mesh-complete mesh-surfaces inflow.vtp]
  set guiABC(flow_rate_file) [file join $dstdir flow-files inflow.flow]
  set guiABC(bct_dat_file)   [file join $dstdir bct.dat.inflow]

  # write files
  wormGUIwritePHASTA

  set guiABC(flow_rate_file) [file join $dstdir flow-files inflow.flow.steady]
  set guiABC(bct_dat_file)   [file join $dstdir bct.dat.inflow.steady]

  # write files
  wormGUIwritePHASTA

  set guiABC(flow_rate_file) [file join $dstdir flow-files inflow.flow]
  set guiABC(bct_dat_file)   [file join $dstdir bct.dat.inflow]

}

