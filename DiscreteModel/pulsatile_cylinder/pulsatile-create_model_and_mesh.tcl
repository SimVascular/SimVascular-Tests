
proc demo_create_model {dstdir} {

  solid_setKernel -name Discrete

  # just copy the model for now

  set fn cylinder.dsm

  catch {repos_delete -obj cyl}
  solid_readNative -file $fn -obj cyl

  file copy $fn $dstdir
  file copy $fn.facenames $dstdir

  global gDiscreteModelFaceNames
  global gDiscreteModelFaceNamesInfo
  catch {unset gDiscreteModelFaceNames}
  catch {unset gDiscreteModelFaceNamesInfo}
  if [file exists $fn.facenames] {
    puts "sourcing $fn.facenames"
    source $fn.facenames
    package require md5
    set mymd5 [::md5::md5 -hex -file $fn]
    if {$mymd5 != $gDiscreteModelFaceNamesInfo(model_file_md5)} {
      return -code error "ERROR: dsm model ($fn) file doesn't match one used to generate facenames ($fn.facenames)!"
    }
  }

  return

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

  global gOptions
  set gOptions(meshing_solid_kernel) Discrete

  # create meshsim style script file
  set fp [open [file join $dstdir cylinder.mss] w]
  fconfigure $fp -translation lf
  puts $fp "msinit"
  puts $fp "logon [file join $dstdir cylinder.logfile]"
  puts $fp "loadModel [file join $dstdir cylinder.dsm]"
  puts $fp "newMesh"
  puts $fp "option surface optimization 1"
  puts $fp "option surface smoothing 3"
  puts $fp "option volume optimization 1"
  puts $fp "option volume smoothing 3"
  puts $fp "option surface 1"
  puts $fp "option volume 1"
  puts $fp "gsize absolute 1"
  if {$pulsatile_mesh_option == 1} {
  } elseif {$pulsatile_mesh_option == 2} {
    puts $fp "size outlet absolute 0.5"
    puts $fp "boundaryLayer wall 4 both 5 0.5"
  } else {
    return -code error "ERROR: invalid pulsatile_mesh_option ($pulsatile_mesh_option)"
  }
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

  file mkdir [file join $dstdir mesh-complete]
  file mkdir [file join $dstdir mesh-complete mesh-surfaces]

  demo_write_mesh_related_files mymesh cyl cylinder [file join $dstdir mesh-complete]

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
  set gFilenames(atdb_solid_file) [file join $dstdir cylinder.dsm]
  wormGUIloadSolidModel

  # set params
  set gBC(period) $T
  set guiABC(viscosity) $viscosity
  set guiABC(density) $density
  set guiABC(type_of_profile) plug

  set guiABC(mesh_face_file) ""
  set guiABC(flow_rate_file) ""
  set guiABC(bct_dat_file)   ""
  set guiABC(face_name) {$facename}
  set guiABC(mesh_face_file) [file join $dstdir mesh-complete mesh-surfaces \$facename.vtp]
  set guiABC(flow_rate_file) [file join $dstdir flow-files \$facename.flow]
  set guiABC(bct_dat_file)   [file join $dstdir bct.dat.\$facename]

  # write files
  wormGUIwriteMultipleFaces
}

