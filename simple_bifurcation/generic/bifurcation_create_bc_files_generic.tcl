
proc bifurcation_create_bc_files_generic {solidfn dstdir} {

  set T 1.1
  set viscosity 0.004
  set density 0.00106

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
  set guiABC(type_of_profile) womersley

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

  set guiABC(flow_rate_file) [file join $dstdir flow-files \$facename.flow.steady]
  set guiABC(bct_dat_file)   [file join $dstdir bct.dat.\$facename.steady]
  set guiABC(bct_vtp_file)   [file join $dstdir bct.vtp.\$facename.steady]

  # write files
  wormGUIwriteMultipleFaces
  set guiABC(flow_rate_file) [file join $dstdir flow-files \$facename.flow]
  set guiABC(bct_dat_file)   [file join $dstdir bct.dat.\$facename]
  set guiABC(bct_vtp_file)   [file join $dstdir bct.vtp.\$facename]

}

