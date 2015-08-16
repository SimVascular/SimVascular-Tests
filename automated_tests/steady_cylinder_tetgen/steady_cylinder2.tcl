#
#   Copyright (c) 2009-2012 Open Source Medical Software Corporation
#   All rights reserved.  
#
#  This script requires the following files:
#     solver.inp
#  and should be sourced interactively from SimVascular
#
#
global gOptions

set gOptions(meshing_solid_kernel) PolyData
set gOptions(meshing_kernel) TetGen
solid_setKernel -name PolyData
mesh_setKernel -name TetGen

set timesteps 64

# sometimes we have to invert the normal to the inflow surface
set thisFile [dict get [ info frame [ info frame ] ] file ]
set thisDir [file dirname $thisFile]
puts $thisFile
puts $thisDir

#source $thisDir/../common/executable_names.tcl.in
source $thisDir/../../common/executable_names.tcl

#
# prompt user for number of procs
#
#set num_procs [tk_dialog .askthem "Select Number of Processors" "Number of Processors \n to use?" question 0 1 2 3 4]
set num_procs 0
incr num_procs

# prompt user for linear solver
#

#set selected_LS [tk_dialog .askthem "Select Linear Solver" "Use which linear solver?" question 0 "  svLS  " " leslib "]
set selected_LS 0
#set rundir [clock format [clock seconds] -format "%m-%d-%Y-%H%M%S"]
set rundir "$thisDir/test"
set fullrundir [file join [pwd] $rundir]
file delete -force $fullrundir 
file mkdir $fullrundir

if {$num_procs == 1} {
  set fullsimdir $fullrundir
} else {
  set fullsimdir [file join $fullrundir $num_procs-procs_case]
}

# create model, mesh, and bc files
source $thisDir/steady-create_model_and_mesh.tcl

demo_create_model $thisDir $fullrundir
demo_create_mesh  $fullrundir
demo_create_flow_files $fullrundir

#
#  Create script file for presolver
#

#foreach i [mymesh Print] {
#  set [lindex $i 0] [lindex $i 1]
#}

puts "Create script file for presolver."
set fp [open [file join $fullrundir cylinder.svpre] w]
puts $fp "mesh_and_adjncy_vtu [file join $fullrundir mesh-complete cylinder.mesh.vtu]"
puts $fp "prescribed_velocities_vtp [file join $fullrundir mesh-complete mesh-surfaces inflow.vtp]"
puts $fp "noslip_vtp [file join $fullrundir mesh-complete mesh-surfaces wall.vtp]"
puts $fp "zero_pressure_vtp [file join $fullrundir mesh-complete mesh-surfaces outlet.vtp]"
puts $fp "set_surface_id_vtp [file join $fullrundir mesh-complete cylinder.exterior.vtp] 1"

puts $fp "fluid_density 0.00106"
puts $fp "fluid_viscosity 0.004"
puts $fp "bct_period 0.2"
puts $fp "bct_analytical_shape plug"
puts $fp "bct_point_number 2"
puts $fp "bct_fourier_mode_number 1"
puts $fp "bct_create [file join $fullrundir mesh-complete mesh-surfaces inflow.vtp] [file join $fullrundir flow-files inflow.flow]"
puts $fp "bct_write_dat [file join $fullrundir bct.dat]"
puts $fp "bct_write_vtp [file join $fullrundir bct.vtp]"

puts $fp "write_numstart 0 [file join $fullrundir numstart.dat]"

puts $fp "write_geombc [file join $fullrundir geombc.dat.1]"
puts $fp "write_restart [file join $fullrundir restart.0.1]"
close $fp

#
#  Call pre-processor
#
puts "Run cvpresolver."
catch {exec $PRESOLVER [file join $fullrundir cylinder.svpre]} msg
puts $msg

#
# set number of timesteps
#

puts "Number of timesteps ($timesteps)"

#
#  Run solver.
#

puts "Run Solver."

#
#  more files needed by solver
#

#file copy [file join $fullrundir bct.dat.inflow] [file join $fullrundir bct.dat]
#set fp [open [file join $fullrundir numstart.dat] w]
#fconfigure $fp -translation lf
#puts $fp "0"
#close $fp

set infp [open $thisDir/solver.inp r]

set outfp [open $fullrundir/solver.inp w]
fconfigure $outfp -translation lf
#
#if {$use_ascii_format == 0} {
#   set file_format binary
#} else {
#   set file_format ascii
#}

while {[gets $infp line] >= 0} {
  regsub -all my_initial_time_increment $line [expr 0.128/$timesteps] line
  regsub -all my_number_of_time_steps $line [expr $timesteps] line
#  regsub -all my_output_format $line $file_format line
  if {$selected_LS} {
       regsub -all "\#leslib_linear_solver" $line {} line
  } else {
       regsub -all "\#svls_linear_solver" $line {} line
  }
  puts $outfp $line
}
close $infp
close $outfp

global tcl_platform
if {$tcl_platform(platform) == "windows"} {
#  set npflag "-noprompt -localroot -localonly -user 1 -n"
  set npflag "-np"
} else {
  set npflag "-np"
}

proc handle { args } {
  puts -nonewline [ set [ lindex $args 0 ] ]
}

set fp [open [file join $fullrundir solver.log] w]
fconfigure $fp -translation lf
puts $fp "Start running solver..."
close $fp

set ::tail_solverlog {}
tail [file join $fullrundir solver.log] .+ 1000 ::tail_solverlog
trace variable ::tail_solverlog w handle

eval exec \"$MPIEXEC\" -wdir \"$fullrundir\" $npflag $num_procs -env FLOWSOLVER_CONFIG \"$FLOWSOLVER_CONFIG\" \"$SOLVER\" >>& [file join $rundir solver.log] &

set endstep 0
while {$endstep < $timesteps} {
  set waittwoseconds 0
  after 2000 set waittwoseconds 1
  vwait waittwoseconds
  if {![file exists [file join $fullsimdir "numstart.dat"]]} continue
  set fp [open [file join $fullsimdir "numstart.dat"] r]
  gets $fp endstep
  close $fp
  set endstep [string trim $endstep]
}

cancelTail [file join $fullrundir solver.log]

#
#  Create ParaView files
#
puts "Reduce restart files."
#if {$use_ascii_format != 0} {
#  set aflag "-nonbinary"
#} else {
#  set aflag ""
#}

puts "exec $POSTSOLVER -indir $fullsimdir -outdir $fullrundir -start 1 -stop 64 -incr 1 -sim_units_mm -vtkcombo -vtu cylinder_results.vtu -vtp cylinder_results.vtp"

if [catch {exec $POSTSOLVER -indir $fullsimdir -outdir $fullrundir -start 1 -stop 64 -incr 1 -sim_units_mm -vtkcombo -vtu cylinder_results.vtu -vtp cylinder_results.vtp} msg] {
   puts $msg
   return -code error "ERROR running postsolver!"
}

#after 1000
#mainGUIexit
#
#  compare results
#

source $thisDir/steady-compare_with_analytic.tcl


