#
#   Copyright (c) 2009-2012 Open Source Medical Software Corporation
#   All rights reserved.  
#
#  This script requires the following files:
#     solver.inp
#  and should be sourced interactively from SimVascular
#

set use_ascii_format 0

source executable_names.tcl

#
# prompt user for number of procs
#

set num_procs [tk_dialog .askthem "Select Number of Processors" "Number of Processors \n to use?" question 0 1 2 3 4]
incr num_procs

set rundir [clock format [clock seconds] -format "%m-%d-%Y-%H%M%S"]
set fullrundir [file join [pwd] $rundir]
file mkdir $fullrundir

set rigid_steady_dir  [file join $fullrundir rigid_steady]
set def_steady_dir [file join $fullrundir deformable_steady]
set def_pulse_dir  [file join $fullrundir deformable_pulsatile]
file mkdir $rigid_steady_dir
file mkdir $def_steady_dir
file mkdir $def_pulse_dir
 
if {$num_procs == 1} {
  set rigid_steady_sim_dir $rigid_steady_dir
  set def_steady_sim_dir   $def_steady_dir
  set def_pulse_sim_dir    $def_pulse_dir
} else {
  set rigid_steady_sim_dir  [file join $rigid_steady_dir $num_procs-procs_case]
  set def_steady_sim_dir [file join $def_steady_dir $num_procs-procs_case]
  set def_pulse_sim_dir  [file join $def_pulse_dir $num_procs-procs_case]
}

# copy files into rundir
file copy deformable-flow-files [file join $fullrundir flow-files]

# create model, mesh, and bc files
source deformable-create_model_and_mesh.tcl
demo_create_model $fullrundir
demo_create_mesh  $fullrundir
demo_create_bc_files $fullrundir

file copy [file join $fullrundir bct.dat.inflow.steady]    [file join $rigid_steady_dir bct.dat]
file copy [file join $fullrundir bct.dat.inflow.steady]    [file join $def_steady_dir bct.dat]
file copy [file join $fullrundir bct.dat.inflow.pulsatile] [file join $def_pulse_dir bct.dat]

#
#  Create script file for cvpresolver
#
foreach i [mymesh Print] {
  set [lindex $i 0] [lindex $i 1]
}

puts "Create script file for presolver."
set fp [open [file join $fullrundir rigid_steady_cylinder.cvpre] w]
if {$use_ascii_format > 0} {
  puts $fp "ascii_format"
}
puts $fp "number_of_variables 5"
puts $fp "number_of_nodes $number_of_nodes"
puts $fp "number_of_elements $number_of_elements"
puts $fp "number_of_mesh_edges $number_of_mesh_edges"
puts $fp "number_of_mesh_faces $number_of_mesh_faces"
puts $fp "nodes [file join $fullrundir cylinder.coordinates.gz]"
puts $fp "elements [file join $fullrundir cylinder.connectivity.gz]"
puts $fp "boundary_faces [file join $fullrundir all.ebc.gz]"
puts $fp "adjacency [file join $fullrundir cylinder.xadj.gz]"
puts $fp "prescribed_velocities [file join $fullrundir mesh-surfaces inflow.nbc.gz]"
puts $fp "noslip [file join $fullrundir mesh-surfaces wall.nbc.gz]"
puts $fp "pressure [file join $fullrundir mesh-surfaces outlet.ebc.gz] 116490.0"
puts $fp "set_surface_id [file join $fullrundir all.ebc.gz] 1"
puts $fp "set_surface_id [file join $fullrundir mesh-surfaces outlet.ebc.gz] 2"
puts $fp "initial_pressure 120000.0"
puts $fp "initial_velocity 0.0 0.0 0.01"
puts $fp "write_geombc [file join $rigid_steady_dir geombc.dat.1]"
puts $fp "write_restart [file join $rigid_steady_dir restart.0.1]"
close $fp

#
#  Call pre-processor
#
puts "Run cvpresolver."
catch {exec $PRESOLVER [file join $fullrundir rigid_steady_cylinder.cvpre]} msg
puts $msg

#
# set number of timesteps
#

set timesteps 100
puts "Number of timesteps ($timesteps)"

#
#  Run solver.
#

puts "Run Solver."

#
#  more files needed by solver
#

set fp [open [file join $rigid_steady_dir numstart.dat] w]
fconfigure $fp -translation lf
puts $fp "0"
close $fp

