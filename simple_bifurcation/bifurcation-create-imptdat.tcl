
#
#  average the impedance values to get the resistance
#
proc avgImpVals {values} {
  # calc average of impedance values
  set sum 0
  for {set i 0} {$i < [llength $values]} {incr i} {
    set sum [expr $sum + [lindex [lindex $values $i] 1]]
  }
  set avg [expr $sum / [llength $values]]
  return $avg
}

#
#  iterate to find the LRR that gives the desired
#  effective resistance when you only keep a subset of
#  the modes
#
proc alterLRR {R rootR period numPts numKeptModes} {

  set LRR [oneD_calcLRR -numTimeSteps $numPts \
                        -resistance $R \
                        -rootRadius $rootR \
                        -period $period]

  set Z   [oneD_calcImpedance -numTimeSteps $numKeptModes \
                              -lengthRadiusRatio $LRR \
                              -rootRadius $rootR \
                              -period $period \
                              -fourier 1]
  set Z0 [lindex $Z 0]

  set Zt  [oneD_calcImpedance -numTimeSteps $numKeptModes \
                              -lengthRadiusRatio $LRR \
                              -rootRadius $rootR \
	                      -period $period]

  puts [format "\n   original   R goal: %12.3f  Z0: %12.3f  LRR: %12.3f"  $R [avgImpVals $Zt] $LRR]

  set maxNumIters 10
  set minNumIters 3

  for {set i 0} {$i < $maxNumIters} {incr i} {

    set newFn [math_linearInterp -pts $Zt -numInterpPts $numPts]
    set newZ0 [avgImpVals $newFn]

    puts [format "              R goal: %12.3f  Z0: %12.3f  LRR: %12.3f" $R $newZ0 $LRR]

    set dR [expr $Z0 - $newZ0]

    if {([expr abs($newZ0-$R)/$R] < 0.01) && ($i >= $minNumIters)} {
       break
    }

    set LRR [oneD_calcLRR -numTimeSteps $numPts \
  	                  -resistance [expr $R + $dR] \
                          -rootRadius $rootR \
                          -period $period]

    set Z   [oneD_calcImpedance -numTimeSteps $numKeptModes \
                                -lengthRadiusRatio $LRR \
                                -rootRadius $rootR \
                                -period $period \
                                -fourier 1]
    set Z0 [lindex $Z 0]

    set Zt  [oneD_calcImpedance -numTimeSteps $numKeptModes \
                                -lengthRadiusRatio $LRR \
                                -rootRadius $rootR \
  	                        -period $period]

  }

  return $LRR

}

#
#  creates an impdt.dat accounting for linear interpolation
#  of impedance function in solver
#
proc create_imptdat_file {outlets period numPts numKeptModes scale_to_mm_flag} {

  set pretty {}

  foreach outlet $outlets {
    set face  [lindex $outlet 0]
    set rootR [lindex $outlet 1]
    set R     [lindex $outlet 2]
    set sf    [lindex $outlet 3]

    set LRR [oneD_calcLRR -numTimeSteps $numPts \
                          -resistance $R \
                          -rootRadius $rootR \
                          -period $period]

    puts "work on face ($face)"
    set modLRR [alterLRR $R $rootR $period $numPts $numKeptModes]

    lappend pretty [list $face $R $LRR $modLRR $rootR]
  }

  #  output a human readable list of the changes in LRR

  puts  [format "\n%20s %15s %15s %15s %15s %15s" Outlet R LRR "modified LRR" "newZ" "effective R"]
  foreach i $pretty {
    set face   [lindex $i 0]
    set R      [lindex $i 1]
    set LRR    [lindex $i 2]
    set modLRR [lindex $i 3]
    set rootR  [lindex $i 4]
    set Z   [oneD_calcImpedance -numTimeSteps $numKeptModes \
                                -lengthRadiusRatio $modLRR \
                                -rootRadius $rootR \
                                -period $period \
                                -fourier 1]
    set Z0 [lindex $Z 0]
    set Zt  [oneD_calcImpedance -numTimeSteps $numKeptModes \
                                -lengthRadiusRatio $modLRR \
                                -rootRadius $rootR \
                                -period $period]
    set newFn [math_linearInterp -pts $Zt -numInterpPts $numPts]
    set newZ0 [avgImpVals $newFn]

    puts [format "%20s %15.2f %15.2f %15.2f %15.2f %15.2f" $face $R $LRR $modLRR $Z0 $newZ0]
  }

  #
  #  output an impt.dat file
  #

  global fullrundir
  set ofp [open [file join $fullrundir "impt.dat"] w]
  fconfigure $ofp -translation lf

  # max number of data pts
  puts $ofp $numKeptModes

  foreach i $pretty {

    set face   [lindex $i 0]
    set R      [lindex $i 1]
    set modLRR [lindex $i 3]
    set rootR  [lindex $i 4]

    # num of data pts for this face
    puts $ofp $numKeptModes

    set Zt  [oneD_calcImpedance -numTimeSteps $numKeptModes \
                                -lengthRadiusRatio $modLRR \
                                -rootRadius $rootR \
  	                        -period $period]
    # output impedance for face
    foreach j $Zt {
	if {!$scale_to_mm_flag} {
	  puts $ofp $j
	} else {
	    puts $ofp "[lindex $j 0] [expr double([lindex $j 1])/10000.0]"
	}
    }

  }

  close $ofp

}





