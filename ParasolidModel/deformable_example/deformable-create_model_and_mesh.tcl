
proc demo_create_model {dstdir} {
  #
  #  Create a solid model of a cylinder:  radius 1.0 cm
  #                                       length 3.0 cm
  #
  puts "Creating solid model."
  catch {repos_delete -obj cyl}
  solid_cylinder -result cyl -radius 1.0 -length 3.0 \
  	       -ctr {0 0 1.5} -axis {0 0 1}

  #
  #  Set Face Names of Solid Model
  #
  #  NOTE:  This can also be done interactively

  puts "Tagging faces."
  set faceids [cyl GetFaceIds]
  cyl SetFaceAttr -attr gdscName -faceId [lindex $faceids 0] -value inflow
  cyl SetFaceAttr -attr gdscName -faceId [lindex $faceids 1] -value outlet
  cyl SetFaceAttr -attr gdscName -faceId [lindex $faceids 2] -value wall

  #
  #  Save the solid model with the face tags to a file
  #
  puts "Save SolidModel."
  cyl WriteNative -file [file join $dstdir cylinder]
}


proc demo_create_mesh {dstdir} {

  puts "Creating mesh."

  # create meshsim style script file
  set fp [open [file join $dstdir cylinder.mss] w]
  fconfigure $fp -translation lf
  puts $fp "msinit"
  puts $fp "logon [file join $dstdir cylinder.logfile]"
  puts $fp "loadModel [file join $dstdir cylinder.xmt_txt]"
  puts $fp "newMesh"
  puts $fp "option surface optimization 1"
  puts $fp "option surface smoothing 3"
  puts $fp "option volume optimization 1"
  puts $fp "option volume smoothing 3"
  puts $fp "option surface 1"
  puts $fp "option volume 1"
  puts $fp "gsize 1 0.2"
  puts $fp "generateMesh"
  puts $fp "writeMesh [file join $dstdir cylinder.sms] sms 0"
  puts $fp "writeStats [file join $dstdir cylinder.sts]"
  puts $fp "deleteMesh"
  puts $fp "deleteModel"
  puts $fp "logoff"
  close $fp

  catch {repos_delete -obj mymesh}
  mesh_readMSS [file join $dstdir cylinder.mss] mymesh

  #  Write out useful mesh surfaces
  #
  #  NOTE:  This can be done interactively using:
  #            Meshing->Write Output Files
  #
  puts "Writing out mesh surfaces."
  file mkdir [file join $dstdir mesh-surfaces]
  foreach i [cyl GetFaceIds] {
    set facename [cyl GetFaceAttr -attr gdscName -faceId $i]
    mymesh GetElementFacesOnModelFace -face $i \
                          -explicitFaceOutput 1 \
	                  -file [file join $dstdir mesh-surfaces/$facename.ebc]
    mymesh GetElementNodesOnModelFace -face $i \
	                  -file [file join $dstdir mesh-surfaces/$facename.nbc]
    mymesh GetFacePolyData -face $i -result face$i
    repos_writeVtkPolyData -obj face$i -type ascii -file [file join $dstdir mesh-surfaces/$facename.vtk]
  }

  mymesh WriteSpectrumSolverElements -file [file join $dstdir cylinder.connectivity]
  mymesh WriteSpectrumSolverNodes -file [file join $dstdir cylinder.coordinates]
  mymesh WriteMetisAdjacency -file [file join $dstdir cylinder.xadj]

  file_append [list [file join $dstdir mesh-surfaces/inflow.ebc.gz] \
		   [file join $dstdir mesh-surfaces/outlet.ebc.gz] \
		   [file join $dstdir mesh-surfaces/wall.ebc.gz]] [file join $dstdir all.ebc.gz]

}


proc demo_create_bc_files {dstdir} {

  set viscosity 0.04
  set density 1.06
  set T 1.1

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
  set gFilenames(atdb_solid_file) [file join $dstdir cylinder.xmt_txt]
  wormGUIloadSolidModel

  # set params
  set gBC(period) $T
  set guiABC(viscosity) $viscosity
  set guiABC(density) $density
  set guiABC(type_of_profile) parabolic

  set guiABC(face_name) {$facename}
  set guiABC(mesh_face_file) [file join $dstdir mesh-surfaces \$facename.vtk]
  set guiABC(flow_rate_file) [file join $dstdir flow-files \$facename.flow.steady]
  set guiABC(bct_dat_file)   [file join $dstdir bct.dat.\$facename.steady]
  set guiABC(num_output_modes) 10
  set guiABC(num_output_pts_in_period) 2

  # write files
  wormGUIwriteMultipleFaces

  set guiABC(face_name) {$facename}
  set guiABC(mesh_face_file) [file join $dstdir mesh-surfaces \$facename.vtk]
  set guiABC(flow_rate_file) [file join $dstdir flow-files \$facename.flow.pulsatile]
  set guiABC(bct_dat_file)   [file join $dstdir bct.dat.\$facename.pulsatile]
  set guiABC(num_output_modes) 10
  set guiABC(num_output_pts_in_period) 276

  # write files
  wormGUIwriteMultipleFaces

}

