
proc steady_cylinder_create_flow_files_generic {dstdir} {

  # Write steady flowrate
  file mkdir [file join $dstdir flow-files]
  set fp [open [file join $dstdir flow-files inflow.flow] "w"]
  puts $fp "\#  Time (sec)   Flow (mm^3/sec)"
  puts $fp "0   -1570.796327"
  puts $fp "0.2 -1570.796327"
  close $fp

}