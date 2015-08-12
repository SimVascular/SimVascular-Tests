#
#   Copyright (c) 2009-2012 Open Source Medical Software Corporation
#   All rights reserved.  
#
#  This script requires the following files:
#     solver.inp
#  and should be sourced interactively from SimVascular
#

solid_setKernel -name Parasolid
mesh_setKernel -name MeshSim
set gOptions(meshing_kernel) MeshSim
set gOptions(meshing_solid_kernel) Parasolid

set use_ascii_format 0

source ../common/executable_names.tcl

#
# prompt user for number of procs
#

set num_procs [tk_dialog .askthem "Select Number of Processors" "Number of Processors \n to use?" question 0 1 2 3 4]
incr num_procs

# prompt user for linear solver
#

set selected_LS [tk_dialog .askthem "Select Linear Solver" "Use which linear solver?" question 0 "  memLS  " " leslib "]


#

set run_varwall [tk_dialog .askthem "Variable Wall Selection" "Add a variable wall demo?" question 0 " No  " " Yes "]



set rundir [clock format [clock seconds] -format "%m-%d-%Y-%H%M%S"]
set fullrundir [file join [pwd] $rundir]
file mkdir $fullrundir

set rigid_steady_dir  [file join $fullrundir rigid_steady]
set def_steady_dir [file join $fullrundir deformable_steady]
set def_pulse_dir  [file join $fullrundir deformable_pulsatile]
set def_varwall_dir  [file join $fullrundir deformable_varwall]

file mkdir $rigid_steady_dir
file mkdir $def_steady_dir
file mkdir $def_pulse_dir
file mkdir $def_varwall_dir


if {$num_procs == 1} {
  set rigid_steady_sim_dir $rigid_steady_dir
  set def_steady_sim_dir   $def_steady_dir
  set def_pulse_sim_dir    $def_pulse_dir
  set def_varwall_sim_dir    $def_varwall_dir
} else {
  set rigid_steady_sim_dir  [file join $rigid_steady_dir $num_procs-procs_case]
  set def_steady_sim_dir [file join $def_steady_dir $num_procs-procs_case]
  set def_pulse_sim_dir  [file join $def_pulse_dir $num_procs-procs_case]
  set def_varwall_sim_dir  [file join $def_varwall_dir $num_procs-procs_case]
}

# copy files into rundir
file copy deformable-flow-files [file join $fullrundir flow-files]
file copy solver.inp.deformable [file join $fullrundir solver.inp.deformable]
# create model, mesh, and bc files
source deformable-create_model_and_mesh.tcl
demo_create_model $fullrundir
demo_create_mesh  $fullrundir
demo_create_bc_files $fullrundir

file copy [file join $fullrundir bct.dat.inflow.steady]    [file join $rigid_steady_dir bct.dat]
file copy [file join $fullrundir bct.dat.inflow.steady]    [file join $def_steady_dir bct.dat]
file copy [file join $fullrundir bct.dat.inflow.pulsatile] [file join $def_pulse_dir bct.dat]
file copy [file join $fullrundir bct.dat.inflow.steady]    [file join $def_varwall_dir bct.dat]

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
  if {$selected_LS} {
       regsub -all "\#leslib_linear_solver" $line {} line
  } else {
       regsub -all "\#memls_linear_solver" $line {} line
  }
  puts $outfp $line
}
close $infp
close $outfp