set infp [open solver.inp.deformable r]

set outfp [open [file join $rigid_steady_dir solver.inp] w]
fconfigure $outfp -translation lf

if {$use_ascii_format == 0} {
   set file_format binary
} else {
   set file_format ascii
}

while {[gets $infp line] >= 0} {
  regsub -all my_initial_time_increment $line 0.001 line
  regsub -all my_number_of_time_steps $line [expr $timesteps] line
  regsub -all my_output_format $line $file_format line
  regsub -all my_deformable_flag $line False line
  regsub -all my_rho_infinity $line 0.5 line
  regsub -all my_step_construction $line "0 1 0 1 0 1    \# this is the standard three iteration" line
  puts $outfp $line
}
close $infp
close $outfp

global tcl_platform
if {$tcl_platform(platform) == "windows"} {
  set npflag "-localonly"
} else {
  set npflag "-np"
}

proc handle { args } {
  puts -nonewline [ set [ lindex $args 0 ] ]
}

set fp [open [file join $rigid_steady_dir solver.log] w]
puts $fp "Start running solver..."
close $fp

set ::tail_solverlog {}
tail [file join $rigid_steady_dir solver.log] .+ 1000 ::tail_solverlog
trace variable ::tail_solverlog w handle

eval exec \"$MPIEXEC\" -wdir \"$rigid_steady_dir\" $npflag $num_procs -env FLOWSOLVER_CONFIG \"$FLOWSOLVER_CONFIG\" \"$SOLVER\" >>& [file join $rigid_steady_dir solver.log] &
#eval exec   $MPIEXEC   -wdir   $rigid_steady_dir   $npflag $num_procs -env FLOWSOLVER_CONFIG   $FLOWSOLVER_CONFIG     $SOLVER solver.inp >>& [file join $rigid_steady_dir solver.log] &

set endstep 0
while {$endstep < $timesteps} {
  set waittwoseconds 0
  after 2000 set waittwoseconds 1
  vwait waittwoseconds
  set fp [open [file join $rigid_steady_sim_dir "numstart.dat"] r]
  gets $fp endstep
  close $fp
  set endstep [string trim $endstep]
}

cancelTail [file join $rigid_steady_dir solver.log]

#
#  Create vis files
#
puts "Reduce restart files."
if {$use_ascii_format != 0} {
  set aflag "-nonbinary"
} else {
  set aflag ""
}

for {set i 0} {$i <= $endstep} {incr i 25} {
   if [catch {exec $POSTSOLVER -dir $rigid_steady_sim_dir -sn $i $aflag -bflux -vis [file join $rigid_steady_sim_dir cylinder_res$i.vis]} msg] {
     puts $msg
     return -code error "ERROR running cvpostsolver!"
   }
}
if [catch {exec $POSTSOLVER -dir $rigid_steady_sim_dir -sn 0 $aflag -vismesh [file join $rigid_steady_sim_dir cylinder_mesh.vis]} msg] {
  puts $msg
  return -code error "ERROR running cvpostsolver!"
}

if [catch {exec $POSTSOLVER -dir $rigid_steady_sim_dir -sn $endstep -td -ph $aflag -newsn 0} msg] {
  puts $msg
  return -code error "ERROR running cvpostsolver!"
}


###
###
###    
###   DEFORMABLE RIGID CASE
###
###
###

