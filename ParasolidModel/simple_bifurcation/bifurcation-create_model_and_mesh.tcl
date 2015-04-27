
proc demo_create_model {dstdir} {
   catch {repos_delete -obj bifurcation}
    solid_readNative -file [file join $dstdir bifurcation.xmt_txt] -obj bifurcation
}



proc demo_write_mesh_related_files {mesh solid prefix outdir} {

  file mkdir [file join $outdir mesh-surfaces]
  file mkdir [file join $outdir misc]

  set ug     myug
  set pd     mypd
  set facepd myfacepd

  set pdwriter mypdwriter
  set ugwriter myugwriter

  catch {repos_delete -obj $ug}
  catch {repos_delete -obj $pd}
  catch {repos_delete -obj $facepd}

  catch {$pdwriter Delete}
  catch {$ugwriter Delete}

  $mesh GetUnstructuredGrid -result $ug
  $mesh GetPolyData -result $pd

  vtkXMLUnstructuredGridWriter $ugwriter
  $ugwriter SetCompressorTypeToZLib
  $ugwriter EncodeAppendedDataOff
  $ugwriter SetInputDataObject [repos_exportToVtk -src $ug]
  $ugwriter SetFileName $outdir/$prefix.mesh.vtu
  $ugwriter Update
  $ugwriter Delete

  vtkXMLPolyDataWriter $pdwriter
  $pdwriter SetCompressorTypeToZLib
  $pdwriter EncodeAppendedDataOff
  $pdwriter SetInputDataObject [repos_exportToVtk -src $pd]
  $pdwriter SetFileName $outdir/$prefix.exterior.vtp
  $pdwriter Update

  set foundWall 0
  set appender tmp-wall-appender
  catch {$appender Delete}
  vtkAppendPolyData $appender
  $appender UserManagedInputsOff

  catch {unset name_to_identifier}
  catch {unset identifier_to_name}
  foreach i [$solid GetFaceIds] {
     set ident {0}
     set ident [$solid GetFaceAttr -attr identifier -faceId $i]
     set facename noname_$ident
     catch {set facename [$solid GetFaceAttr -attr gdscName -faceId $i]}
     set name_to_identifier($facename) $ident
     set identifier_to_name($ident) $facename 
     catch {repos_delete -obj $facepd}
     $mesh GetFacePolyData -result $facepd -face $i
     $pdwriter SetInputDataObject [repos_exportToVtk -src $facepd]
     $pdwriter SetFileName $outdir/mesh-surfaces/$facename.vtp
     $pdwriter Update
     if {[string range [string trim $facename] 0 3] == "wall"} { 
       set foundWall 1
       $appender AddInputData [repos_exportToVtk -src $facepd]
     }
     catch {repos_delete -obj $facepd}
  }

  if {$foundWall} {
    set cleaner tmp-wall-cleaner
    $appender Update
    vtkCleanPolyData $cleaner
    $cleaner PointMergingOn
    $cleaner PieceInvariantOff
    $cleaner SetInputDataObject [$appender GetOutput]
    $cleaner Update
    $pdwriter SetFileName $outdir/walls_combined.vtp
    $pdwriter SetInputDataObject [$cleaner GetOutput]
    $pdwriter Update
    $cleaner Delete
  }
  $appender Delete

  $pdwriter Delete

  $mesh WriteMetisAdjacency -file $outdir/$prefix.xadj

  catch {repos_delete -obj $ug}
  catch {repos_delete -obj $pd}
  catch {repos_delete -obj $facepd}

  $mesh WriteSpectrumSolverElements -file $outdir/misc/$prefix.connectivity
  $mesh WriteSpectrumSolverNodes    -file $outdir/misc/$prefix.coordinates

}


proc demo_create_mesh {dstdir pulsatile_mesh_option} {
  #
  #  Mesh the solid using stand-alone MeshSim executable
  #  and a script file.
  #
  #  NOTE:  This can be done interactively using:
  #            Meshing->Create Attribute File
  #            Meshing->Create Mesh
  #

  puts "Creating mesh."

  # create meshsim style script file
  set fp [open [file join $dstdir bifurcation.mss] w]
  fconfigure $fp -translation lf
  puts $fp "msinit"
  puts $fp "logon [file join $dstdir bifurcation.logfile]"
  puts $fp "loadModel [file join $dstdir bifurcation.xmt_txt]"
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

  #  Write out useful mesh surfaces
  #
  #  NOTE:  This can be done interactively using:
  #            Meshing->Write Output Files
  #
  puts "Writing out mesh surfaces."
  file mkdir [file join $dstdir mesh-complete]
  file mkdir [file join $dstdir mesh-complete mesh-surfaces]
  file mkdir [file join $dstdir mesh-complete special]

  demo_write_mesh_related_files mymesh bifurcation bifurcation [file join $dstdir mesh-complete]

}


proc demo_create_bc_files {dstdir} {

  set T 1.1
  set viscosity 0.004
  set density 0.00106

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
  set gFilenames(atdb_solid_file) [file join $dstdir bifurcation.xmt_txt]
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

