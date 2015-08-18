#
#   Copyright (c) 2015 Stanford University
#   All rights reserved.  
#
#   Portions of the code Copyright (c) 2009-2012 Open Source Medical Software Corporation
#
#  This script requires the following files:
#     solver.inp
#  and should be sourced interactively from SimVascular
#

proc adaptor_cylinder_create_bc_files_generic { dstdir adapted adapt_step} {

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
  
  puts "Create script file for presolver."
  set fp [open [file join $dstdir cylinder.svpre] w]
  #if {$use_ascii_format > 0} {
  #  puts $fp "ascii_format"
  #}
  #puts $fp "verbose"
  puts $fp "mesh_and_adjncy_vtu [file join $dstdir mesh-complete cylinder.mesh.vtu]"
  puts $fp "prescribed_velocities_vtp [file join $dstdir mesh-complete mesh-surfaces inflow.vtp]"
  puts $fp "noslip_vtp [file join $dstdir mesh-complete mesh-surfaces wall.vtp]"
  puts $fp "zero_pressure_vtp [file join $dstdir mesh-complete mesh-surfaces outlet.vtp]"
  puts $fp "set_surface_id_vtp [file join $dstdir mesh-complete cylinder.exterior.vtp] 1"
  
  puts $fp "fluid_density 0.00106"
  puts $fp "fluid_viscosity 0.004"
  puts $fp "bct_period 0.2"
  puts $fp "bct_analytical_shape plug"
  puts $fp "bct_point_number 201"
  puts $fp "bct_fourier_mode_number 10"
  puts $fp "bct_create [file join $dstdir mesh-complete mesh-surfaces inflow.vtp] [file join $dstdir flow-files inflow.flow]"
  puts $fp "bct_write_dat [file join $dstdir bct.dat]"
  puts $fp "bct_write_vtp [file join $dstdir bct.vtp]"
  
  puts $fp "write_geombc [file join $dstdir geombc.dat.1]"
  
  if {$adapted == 0} {
    puts $fp "write_restart [file join $dstdir restart.0.1]"
    puts $fp "write_numstart 0 [file join $dstdir numstart.dat]"
  } else {
    puts $fp "write_numstart $adapt_step [file join $dstdir numstart.dat]"
  }
  close $fp
  
  #
  #  Call pre-processor
  #
  puts "Run cvpresolver."
  global PRESOLVER
  catch {exec $PRESOLVER [file join $dstdir cylinder.svpre]} msg
  puts $msg
  
}