puts "Create script file for presolver."
set fp [open [file join $fullrundir rigid_deformable_cylinder.cvpre] w]
if {$use_ascii_format > 0} {
  puts $fp "ascii_format"
}
puts $fp "number_of_variables 5"
puts $fp "number_of_nodes $number_of_nodes"
puts $fp "number_of_elements $number_of_elements"
puts $fp "number_of_mesh_edges $number_of_mesh_edges"
puts $fp "number_of_mesh_faces $number_of_mesh_faces"
puts $fp "nodes [file join $fullrundir cylinder.coordinates.gz]"
puts $fp "elements [file join $fullrundir cylinder.connectivity.gz]"
puts $fp "boundary_faces [file join $fullrundir all.ebc.gz]"
puts $fp "adjacency [file join $fullrundir cylinder.xadj.gz]"
puts $fp "prescribed_velocities [file join $fullrundir mesh-surfaces inflow.nbc.gz]"
puts $fp "deformable_wall [file join $fullrundir mesh-surfaces wall.ebc.gz]"
puts $fp "pressure [file join $fullrundir mesh-surfaces outlet.ebc.gz] 116490.0"
puts $fp "set_surface_id [file join $fullrundir all.ebc.gz] 1"
puts $fp "set_surface_id [file join $fullrundir mesh-surfaces outlet.ebc.gz] 2"
puts $fp "deformable_create_mesh [file join $fullrundir mesh-surfaces wall.ebc.gz]"
puts $fp "deformable_write_vtk_mesh [file join $def_steady_dir wall-mesh.vtk]"
puts $fp "deformable_write_feap [file join $def_steady_dir matlab.dat]"
puts $fp "deformable_Evw 4144000.0"
puts $fp "deformable_nuvw 0.5"
puts $fp "deformable_thickness 0.1"
puts $fp "deformable_pressure 120000.0"
puts $fp "deformable_kcons 0.833333"
puts $fp "deformable_solve"
puts $fp "read_restart_solution [file join $rigid_steady_sim_dir restart.0.0]"
puts $fp "read_restart_accelerations [file join $rigid_steady_sim_dir restart.0.0]"
puts $fp "write_geombc [file join $def_steady_dir geombc.dat.1]"
puts $fp "write_geombc [file join $def_pulse_dir geombc.dat.1]"
puts $fp "write_restart [file join $def_steady_dir restart.0.1]"
close $fp

#
#  Call pre-processor
#
puts "Run cvpresolver."
catch {exec $PRESOLVER [file join $fullrundir rigid_deformable_cylinder.cvpre]} msg
puts $msg

#
# set number of timesteps
#

set timesteps 100
puts "Number of timesteps ($timesteps)"

#
#  Run solver.
#

puts "Run Solver."

#
#  more files needed by solver
#

set fp [open [file join $def_steady_dir numstart.dat] w]
fconfigure $fp -translation lf
puts $fp "0"
close $fp

set infp [open solver.inp.deformable r]

set outfp [open [file join $def_steady_dir solver.inp] w]
fconfigure $outfp -translation lf

if {$use_ascii_format == 0} {
   set file_format binary
} else {
   set file_format ascii
}

while {[gets $infp line] >= 0} {
  regsub -all my_initial_time_increment $line 0.0004 line
  regsub -all my_number_of_time_steps $line [expr $timesteps] line
  regsub -all my_output_format $line $file_format line
  regsub -all my_deformable_flag $line True line
  regsub -all my_rho_infinity $line 0.0 line
  regsub -all my_step_construction $line "0 1 0 1 0 1 0 1   \# this is the standard four iteration" line
  puts $outfp $line
}
close $infp
close $outfp

global tcl_platform
if {$tcl_platform(platform) == "windows"} {
  set npflag "-localonly"
} else {
  set npflag "-np"
}

proc handle { args } {
  puts -nonewline [ set [ lindex $args 0 ] ]
}

set fp [open [file join $def_steady_dir solver.log] w]
puts $fp "Start running solver..."
close $fp

set ::tail_solverlog {}
tail [file join $def_steady_dir solver.log] .+ 1000 ::tail_solverlog
trace variable ::tail_solverlog w handle

eval exec \"$MPIEXEC\" -wdir \"$def_steady_dir\" $npflag $num_procs -env FLOWSOLVER_CONFIG \"$FLOWSOLVER_CONFIG\" \"$SOLVER\" >>& [file join $def_steady_dir solver.log] &
#exec        $MPIEXEC   -wdir   $def_steady_dir   $npflag $num_procs -env FLOWSOLVER_CONFIG   $FLOWSOLVER_CONFIG     $SOLVER solver.inp >>& [file join $def_steady_dir solver.log] &

set endstep 0
while {$endstep < $timesteps} {
  set waittwoseconds 0
  after 2000 set waittwoseconds 1
  vwait waittwoseconds
  set fp [open [file join $def_steady_sim_dir "numstart.dat"] r]
  gets $fp endstep
  close $fp
  set endstep [string trim $endstep]
}

cancelTail [file join $def_steady_dir solver.log]

#
#  Create vis files
#
puts "Reduce restart files."
if {$use_ascii_format != 0} {
  set aflag "-nonbinary"
} else {
  set aflag ""
}