global tcl_platform
if {$tcl_platform(platform) == "windows"} {
  set npflag "-np"
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

cd $rigid_steady_sim_dir 

puts "Reduce restart files."
if {$use_ascii_format != 0} {
  set aflag "-nonbinary"
} else {
  set aflag ""
}



for {set i 0} {$i <= $endstep} {incr i 25} {  
   if [catch {exec $POSTSOLVER  -sn $i $aflag -vis  cylinder} msg] {
     puts $msg
     return -code error "ERROR running cvpostsolver!"
   }
}

if [catch {exec $POSTSOLVER   -sn 0 $aflag -vismesh cylinder_mesh.vis} msg] {
  puts $msg
  return -code error "ERROR running cvpostsolver!"
}



if [catch {exec $POSTSOLVER  -sn $endstep -td -ph -sol $aflag -newsn 0} msg] {
  puts $msg
  return -code error "ERROR running cvpostsolver!"
}



file copy [file join $rigid_steady_sim_dir restart.0.0]    [file join $def_steady_dir restart.0.1]

cd $fullrundir 



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
puts $fp "fix_free_edge_nodes [file join $fullrundir mesh-surfaces wall.ebc.gz]"
puts $fp "pressure [file join $fullrundir mesh-surfaces outlet.ebc.gz] 116490.0"
puts $fp "set_surface_id [file join $fullrundir all.ebc.gz] 1"
puts $fp "set_surface_id [file join $fullrundir mesh-surfaces outlet.ebc.gz] 2"
puts $fp "deformable_create_mesh [file join $fullrundir mesh-surfaces wall.ebc.gz]"
puts $fp "deformable_E 4144000.0"
puts $fp "deformable_nu 0.5"
puts $fp "deformable_thickness 0.1"
puts $fp "deformable_pressure 120000.0"
puts $fp "deformable_kcons 0.833333"
puts $fp "deformable_solve_displacements"
puts $fp "write_geombc [file join $def_steady_dir geombc.dat.1]"
puts $fp "append_displacements [file join $def_steady_dir restart.0.1]"
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
  if {$selected_LS} {
       regsub -all "\#leslib_linear_solver" $line {} line
  } else {
       regsub -all "\#memls_linear_solver" $line {} line
  }
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


cd $def_steady_sim_dir
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
   if [catch {exec $POSTSOLVER  -sn $i $aflag  -vis cylinder} msg] {
     puts $msg
     return -code error "ERROR running cvpostsolver!"
   }
}
if [catch {exec $POSTSOLVER  -sn 0 $aflag -vismesh  cylinder_mesh.vis} msg] {
  puts $msg
  return -code error "ERROR running cvpostsolver!"
}


if [catch {exec $POSTSOLVER  -sn $timesteps -disp -td -ph -sol $aflag -newsn 0} msg] {
  puts $msg
  return -code error "ERROR running cvpostsolver!"
}



cd $fullrundir

