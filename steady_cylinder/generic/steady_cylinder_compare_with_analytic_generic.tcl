#
#   Copyright (c) 2009-2012 Open Source Medical Software Corporation
#   All rights reserved.  
#

#
#  user defined list of res files to compare
#

set tlist [list step_2 \
                step_4 \
	        step_6 \
                step_8 \
                step_10 \
                step_16 \
                step_32 \
          ]

set vturesultsfn [file join $fullrundir cylinder_results.vtu]

set rlist [list 2 4 6 8 10 16 32]

set Q 1570.795327
set radius 2.0

set Vmax [expr 2.0*$Q/([math_pi]*$radius*$radius)]

# read the rsults

set ugreader my-ug-reader
catch {$ugreader Delete}
vtkXMLUnstructuredGridReader $ugreader
$ugreader SetFileName $vturesultsfn
$ugreader Update

set simres [$ugreader GetOutput]

# read outflow mesh face
catch {repos_delete -obj outflow}
repos_readXMLPolyData [file join $fullrundir mesh-complete mesh-surfaces outlet.vtp] outflow
set numPts [geom_numPts -obj outflow]
set outflowObj [repos_exportToVtk -src outflow]
[$outflowObj GetPointData] SetActiveScalars "GlobalNodeID"
set outflowNodeIDs [[$outflowObj GetPointData] GetScalars]

# now calculate flow rate for each time point
set myVectors tmp-myVectors

set countem 0

foreach restimestep $rlist {

  set time [lindex $tlist $countem]
  incr countem

  catch {unset results}

  catch {$myVectors Delete}
  vtkFloatArray $myVectors; $myVectors SetNumberOfComponents 3
  $myVectors Allocate 1000 1000

  [$simres GetPointData] SetActiveScalars "pressure_[format %05i $restimestep]"
  [$simres GetPointData] SetActiveVectors "velocity_[format %05i $restimestep]"

  set vsoln [[$simres GetPointData] GetVectors]
  
  for {set i 0} {$i < $numPts} {incr i} {
    set node [expr int([$outflowNodeIDs GetValue $i])]
    # nodes in vtk start at 0, so subtract 1 off
    set node [expr $node - 1]
    set vec [$vsoln GetTuple3 $node]
    #puts "processing vtk node: $node vec: $vec"
    $myVectors InsertNextTuple3 [lindex $vec 0] [lindex $vec 1] [lindex $vec 2]
  }

  # associate vectors with polydata
  [$outflowObj GetPointData] SetVectors $myVectors

  # calculate profile
  for {set j -20} {$j < 21} {incr j} {
      set r [format {%.4f} [expr double($j)/double(10)]]
      set results($restimestep,$r) {}
      catch {set results($restimestep,$r) [list $r [lindex [geom_interpolateVector -obj outflow -pt [list $r 0 0]] 2]]}
  }

  # now write out the results
  set fp [open [file join $fullrundir profiles_for_$time] w]
  fconfigure $fp -translation lf
  puts -nonewline $fp "radius\tr/R\tanalytic\t"
  puts $fp ""
  for {set j -20} {$j < 21} {incr j} {
    set r [format {%.4f} [expr double($j)/double(10)]]
    puts -nonewline $fp "$r\t[expr double($r)/$radius]\t"

    puts -nonewline $fp [format "%f\t" [expr -1.0*$Vmax*(1-($r*$r)/($radius*$radius))]]
    if {[llength $results($restimestep,$r)] == 2} {
      puts -nonewline $fp "[lindex $results($restimestep,$r) 1]\t"
    } else {
      puts -nonewline $fp "\t"
    }
    puts $fp ""
  }
  close $fp

}

proc demoCreateGraph {graphname title analytic feasoln xoffset yoffset} {

  set canvasWidth 500
  set canvasHeight 500

  set guiDEMOgraph1 $graphname

  toplevel .$guiDEMOgraph1  \
    -background {white}

  # Window manager configurations
  wm positionfrom .$guiDEMOgraph1 program
  wm sizefrom .$guiDEMOgraph1 program
  wm maxsize .$guiDEMOgraph1 1600 1200
  wm minsize .$guiDEMOgraph1 50 50
  wm protocol .$guiDEMOgraph1 WM_DELETE_WINDOW {XFProcError {Application windows can not be destroyed.
Please use the "Current widget path:" to show/hide windows.}}
  wm title .$guiDEMOgraph1 $title

  # build widget .$guiDEMOgraph1.canvas1
  canvas .$guiDEMOgraph1.canvas1 \
    -height $canvasHeight \
    -relief {raised} \
    -width $canvasWidth \
    -background white

  # build widget .guiDEMOgraph1.button2
  button .$guiDEMOgraph1.button2 \
    -background {blue} \
    -command "destroy .$guiDEMOgraph1" \
    -font {Helvetica 10} \
    -foreground {white} \
    -text {CLOSE}

  # pack master .guiDEMOgraph1
  pack configure .$guiDEMOgraph1.canvas1
  pack configure .$guiDEMOgraph1.button2 \
    -fill both

  set fontstr  "-family System -size 8 -weight normal -underline 0 -overstrike 0"

  emu_graph::emu_graph $graphname -canvas .$guiDEMOgraph1.canvas1 \
                                  -width [expr $canvasWidth - 50] \
                                  -height [expr $canvasHeight - 50] \
                                  -font $fontstr -nticks_x 3 -nticks_y 10

  $graphname data d1 -colour green -points 0 -lines 1 -coords $analytic
  $graphname data d2 -colour red   -points 1 -lines 0 -coords $feasoln
  $graphname configure -autorange 0
  $graphname configure -xmin -1 \
                       -xmax 1
  $graphname configure -autorange 0
  $graphname configure -ymin -5 \
                       -ymax 45
  $graphname redraw

  # wait for the window to display?
  set letupdate 0
  after 100 {set letupdate 1}
  vwait letupdate

  set orgGeometry [wm geometry .$guiDEMOgraph1]
  set newGeometry "[lindex [split $orgGeometry +] 0]+$xoffset+$yoffset"
  wm geometry .$guiDEMOgraph1 $newGeometry

}

   for {set i [expr [llength $tlist] - 1]} {$i >= 0} {incr i -1} {
     set title "[file tail [pwd]]  [lindex $tlist $i]  Velocity (cm/sec) vs. r/R"
     set graphname [file tail [pwd]]-graph$i
     set fp [open [file join $fullrundir "profiles_for_[lindex $tlist $i]"] r]
     gets $fp line
     set analytic {}
     set feasoln {}
     while {[gets $fp line] > 0} {
       lappend analytic [lindex $line 1]
       lappend analytic [expr -[lindex $line 2] / 10.0]
       lappend feasoln [lindex $line 1]
       if {[llength $line] > 3} {
         lappend feasoln [expr -[lindex $line 3] / 10.0]
       } else {
         lappend feasoln 0
       }
     }
    close $fp 
    demoCreateGraph $graphname $title $analytic $feasoln [expr 100+50*$i] [expr 100+50*$i]
  }

