
proc cylinder_create_model_Parasolid {dstdir} {
  #
  #  Create a solid model of a cylinder:  radius 0.2 cm
  #                                       length 6.0 cm
  #                                       length 3.0 cm
  #
  puts "Creating solid model."
  catch {repos_delete -obj cyl}
  #solid_cylinder -result cyl -radius 0.2 -length 6.0 \
  #	       -ctr {0 0 3.0} -axis {0 0 1}
  solid_cylinder -result cyl -radius 2 -length 30 \
	         -ctr {0 0 15} -axis {0 0 1}

  #
  #  Set Face Names of Solid Model
  #
  #  NOTE:  This can be done interactively using:
  #         Solid Modeling->Simple Model Viewer
  #                                            -> View
  #                                            -> Save

  puts "Tagging faces."
  set faceids [cyl GetFaceIds]
  cyl SetFaceAttr -attr gdscName -faceId [lindex $faceids 0] -value inflow
  cyl SetFaceAttr -attr gdscId   -faceId [lindex $faceids 1] -value 1
  cyl SetFaceAttr -attr gdscName -faceId [lindex $faceids 1] -value outlet
  cyl SetFaceAttr -attr gdscName -faceId [lindex $faceids 2] -value wall

  #
  #  Save the solid model with the face tags to a file
  #
  puts "Save SolidModel."
  cyl WriteNative -file [file join $dstdir cylinder]
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

proc cylinder_create_mesh_MeshSim {dstdir pulsatile_mesh_option} {
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

proc cylinder_run_adaptor_MeshSim {adaptdir fullrundir adapt_step num_procs} {
  
  #
  #  Run the adaptor
  #
  #  Parameter Setup
  set out_mesh   [file join $adaptdir adapted-cylinder.sms]
  set model_file [file join $fullrundir cylinder.xmt_txt]
  set mesh_file  [file join $fullrundir cylinder.sms]
  set discreteFlag 0
  set adaptorsphere {-1 0 0 0 0}
  set maxRefineFactor 0.1
  set maxCoarseFactor 0.5
  set reductionRatio 0.6
  if {$num_procs > 1} {
    set solution [file join $fullrundir "restart.$adapt_step.0"]
  } else {
    set solution [file join $fullrundir "restart.$adapt_step.1"]
  }
#  set error_file [file join $fullsimdir "ybar.$adapt_step.0"]
  
  set out_solution [file join $adaptdir "restart.$adapt_step.1"]
  set stepNumber $adapt_step
  
  file delete [file join $fullrundir adaptor_done_running]
  set fp [open [file join $fullrundir run_adaptor.log] w]
  puts $fp "Start running adaptor..."
  #  Call the Adaptor
  global ADAPTOR
  puts $fp "exec $ADAPTOR -model_file $model_file -mesh_file $mesh_file -solution_file $solution -error_indicator_file $solution -out_mesh_file $out_mesh -out_solution_file $out_solution -out_sn $stepNumber -ratio $reductionRatio -hmax $maxCoarseFactor -hmin $maxRefineFactor -discrete_model_flag $discreteFlag -sphere_refinement [lindex $adaptorsphere 0] [lindex $adaptorsphere 1] [lindex $adaptorsphere 2] [lindex $adaptorsphere 3] [lindex $adaptorsphere 4]"
  close $fp
  
  if [catch {exec $ADAPTOR -model_file $model_file -mesh_file $mesh_file -solution_file $solution -error_indicator_file $solution -out_mesh_file $out_mesh -out_solution_file $out_solution -out_sn $stepNumber -ratio $reductionRatio -hmax $maxCoarseFactor -hmin $maxRefineFactor -discrete_model_flag $discreteFlag -sphere_refinement [lindex $adaptorsphere 0] [lindex $adaptorsphere 1] [lindex $adaptorsphere 2] [lindex $adaptorsphere 3] [lindex $adaptorsphere 4]} msg] {
    puts $msg
    return -code error "ERROR running adaptor!"
  }
  
  #cancelTail [file join [pwd] run_adaptor.log] ::tail_adaptorlog
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
  $adaptmesh LoadModel -file [file join $fullrundir cylinder.xmt_txt]
  $adaptmesh NewMesh  
  $adaptmesh LoadMesh -file [file join $adaptdir adapted-cylinder.sms]
  
  #
  # Create boundary condition and complete mesh files for solver
  #
  demo_write_mesh_related_files $adaptmesh cyl cylinder [file join $adaptdir mesh-complete]
  
}

