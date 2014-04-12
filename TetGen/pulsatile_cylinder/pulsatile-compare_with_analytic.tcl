#
#  user defined list of res files to compare
#

set tlist [list 0.025 \
                0.075 \
	        0.125 \
                0.175 \
          ]

set toverTlist [list 0.125 \
                     0.375 \
	             0.625 \
                     0.875 \
          ]

set simstepnumlist [list [expr int($timesteps*(1 + [lindex $tlist 0]/0.2)) + 1] \
		         [expr int($timesteps*(1 + [lindex $tlist 1]/0.2)) + 1] \
		         [expr int($timesteps*(1 + [lindex $tlist 2]/0.2)) + 1] \
		         [expr int($timesteps*(1 + [lindex $tlist 3]/0.2)) + 1] \
              ]

set resfn [file join $fullrundir cylinder_results.vtu]

set viscosity 0.004
set density 0.00106
set T 0.2
set Vbar 135
set radius 2.0
set omega [expr 2.0*[math_pi]/$T]

# calculate FFT terms
set pts {}
for {set i 0} {$i < 256} {incr i} {

  set dt [expr double($T)/255.0]
  set t [expr [expr double($i)*$dt]]
  set Vmean [expr $Vbar*(1.0+sin(2*[math_pi]*$t/$T))]
  set area [expr [math_pi]*$radius*$radius]

  lappend pts [list [expr double($i)*$dt] [expr $Vmean*$area]]

}
set terms [math_FFT -pts $pts -numInterpPts 256 -nterms 2]

# read outflow mesh face
catch {repos_delete -obj outflow}
repos_readXMLPolyData [file join $fullrundir mesh-complete mesh-surfaces outlet.vtp] outflow
set numPts [geom_numPts -obj outflow]
set outflowObj [repos_exportToVtk -src outflow]
set outflowScalars [[$outflowObj GetPointData] GetScalars]

puts "Reading simulation results ($resfn)."
set resReader tmp-results-reader
catch {$resReader Delete}
vtkXMLUnstructuredGridReader $resReader
$resReader SetFileName $resfn
$resReader Update

# now calculate flow rate for each time point
set myVectors tmp-myVectors

set countem 0

foreach stepnum $simstepnumlist {

  set time [lindex $tlist $countem]
  incr countem

  catch {unset results}

  catch {$myVectors Delete}
  vtkFloatArray $myVectors; $myVectors SetNumberOfComponents 3
  $myVectors Allocate 1000 1000

  set pointData [[$resReader GetOutput] GetPointData]
  set objVectors [$pointData GetArray velocity_[format "%05i" $stepnum]]

  for {set i 0} {$i < $numPts} {incr i} {
      set node [expr int([$outflowScalars GetValue $i])]
      # nodes in vtk start at 0, so subtract 1 off
      set node [expr $node - 1]
      set vec [$objVectors GetTuple3 $node]
      #puts "processing vtk node: $node vec: $vec"
      $myVectors InsertNextTuple3 [lindex $vec 0] [lindex $vec 1] [lindex $vec 2]
  }

  # associate vectors with polydata
  [$outflowObj GetPointData] SetVectors $myVectors

  # calculate profile
  for {set j -20} {$j < 21} {incr j} {
      set r [format {%.4f} [expr double($j)/double(10)]]
      set results($stepnum,$r) {}
      catch {set results($stepnum,$r) [list $r [lindex [geom_interpolateVector -obj outflow -pt [list $r 0 0]] 2]]}
  }

  # now write out the results
  set fp [open [file join $fullrundir profiles_for_$time] w]
  fconfigure $fp -translation lf
  puts -nonewline $fp "radius\tr/R\tanalytic\t"
  puts -nonewline $fp "$stepnum\t"
  puts $fp ""
  for {set j -20} {$j < 21} {incr j} {
    set r [format {%.4f} [expr double($j)/double(10)]]
    puts -nonewline $fp "$r\t[expr double($r)/$radius]\t"
    puts -nonewline $fp [format "%f\t" [expr -1.0*[math_computeWomersley -terms $terms -time $time \
                     -viscosity $viscosity -omega $omega -density $density \
                     -radmax $radius -radius $r]]]
    if {[llength $results($stepnum,$r)] == 2} {
        puts -nonewline $fp "[lindex $results($stepnum,$r) 1]\t"
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
                       -ymax 50
  $graphname redraw

  # wait for the window to display?
  set letupdate 0
  after 100 {set letupdate 1}
  vwait letupdate

  set orgGeometry [wm geometry .$guiDEMOgraph1]
  set newGeometry "[lindex [split $orgGeometry +] 0]+$xoffset+$yoffset"
  wm geometry .$guiDEMOgraph1 $newGeometry
}


   for {set i 0} {$i < 4} {incr i} {
     set title "[file tail [pwd]]  t/T = [lindex $toverTlist $i]"
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
    demoCreateGraph $graphname $title $analytic $feasoln [expr 100+$i*50] [expr 100+$i*50]
  }

