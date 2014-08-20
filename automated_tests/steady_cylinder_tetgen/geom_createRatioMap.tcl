# -------------------
# geom_createRatioMap
# -------------------

proc geom_createRatioMap {inlet_mesh_face radmax result} {

  #@author Nathan Wilson
  #@c  This proc maps the scalars given on an input PolyData
  #@c  object to a destination PolyData object and returns
  #@c  a new PolyData.  This routine is not general and makes
  #@c  numerous assumptions about the nature of each point set.  See
  #@c  notes.
  #@a  velocityMap:  Input PolyData with defined scalar data.
  #@a  inlet_mesh_face:  PolyData onto which to map the scalar data.
  #@a  result:  Name of new repository PolyData object to be
  #@a  result:  created.
  #@r  status
  #@note  This code does a simple mapping of the Womersley analytic
  #@note  profile on to the points of the
  #@note  the output PolyData.  This mapping assumes that the objects
  #@note  are similar in that if you send a ray from the center of each
  #@note  object the relationship between inner (r) and outer (R) radius
  #@note  is given by r_out = r_in * R_out / R_in for any given angle.
  #@note  We also scale the result scalars assuming they represent a
  #@note  a through plane flux so that the input and output PolyData's
  #@note  have the same through plane flux.  This code requires that both
  #@note  PolyData's be in the z=0 plane.  Each should consist of a single
  #@note  region.  Iso-parametric interpolation functions are used to
  #@note  evaluate the scalar values and for calculating through plane
  #@note  flow rate.
  #@note  The absolute value of the ratio is the radius ratio,
  #@note  where positive values denote interior and negative values
  #@note  denote boundary nodes.
  #@note  This code would be much faster if it were rewritten in C.

  if {[repos_exists -obj $inlet_mesh_face] == "0"} {
    puts "ERROR:  Input PolyData $inlet_mesh_face doesn't exist."
    return -code error GDSC_ERROR
  }
  if {[repos_type -obj $inlet_mesh_face] != "PolyData"} {
    puts "ERROR:  Object $inlet_mesh_face not of type PolyData."
    return -code error GDSC_ERROR
  }
  if {[repos_exists -obj $result] == "1"} {
    puts "ERROR:  Output object $result exists."
    return -code error GDSC_ERROR
  }

  set myFE /tmp/geom_mapScalars/myFE
  set meshFreeEdges /tmp/geom_mapScalars/free_edges
  set myLinFilt /tmp/geom_mapScalars/myLinFilt
  set extrudedMeshWall /tmp/geom_mapScalars/extruded/mesh/wall
  set extrudedSegWall /tmp/geom_mapScalars/extruded/seg/wall
  set segmentation /tmp/geom_mapScalars/segmentation
  set vScalars tmp-geom_mapScalars-scalars
  set vVectors tmp-geom_mapScalars-vectors
  set pointLocator tmp-geom_mapScalars-pointlocator
  set outputObj tmp-geom_mapScalars-outputObj
  set tmpresult tmp-geom_mapScalars-tmpresult

  catch {$myFE Delete}
  catch {repos_delete -obj $meshFreeEdges}
  catch {repos_delete -obj $segmentation}
  catch {$myLinFilt Delete}
  catch {repos_delete -obj $extrudedMeshWall}
  catch {repos_delete -obj $extrudedSegWall}
  catch {repos_delete -obj $tmpresult}
  catch {$outputObj Delete}
  catch {$pointLocator Delete}
  catch {$vVectors Delete}
  catch {$vScalars Delete}

  # extract the free edges from mesh
  puts "Find free edges of inlet mesh face."
  vtkFeatureEdges $myFE
  $myFE SetInputDataObject [repos_exportToVtk -src $inlet_mesh_face]
  $myFE FeatureEdgesOff
  $myFE NonManifoldEdgesOff
  $myFE BoundaryEdgesOn
  $myFE ColoringOff
  $myFE Update
  repos_importVtkPd -src [$myFE GetOutput] -dst $meshFreeEdges

  # need extruded object to do intersections

  # extrude mesh free edges
  vtkLinearExtrusionFilter $myLinFilt
  $myLinFilt SetExtrusionTypeToVectorExtrusion
  $myLinFilt SetInputDataObject [repos_exportToVtk -src $meshFreeEdges]
  $myLinFilt SetVector 0 0 1
  $myLinFilt SetScaleFactor 2
  $myLinFilt Update
  repos_importVtkPd -src [$myLinFilt GetOutput] -dst $extrudedMeshWall

  # create an interior (non-boundary) node list
  puts "Find interior nodes on mesh face (i.e. non-boundary nodes)."
  geom_getSubsetOfPts $inlet_mesh_face $meshFreeEdges 0.001 nodes
  puts "Found [llength $nodes] interior nodes."

  # get the centers of each object
  set ctrMesh [geom_avgPt -obj $meshFreeEdges]
  puts "Center of mesh face: $ctrMesh"

  # create a new set of scalars and vectors
  vtkFloatArray $vScalars
  $vScalars SetNumberOfComponents 1
  $vScalars Allocate 100 100
  vtkFloatArray $vVectors
  $vVectors SetNumberOfComponents 3
  $vVectors Allocate 100 100

  # create point locator
  vtkPointLocator $pointLocator
  $pointLocator SetDataSet [repos_exportToVtk -src $inlet_mesh_face]
  $pointLocator AutomaticOn
  $pointLocator SetTolerance 0.001
  $pointLocator BuildLocator

  # this loop effectively sets only the boundary nodes to have a value of
  # -radmax
  for {set i 0} {$i < [[repos_exportToVtk -src $inlet_mesh_face] GetNumberOfPoints]} {incr i} {
    $vScalars InsertNextTuple1 [expr -1.0*$radmax]
  }

  # now loop over the nodes calculating the velocity for each mesh node

  set counter 0

  foreach node $nodes {

    set r_m_pt [math_subVectors $node $ctrMesh]
    set r_m_pt [list [lindex $r_m_pt 0] [lindex $r_m_pt 1] 0]
    set r_m [math_magnitude $r_m_pt]

    set angleDeg [math_radToDeg [expr atan2(double([lindex $r_m_pt 1]),double([lindex $r_m_pt 0]))]]

    #set circle [math_circlePt $angleDeg 500.0]
    set circle [math_circlePt $angleDeg 10.0]
    set outsidePtMesh [list [expr [lindex $ctrMesh 0]+[lindex $circle 0]] \
                            [expr [lindex $ctrMesh 1]+[lindex $circle 1]] 1]

    # if we can't intersect directly, try and get close
    if [catch {set bdryPtMesh [geom_intersectWithLine -obj $extrudedMeshWall \
                            -pt0 [list [lindex $ctrMesh 0] [lindex $ctrMesh 1] 1] \
				   -pt1 $outsidePtMesh]}] {
      puts "set bdryPtMesh \[geom_intersectWithLine -obj $extrudedMeshWall \
                            -pt0 [list [lindex $ctrMesh 0] [lindex $ctrMesh 1] 1] \
                            -pt1 $outsidePtMesh\]"
      # arbitrarily add a degree and try again and then give up
      set circle [math_circlePt [expr $angleDeg + 1.0] 10.0]
      set outsidePtMesh [list [expr [lindex $ctrMesh 0]+[lindex $circle 0]] \
                              [expr [lindex $ctrMesh 1]+[lindex $circle 1]] 1]
      set bdryPtMesh [geom_intersectWithLine -obj $extrudedMeshWall \
                            -pt0 [list [lindex $ctrMesh 0] [lindex $ctrMesh 1] 1] \
				   -pt1 $outsidePtMesh]
    }

    set bdryPtMesh [list [lindex $bdryPtMesh 0] [lindex $bdryPtMesh 1] 0]

    set R_m_pt [math_subVectors $bdryPtMesh $ctrMesh]
    set R_m_pt [list [lindex $R_m_pt 0] [lindex $R_m_pt 1] 0]
    set R_m [math_magnitude $R_m_pt]

    if {$r_m > $R_m} {
      puts "ERROR:  inside radius ($r_m) exceeds outside radius ($R_m)."
      return -code error "ERROR:  inside radius ($r_m) exceeds outside radius ($R_m)."
    }

    set R_pc $radmax

    set r_pc [expr double($r_m*$R_pc)/double($R_m)]

    if {$r_pc > $R_pc} {
      puts "ERROR:  inside radius ($r_pc) exceeds outside radius ($R_pc)."
      return -code error "ERROR:  inside radius ($r_pc) exceeds outside radius ($R_pc)."
    }

    # debugging graphics
    if {$counter < 0} {
        set r 0.1
	catch {repos_delete -obj line1}
        catch {repos_delete -obj line2}
        catch {repos_delete -obj sCtrMesh}
        catch {repos_delete -obj sCtrPC}
        catch {repos_delete -obj sNode}
        catch {repos_delete -obj sPt}
        catch {repos_delete -obj sBdryMesh}
        catch {repos_delete -obj sBdryPC}
        solid_sphere -r $r -ctr $ctrMesh -result sCtrMesh
        solid_sphere -r $r -ctr $ctrPCMRI -result sCtrPC
        solid_sphere -r $r -ctr $node -result sNode
        solid_sphere -r $r -ctr $pt -result sPt
        solid_sphere -r $r -ctr $bdryPtMesh -result sBdryMesh
        solid_sphere -r $r -ctr $bdryPtSeg -result sBdryPC
        geom_mkLinesFromPts [list $ctrMesh $bdryPtMesh] line1 0
        geom_mkLinesFromPts [list $ctrPCMRI $bdryPtSeg] line2 0
	repos_setLabel -obj line1 -key color -value blue
        repos_setLabel -obj line2 -key color -value red
        repos_setLabel -obj sCtrMesh -key color -value yellow
        repos_setLabel -obj sCtrPC -key color -value yellow
        repos_setLabel -obj sNode -key color -value green
        repos_setLabel -obj sPt -key color -value green
        repos_setLabel -obj sBdryMesh -key color -value white
        repos_setLabel -obj sBdryPC -key color -value white
        catch {repos_setLabel -obj $meshFreeEdges -key color -value blue}
        catch {repos_setLabel -obj $segmentation -key color -value red}
        gdscView sCtrMesh sCtrPC sNode sPt sBdryMesh sBdryPC line1 line2 $segmentation $meshFreeEdges
        incr counter
    }

    # update velocities for mesh
    set ptId [$pointLocator FindClosestPoint [lindex $node 0] [lindex $node 1] [lindex $node 2]]
    $vScalars SetTuple1 $ptId $r_pc

    #puts "r_m: $r_m  R_m: $R_m  r_pc: $r_pc  R_pc: $R_pc  angle: $angleDeg ptId: $ptId"
  }

  # create the output object
  vtkPolyData $outputObj
  $outputObj SetPoints [[repos_exportToVtk -src $inlet_mesh_face] GetPoints]
  $outputObj CopyStructure [repos_exportToVtk -src $inlet_mesh_face]
  [$outputObj GetPointData] SetScalars $vScalars
  catch {repos_delete -obj $result}
  repos_importVtkPd -src $outputObj -dst $result

  # clean up
  catch {$myFE Delete}
  catch {repos_delete -obj $meshFreeEdges}
  catch {repos_delete -obj $segmentation}
  catch {$myLinFilt Delete}
  catch {repos_delete -obj $extrudedMeshWall}
  catch {repos_delete -obj $extrudedSegWall}
  catch {repos_delete -obj $tmpresult}
  catch {$outputObj Delete}
  catch {$pointLocator Delete}
  catch {$vVectors Delete}
  catch {$vScalars Delete}

  return GDSC_OK

}