if {$run_varwall == 1 } {


###
###
###    
###   VARIABLE WALL CASE
###
###
###

file copy [file join $rigid_steady_sim_dir restart.0.0] [file join $def_varwall_dir restart.0.1]


puts "Create script file for presolver."
set fp [open [file join $fullrundir variablewall_cylinder.cvpre] w]
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
puts $fp "fix_free_edge_nodes [file join $fullrundir mesh-surfaces wall.ebc.gz]"
puts $fp "pressure [file join $fullrundir mesh-surfaces outlet.ebc.gz] 116490.0"
puts $fp "set_surface_id [file join $fullrundir all.ebc.gz] 1"
puts $fp "set_surface_id [file join $fullrundir mesh-surfaces outlet.ebc.gz] 2"
puts $fp "set_surface_thickness [file join $fullrundir mesh-surfaces inflow.nbc.gz] 0.15"
puts $fp "set_surface_thickness [file join $fullrundir mesh-surfaces outlet.nbc.gz] 0.05"
puts $fp "solve_varwall_thickness"
puts $fp "set_surface_Evw [file join $fullrundir mesh-surfaces inflow.nbc.gz] 5180000"
puts $fp "set_surface_Evw [file join $fullrundir mesh-surfaces outlet.nbc.gz] 3108000"
puts $fp "solve_varwall_E"
puts $fp "varwallprop_write_vtk varwall_cylinder.vtk"
puts $fp "deformable_create_mesh [file join $fullrundir mesh-surfaces wall.ebc.gz]"
puts $fp "deformable_E 4144000.0"
puts $fp "deformable_nu 0.5"
puts $fp "deformable_thickness 0.1"
puts $fp "deformable_pressure 120000.0"
puts $fp "deformable_kcons 0.833333"
puts $fp "deformable_solve_displacements"
puts $fp "write_geombc [file join $def_varwall_dir geombc.dat.1]"
puts $fp "append_displacements [file join $def_varwall_dir restart.0.1]"
puts $fp "append_varwallprop [file join $def_varwall_dir restart.0.1]"
close $fp



#
#  Call pre-processor
#
puts "Run cvpresolver."
catch {exec $PRESOLVER [file join $fullrundir variablewall_cylinder.cvpre]} msg
puts $msg

#
# set number of timesteps
#

set timesteps 200
puts "Number of timesteps ($timesteps)"

#
#  Run solver.
#

puts "Run Solver."

#
#  more files needed by solver
#

set fp [open [file join $def_varwall_dir numstart.dat] w]
fconfigure $fp -translation lf
puts $fp "0"
close $fp

set infp [open solver.inp.deformable r]

set outfp [open [file join $def_varwall_dir solver.inp] w]
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
  regsub -all my_variablewall_flag $line True line
  regsub -all my_rho_infinity $line 0.0 line
  regsub -all my_step_construction $line "0 1 0 1 0 1 0 1 0 1  \# this is the standard five iteration" line
  if {$selected_LS} {
       regsub -all "\#leslib_linear_solver" $line {} line
  } else {
       regsub -all "\#memls_linear_solver" $line {} line
  }
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

set fp [open [file join $def_varwall_dir solver.log] w]
puts $fp "Start running solver..."
close $fp

set ::tail_solverlog {}
tail [file join $def_varwall_dir solver.log] .+ 1000 ::tail_solverlog
trace variable ::tail_solverlog w handle

eval exec \"$MPIEXEC\" -wdir \"$def_varwall_dir\" $npflag $num_procs -env FLOWSOLVER_CONFIG \"$FLOWSOLVER_CONFIG\" \"$SOLVER\" >>& [file join $def_varwall_dir solver.log] &
#exec        $MPIEXEC   -wdir   $def_steady_dir   $npflag $num_procs -env FLOWSOLVER_CONFIG   $FLOWSOLVER_CONFIG     $SOLVER solver.inp >>& [file join $def_steady_dir solver.log] &

set endstep 0
while {$endstep < $timesteps} {
  set waittwoseconds 0
  after 2000 set waittwoseconds 1
  vwait waittwoseconds
  set fp [open [file join $def_varwall_sim_dir "numstart.dat"] r]
  gets $fp endstep
  close $fp
  set endstep [string trim $endstep]
}

cancelTail [file join $def_varwall_dir solver.log]

cd $def_varwall_sim_dir
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
   if [catch {exec $POSTSOLVER -sn $i $aflag -vis cylinder} msg] {
     puts $msg
     return -code error "ERROR running cvpostsolver!"
   }
}
if [catch {exec $POSTSOLVER  -sn 0 $aflag -vismesh  cylinder_mesh.vis} msg] {
  puts $msg
  return -code error "ERROR running cvpostsolver!"
}


if [catch {exec $POSTSOLVER  -sn $timesteps -disp -td -ph -sol $aflag -newsn 0} msg] {
  puts $msg
  return -code error "ERROR running cvpostsolver!"
}






 }


cd $fullrundir

###
###
###    
###   DEFORMABLE PULSATILE CASE
###
###
###

file copy [file join $def_steady_sim_dir restart.0.0] [file join $def_pulse_dir restart.0.1]
file copy [file join $def_steady_dir geombc.dat.1] [file join $def_pulse_dir geombc.dat.1]

#
# set number of timesteps
#

set timesteps 250

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
  if {$selected_LS} {
       regsub -all "\#leslib_linear_solver" $line {} line
  } else {
       regsub -all "\#memls_linear_solver" $line {} line
  }
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

cd $def_pulse_sim_dir
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
   if [catch {exec $POSTSOLVER  -sn $i $aflag  -vis cylinder} msg] {
     puts $msg
     return -code error "ERROR running cvpostsolver!"
   }
}
if [catch {exec $POSTSOLVER   -sn 0 $aflag -vismesh  cylinder_mesh.vis} msg] {
  puts $msg
  return -code error "ERROR running cvpostsolver!"
}




