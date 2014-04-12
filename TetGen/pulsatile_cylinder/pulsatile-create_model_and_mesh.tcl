
proc demo_create_model {dstdir} {

  # just copy the model for now

  solid_readNative -file cylinder.vtp -obj cyl

  file copy cylinder.vtp $dstdir
  file copy cylinder.vtp.facenames $dstdir
  
  return

}



proc demo_create_mesh {dstdir pulsatile_mesh_option} {

  #
  #  Mesh the solid
  #

  puts "Creating mesh."

  # create meshsim style script file
  set fp [open [file join $dstdir cylinder.tgs] w]
  fconfigure $fp -translation lf
  puts $fp "msinit"
  puts $fp "logon [file join $dstdir cylinder.logfile]"
  puts $fp "loadModel [file join $dstdir cylinder.vtp] 50.0"
  puts $fp "extractBoundaries 50.0"
  puts $fp "newMesh"
  puts $fp "option surface optimization 1"
  puts $fp "option surface smoothing 3"
  puts $fp "option volume optimization 1"
  puts $fp "option volume smoothing 3"
  puts $fp "option surface 1"
  puts $fp "option volume 1"
  puts $fp "gsize 1 0.005"
  #puts $fp "option O1"
  puts $fp "quality 2.0"
#  if {$pulsatile_mesh_option == 1} {
#  } elseif {$pulsatile_mesh_option == 2} {
#    puts $fp "size outlet absolute 0.5"
#    puts $fp "boundaryLayer wall 4 both 5 0.5"
#  } else {
#    return -code error "ERROR: invalid pulsatile_mesh_option ($pulsatile_mesh_option)"
#  }
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


proc demo_create_bc_files {dstdir} {

  #
  #  Create an analytic Inflow Waveform and create a flow file.
  #  Also calculate the FFT of the waveform for later.
  #

  puts "Generating sinusodial volumetric flow waveform."
  set viscosity 0.004
  set density 0.00106
  set T 0.2
  set Vbar 135
  set radius 2
  set omega [expr 2.0*[math_pi]/$T]

  # calculate FFT terms
  set pts {}
  file mkdir [file join $dstdir flow-files]
  set fp [open [file join $dstdir flow-files inflow.flow] "w"]
  puts $fp "\#  Time (sec)   Flow (cc/sec)"
  for {set i 0} {$i < 256} {incr i} {
    set dt [expr double($T)/255.0]
    set t [expr [expr double($i)*$dt]]
    set Vmean [expr $Vbar*(1.0+sin(2*[math_pi]*$t/$T))]
    set area [expr [math_pi]*$radius*$radius]
    lappend pts [list [expr double($i)*$dt] [expr $Vmean*$area]]
    puts $fp "[expr double($i)*$dt] -[expr $Vmean*$area]"
  }
  close $fp
  puts "Calculate analytic profile for outlet. (not done!!)"
  set terms [math_FFT -pts $pts -numInterpPts 256 -nterms 2]

  #
  #  write out bct.dat.inflow and usrNBC?.var.inflow files
  #
  #   need to use GUI for this
  #
  #  NOTE:  The same as using Boundary Conditions ->
  #                           Analytic B.C.
  #
  puts "Write bct.dat files."
  global gBC
  global guiABC
  global gFilenames

  # load in the solid used for meshing
  set gFilenames(atdb_solid_file) [file join $dstdir cylinder.vtp]
  wormGUIloadSolidModel

  # set params
  set gBC(period) $T
  set guiABC(viscosity) $viscosity
  set guiABC(density) $density
  set guiABC(type_of_profile) plug

  set guiABC(mesh_face_file) ""
  set guiABC(flow_rate_file) ""
  set guiABC(bct_dat_file)   ""
  set guiABC(face_name) {inflow}
  set guiABC(mesh_face_file) [file join $dstdir mesh-complete mesh-surfaces inflow.vtp]
  set guiABC(flow_rate_file) [file join $dstdir flow-files inflow.flow]
  set guiABC(bct_dat_file)   [file join $dstdir bct.dat.inflow]

  wormGUIwritePHASTA

}

