
proc pulsatile_cylinder_create_flow_files_generic {dstdir} {

  # Write sinusodial flowrate
  puts "Generating sinusodial volumetric flow waveform."
  set T 0.2
  set Vbar 135
  set radius 2

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

}