for {set i 0} {$i <= $endstep} {incr i 25} {
   if [catch {exec $POSTSOLVER -dir $def_steady_sim_dir -sn $i $aflag -bflux -vis [file join $def_steady_sim_dir cylinder_res$i.vis]} msg] {
     puts $msg
     return -code error "ERROR running cvpostsolver!"
   }
}
if [catch {exec $POSTSOLVER -dir $def_steady_sim_dir -sn 0 $aflag -vismesh [file join $def_steady_sim_dir cylinder_mesh.vis]} msg] {
  puts $msg
  return -code error "ERROR running cvpostsolver!"
}

if [catch {exec $POSTSOLVER -dir $def_steady_sim_dir -sn $timesteps -td -disp -ph $aflag -newsn 0} msg] {
  puts $msg
  return -code error "ERROR running cvpostsolver!"
}


###
###
###    
###   DEFORMABLE PULSATILE CASE
###
###
###

file copy [file join $def_steady_sim_dir restart.0.0] [file join $def_pulse_dir restart.0.1]

#
# set number of timesteps
#

set timesteps 2750

puts "Number of timesteps ($timesteps)"

#
#  Run solver.
#

puts "Run Solver."

#
#  more files needed by solver
#

set fp [open [file join $def_pulse_dir numstart.dat] w]
fconfigure $fp -translation lf
puts $fp "0"
close $fp

set infp [open solver.inp.deformable r]

set outfp [open [file join $def_pulse_dir solver.inp] w]
fconfigure $outfp -translation lf

if {$use_ascii_format == 0} {
   set file_format binary
} else {
   set file_format ascii
}

while {[gets $infp line] >= 0} {
  regsub -all my_initial_time_increment $line 0.0004 line
  regsub -all my_number_of_time_steps $line [expr $timesteps] line
  regsub -all my_output_format $line $file_format line
  regsub -all my_deformable_flag $line True line
  regsub -all my_rho_infinity $line 0.0 line
  regsub -all my_step_construction $line "0 1 0 1 0 1 0 1   \# this is the standard four iteration" line
  puts $outfp $line
}
close $infp
close $outfp

global tcl_platform
if {$tcl_platform(platform) == "windows"} {
  set npflag "-localonly"
} else {
  set npflag "-np"
}

proc handle { args } {
  puts -nonewline [ set [ lindex $args 0 ] ]
}

set fp [open [file join $def_pulse_dir solver.log] w]
puts $fp "Start running solver..."
close $fp

set ::tail_solverlog {}
tail [file join $def_pulse_dir solver.log] .+ 1000 ::tail_solverlog
trace variable ::tail_solverlog w handle

eval exec \"$MPIEXEC\" -wdir \"$def_pulse_dir\" $npflag $num_procs -env FLOWSOLVER_CONFIG \"$FLOWSOLVER_CONFIG\" \"$SOLVER\" >>& [file join $def_pulse_dir solver.log] &
#exec       $MPIEXEC   -wdir   $def_pulse_dir   $npflag $num_procs -env FLOWSOLVER_CONFIG   $FLOWSOLVER_CONFIG     $SOLVER solver.inp >>& [file join $def_pulse_dir solver.log] &

set endstep 0
while {$endstep < $timesteps} {
  set waittwoseconds 0
  after 2000 set waittwoseconds 1
  vwait waittwoseconds
  set fp [open [file join $def_pulse_sim_dir "numstart.dat"] r]
  gets $fp endstep
  close $fp
  set endstep [string trim $endstep]
}

cancelTail [file join $def_pulse_dir solver.log]

#
#  Create vis files
#
puts "Reduce restart files."
if {$use_ascii_format != 0} {
  set aflag "-nonbinary"
} else {
  set aflag ""
}

for {set i 0} {$i <= $endstep} {incr i 25} {
   if [catch {exec $POSTSOLVER -dir $def_pulse_sim_dir -sn $i $aflag -bflux -vis [file join $def_pulse_sim_dir cylinder_res$i.vis]} msg] {
     puts $msg
     return -code error "ERROR running cvpostsolver!"
   }
}
if [catch {exec $POSTSOLVER -dir $def_pulse_sim_dir -sn 0 $aflag -vismesh [file join $def_pulse_sim_dir cylinder_mesh.vis]} msg] {
  puts $msg
  return -code error "ERROR running cvpostsolver!"
}

if [catch {exec $POSTSOLVER -dir $def_pulse_sim_dir -sn $timesteps -td -ph $aflag -newsn 0} msg] {
  puts $msg
  return -code error "ERROR running cvpostsolver!"
}




