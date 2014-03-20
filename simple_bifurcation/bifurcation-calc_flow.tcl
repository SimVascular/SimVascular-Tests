
proc demoFlowThruFace {theMesh meshFaceObj unitOutwardNormal type rtnFlow} {

  # NOTE: this proc has been generalized to calculate mean pressure
  #       as well, so the name is not really correct

  upvar $rtnFlow flux

  set flat /demo/demoFlowThruFace/flat
  set flat_0 /demo/demoFlowThruFace/flat/0
  set myVectors tmp-demoFlowThruFace-vec
  set myScalars tmp-demoFlowThruFace-sca
  catch {repos_delete -obj $flat}
  catch {repos_delete -obj $flat_0}
  catch {$myVectors Delete}
  catch {$myScalars Delete}

  #now calculate flow rate for each time point

  set numPts [geom_numPts -obj $meshFaceObj]
  set nodeIds [[[repos_exportToVtk -src $meshFaceObj] GetPointData] GetScalars]

  if {$type == "flow"} {

    # create an array for the velocity vectors
    vtkFloatArray $myVectors; $myVectors SetNumberOfComponents 3
    $myVectors Allocate 1000 1000

    set objVectors [[$theMesh GetPointData] GetVectors]

    for {set i 0} {$i < $numPts} {incr i} {
      set node [expr int([$nodeIds GetValue $i])]
      # nodes in vtk start at 0, so subtract 1 off
      set node [expr $node - 1]
      set vec [$objVectors GetTuple3 $node]
      #puts "processing vtk node: $node vec: $vec"
      $myVectors InsertNextTuple3 [lindex $vec 0] [lindex $vec 1] [lindex $vec 2]
    }

    # associate vectors with polydata
    [[repos_exportToVtk -src $meshFaceObj] GetPointData] SetVectors $myVectors

  } elseif {$type == "pressure"} {

    # create an array for the velocity vectors
    vtkFloatArray $myScalars; $myScalars SetNumberOfComponents 1
    $myScalars Allocate 1000 1000

    set objScalars [[$theMesh GetPointData] GetScalars]

    for {set i 0} {$i < $numPts} {incr i} {
      set node [expr int([$nodeIds GetValue $i])]
      # nodes in vtk start at 0, so subtract 1 off
      set node [expr $node - 1]
      set scalar [$objScalars GetTuple1 $node]
      #puts "processing vtk node: $node vec: $vec"
      $myScalars InsertNextTuple1 $scalar
    }

    # need to wait to associate scalars with polydata, see below

  } else {

    return -code error "ERROR:  invalid type ($type)."

  }

  set boolean 1
  set rotated_norm {}
  geom_flatten $unitOutwardNormal $boolean $meshFaceObj rotated_norm $flat

  set bbox [geom_bbox -obj $flat]

  if {[expr abs([lindex $bbox 5] - [lindex $bbox 4])] > 0.1} {
    catch {repos_delete -obj $flat}
    set flux non-planar
    puts "NOTE:  face not flat, value of zero being returned!"
    return
  }

  geom_translate -src $flat  -vec [list 0 0 [expr -1.0*[lindex $bbox 4]]]  -dst $flat_0
  set area [geom_surfArea -src $flat_0]
  #puts "area: $area"

  # find the idealized outward normal
  if {[lindex $rotated_norm 2] > 0} {
      set inorm {0 0 1}
  } else {
      set inorm {0 0 -1}
  }


  # intentionally wait to define scalars on flat object so we don't overwrite
  # scalar node id values!

  if {$type == "pressure"} {
    # associate scalars with polydata
    [[repos_exportToVtk -src $flat_0] GetPointData] SetScalars $myScalars
  }

  #puts "original normal  : $unitOutwardNormal"
  #puts "rotated normal   : $rotated_norm"
  #puts "idealized normal : $inorm"

  # get flux
  if {$type == "flow"} {
     set tensorType 1
    set flux [geom_integrateSurfaceFlux -obj $flat_0 -nrm $inorm -tensorType $tensorType]
  } elseif {$type == "pressure"} {
     set tensorType 0
     set flux [geom_integrateSurfaceFlux -obj $flat_0 -nrm $inorm -tensorType $tensorType]
     set flux [expr $flux / $area]
  } else {
     return -code error "ERROR: invalid type ($type)."
  }


  #puts "$flux"

  catch {repos_delete -obj $flat}
  catch {repos_delete -obj $flat_0}

  if {$type == "flow"} {
    # unassociate vectors with polydata
    [[repos_exportToVtk -src $meshFaceObj] GetPointData] SetVectors ""
    $myVectors Delete
  } elseif {$type == "pressure"} {
    #[[repos_exportToVtk -src $meshFaceObj] GetPointData] SetScalars ""
    $myScalars Delete
  } else {
    return -code error "ERROR: invalid type ($type)."
  }

}

