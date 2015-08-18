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

proc steady_cylinder_create_flow_files_generic {dstdir} {

  # Write steady flowrate
  file mkdir [file join $dstdir flow-files]
  set fp [open [file join $dstdir flow-files inflow.flow] "w"]
  puts $fp "\#  Time (sec)   Flow (mm^3/sec)"
  puts $fp "0   -1570.796327"
  puts $fp "0.2 -1570.796327"
  close $fp

}

proc steady_cylinder_create_bc_files_generic {solidfn dstdir} {

  #
  #  Create an analytic Inflow Waveform and create a flow file.
  #  Also calculate the FFT of the waveform for later.
  #

  steady_cylinder_create_flow_files_generic $dstdir
  
  puts "Generating sinusodial volumetric flow waveform."
  set viscosity 0.004
  set density 0.00106
  set T 0.2
  set Vbar 135
  set radius 2
  set omega [expr 2.0*[math_pi]/$T]

  puts "Write bct.dat and bct.vtp files."
  global gBC
  global guiABC
  global gFilenames

  # load in the solid used for meshing
  # set both vars to handle any type of model
  set gFilenames(atdb_solid_file) $solidfn
  set gFilenames(polydata_solid_file) $solidfn
  wormGUIloadSolidModel

  # set params
  set gBC(period) $T
  set guiABC(viscosity) $viscosity
  set guiABC(density) $density
  set guiABC(type_of_profile) plug

  set guiABC(mesh_face_file) ""
  set guiABC(flow_rate_file) ""
  set guiABC(bct_dat_file)   ""
  set guiABC(bct_vtp_file)   ""
  set guiABC(face_name) {$facename}
  set guiABC(mesh_face_file) [file join $dstdir mesh-complete mesh-surfaces \$facename.vtp]
  set guiABC(flow_rate_file) [file join $dstdir flow-files \$facename.flow]
  set guiABC(bct_dat_file)   [file join $dstdir bct.dat.\$facename]
  set guiABC(bct_vtp_file)   [file join $dstdir bct.vtp.\$facename]

  # write files
  wormGUIwriteMultipleFaces
}

