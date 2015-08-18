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

#
# prompt user for number of procs
#
if {$num_procs == ""} {
  set num_procs [tk_dialog .askthem "Select Number of Processors" "Number of Processors \n to use?" question 0 1 2 3 4]
  incr num_procs
}
# prompt user for linear solver
#
if {$selected_LS == ""} {
  set selected_LS [tk_dialog .askthem "Select Linear Solver" "Use which linear solver?" question 0 "  svLS  " " leslib "]
}

if {$run_varwall == ""} {
  set run_varwall [tk_dialog .askthem "Variable Wall Selection" "Add a variable wall demo?" question 0 " No  " " Yes "]
}

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
file copy ../generic/deformable-flow-files [file join $fullrundir flow-files]
# create model, mesh, and bc files
cylinder_create_model_$gOptions(meshing_solid_kernel) $fullrundir
cylinder_create_mesh_$gOptions(meshing_kernel)  $fullrundir

#
#  Create script file for steady bct
#
puts "Create script for steady bct."
set fp [open [file join $fullrundir steady_bct.svpre] w]
puts $fp "mesh_and_adjncy_vtu [file join $fullrundir mesh-complete cylinder.mesh.vtu]"
puts $fp "fluid_density 0.00106"
puts $fp "fluid_viscosity 0.004"
puts $fp "bct_period 1.1"
puts $fp "bct_analytical_shape parabolic"
puts $fp "bct_point_number 2"
puts $fp "bct_fourier_mode_number 1"
puts $fp "bct_create [file join $fullrundir mesh-complete mesh-surfaces inflow.vtp] [file join $fullrundir flow-files inflow.flow.steady]"
puts $fp "bct_write_dat [file join $fullrundir bct_steady.dat]"
puts $fp "bct_write_vtp [file join $fullrundir bct_steady.vtp]"
close $fp
puts "Run cvpresolver for steady bct."
catch {exec $PRESOLVER [file join $fullrundir steady_bct.svpre]} msg
puts $msg
#
#  Create script file for pulsatile bct
#
puts "Create script for pulsatile bct."
set fp [open [file join $fullrundir pulsatile_bct.svpre] w]
puts $fp "mesh_and_adjncy_vtu [file join $fullrundir mesh-complete cylinder.mesh.vtu]"
puts $fp "fluid_density 0.00106"
puts $fp "fluid_viscosity 0.004"
puts $fp "bct_period 1.1"
puts $fp "bct_analytical_shape parabolic"
puts $fp "bct_point_number 276"
puts $fp "bct_fourier_mode_number 10"
puts $fp "bct_create [file join $fullrundir mesh-complete mesh-surfaces inflow.vtp] [file join $fullrundir flow-files inflow.flow.pulsatile]"
puts $fp "bct_write_dat [file join $fullrundir bct_pulsatile.dat]"
puts $fp "bct_write_vtp [file join $fullrundir bct_pulsatile.vtp]"
close $fp
puts "Run cvpresolver for pulsatile bct."
catch {exec $PRESOLVER [file join $fullrundir pulsatile_bct.svpre]} msg
puts $msg

file copy [file join $fullrundir bct_steady.dat]    [file join $rigid_steady_dir bct.dat]
file copy [file join $fullrundir bct_steady.dat]    [file join $def_steady_dir bct.dat]
file copy [file join $fullrundir bct_pulsatile.dat] [file join $def_pulse_dir bct.dat]
file copy [file join $fullrundir bct_steady.dat]    [file join $def_varwall_dir bct.dat]

file copy [file join $fullrundir bct_steady.vtp]    [file join $rigid_steady_dir bct.vtp]
file copy [file join $fullrundir bct_steady.vtp]    [file join $def_steady_dir bct.vtp]
file copy [file join $fullrundir bct_pulsatile.vtp] [file join $def_pulse_dir bct.vtp]
file copy [file join $fullrundir bct_steady.vtp]    [file join $def_varwall_dir bct.vtp]

#
#  Create presolver script file for rigid wall steady
#
foreach i [mymesh Print] {
  set [lindex $i 0] [lindex $i 1]
}

puts "Create presolver script file for rigid wall steady."
set fp [open [file join $rigid_steady_dir rigid_steady_cylinder.cvpre] w]
puts $fp "mesh_and_adjncy_vtu [file join $fullrundir mesh-complete cylinder.mesh.vtu]"
puts $fp "prescribed_velocities_vtp [file join $fullrundir mesh-complete mesh-surfaces inflow.vtp]"
puts $fp "noslip_vtp [file join $fullrundir mesh-complete mesh-surfaces wall.vtp]"
puts $fp "pressure_vtp [file join $fullrundir mesh-complete mesh-surfaces outlet.vtp] 11649.0"
puts $fp "set_surface_id_vtp [file join $fullrundir mesh-complete cylinder.exterior.vtp] 1"
puts $fp "set_surface_id_vtp [file join $fullrundir mesh-complete mesh-surfaces outlet.vtp] 2"
puts $fp "initial_pressure 12000.0"
puts $fp "initial_velocity 0.0 0.0 0.1"
puts $fp "write_numstart 0 [file join $rigid_steady_dir numstart.dat]"
puts $fp "write_geombc [file join $rigid_steady_dir geombc.dat.1]"
puts $fp "write_restart [file join $rigid_steady_dir restart.0.1]"
close $fp

#
#  Call pre-processor
#
puts "Run cvpresolver."
catch {exec $PRESOLVER [file join $rigid_steady_dir rigid_steady_cylinder.cvpre]} msg
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

set infp [open ../generic/solver.inp.deformable r]

set outfp [open [file join $rigid_steady_dir solver.inp] w]
fconfigure $outfp -translation lf


while {[gets $infp line] >= 0} {
  regsub -all my_initial_time_increment $line 0.001 line
  regsub -all my_number_of_time_steps $line [expr $timesteps] line
  regsub -all my_deformable_flag $line False line
  regsub -all my_rho_infinity $line 0.5 line
  regsub -all my_step_construction $line "0 1 0 1 0 1    \# this is the standard three iteration" line
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


puts "Reduce last step restart files to a single file for other simulations"
if [catch {exec $POSTSOLVER -indir $rigid_steady_sim_dir -outdir $rigid_steady_dir  -sn $endstep -ph -td -sol -newsn 0} msg] {
  puts $msg
  return -code error "ERROR running cvpostsolver!"
}

puts "Reduce restart files to vtp vtu"
if [catch {exec $POSTSOLVER -indir $rigid_steady_sim_dir -outdir $rigid_steady_dir -start 0 -stop $timesteps -incr 25 -sim_units_mm -vtkcombo -vtu cylinder_results.vtu -vtp cylinder_results.vtp} msg] {
   puts $msg
   return -code error "ERROR running postsolver!"
}


file copy [file join $rigid_steady_dir restart.0.0]    [file join $def_steady_dir restart.0.1]


###
###
###    
###   DEFORMABLE STEADY CASE
###
###
###

puts "Create presolver script file for deformable wall steady."
set fp [open [file join $def_steady_dir deformable_steady_cylinder.cvpre] w]
puts $fp "mesh_and_adjncy_vtu [file join $fullrundir mesh-complete cylinder.mesh.vtu]"
puts $fp "prescribed_velocities_vtp [file join $fullrundir mesh-complete mesh-surfaces inflow.vtp]"
puts $fp "deformable_wall_vtp [file join $fullrundir mesh-complete mesh-surfaces wall.vtp]"
puts $fp "pressure_vtp [file join $fullrundir mesh-complete mesh-surfaces outlet.vtp] 11649.0"
puts $fp "set_surface_id_vtp [file join $fullrundir mesh-complete cylinder.exterior.vtp] 1"
puts $fp "set_surface_id_vtp [file join $fullrundir mesh-complete mesh-surfaces outlet.vtp] 2"
puts $fp "deformable_E 414400.0"
puts $fp "deformable_thickness 1.0"
puts $fp "deformable_nu 0.5"
puts $fp "deformable_pressure 12000.0"
puts $fp "deformable_kcons 0.833333"
puts $fp "deformable_solve_displacements"
puts $fp "wall_displacements_write_vtp [file join $def_steady_dir walldisp.vtp]"
puts $fp "write_numstart 0 [file join $def_steady_dir numstart.dat]"
puts $fp "write_geombc [file join $def_steady_dir geombc.dat.1]"
puts $fp "append_displacements [file join $def_steady_dir restart.0.1]"
close $fp
#
#  Call pre-processor
#
puts "Run cvpresolver."
catch {exec $PRESOLVER [file join $def_steady_dir deformable_steady_cylinder.cvpre]} msg
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

set infp [open ../generic/solver.inp.deformable r]

set outfp [open [file join $def_steady_dir solver.inp] w]
fconfigure $outfp -translation lf

while {[gets $infp line] >= 0} {
  regsub -all my_initial_time_increment $line 0.0004 line
  regsub -all my_number_of_time_steps $line [expr $timesteps] line
  regsub -all my_deformable_flag $line True line
  regsub -all my_rho_infinity $line 0.0 line
  regsub -all my_step_construction $line "0 1 0 1 0 1 0 1   \# this is the standard four iteration" line
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
  set npflag "-np"
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

puts "Reduce last step restart files to a single file for other simulations"
if [catch {exec $POSTSOLVER -indir $def_steady_sim_dir -outdir $def_steady_dir  -sn $endstep -ph -disp -td -sol -newsn 0} msg] {
  puts $msg
  return -code error "ERROR running cvpostsolver!"
}

puts "Reduce restart files to vtp vtu"
if [catch {exec $POSTSOLVER -indir $def_steady_sim_dir -outdir $def_steady_dir -start 0 -stop $timesteps -incr 25 -sim_units_mm -vtkcombo -vtu cylinder_results.vtu -vtp cylinder_results.vtp} msg] {
   puts $msg
   return -code error "ERROR running postsolver!"
}


if {$run_varwall == 1 } {


###
###
###    
###   VARIABLE STEADY CASE
###
###
###

file copy [file join $rigid_steady_dir restart.0.0] [file join $def_varwall_dir restart.0.1]


puts "Create presolver script file for variable wall steady."
set fp [open [file join $def_varwall_dir variable_steady_cylinder.cvpre] w]
puts $fp "mesh_and_adjncy_vtu [file join $fullrundir mesh-complete cylinder.mesh.vtu]"
puts $fp "prescribed_velocities_vtp [file join $fullrundir mesh-complete mesh-surfaces inflow.vtp]"
puts $fp "deformable_wall_vtp [file join $fullrundir mesh-complete mesh-surfaces wall.vtp]"
puts $fp "pressure_vtp [file join $fullrundir mesh-complete mesh-surfaces outlet.vtp] 11649.0"
puts $fp "set_surface_id_vtp [file join $fullrundir mesh-complete cylinder.exterior.vtp] 1"
puts $fp "set_surface_id_vtp [file join $fullrundir mesh-complete mesh-surfaces outlet.vtp] 2"
puts $fp "set_surface_thickness_vtp [file join $fullrundir mesh-complete mesh-surfaces inflow.vtp] 1.5"
puts $fp "set_surface_thickness_vtp [file join $fullrundir mesh-complete mesh-surfaces outlet.vtp] 0.5"
puts $fp "solve_varwall_thickness"
puts $fp "set_surface_E_vtp [file join $fullrundir mesh-complete mesh-surfaces inflow.vtp] 518000"
puts $fp "set_surface_E_vtp [file join $fullrundir mesh-complete mesh-surfaces outlet.vtp] 310800"
puts $fp "solve_varwall_E"
puts $fp "varwallprop_write_vtp [file join $def_varwall_dir varwallprop.vtp]"
#puts $fp "deformable_E 4144000.0"
#puts $fp "deformable_thickness 0.1"
puts $fp "deformable_nu 0.5"
puts $fp "deformable_pressure 12000.0"
puts $fp "deformable_kcons 0.833333"
puts $fp "deformable_solve_displacements"
puts $fp "wall_displacements_write_vtp [file join $def_varwall_dir walldisp.vtp]"
puts $fp "write_numstart 0 [file join $def_varwall_dir numstart.dat]"
puts $fp "write_geombc [file join $def_varwall_dir geombc.dat.1]"
puts $fp "append_displacements [file join $def_varwall_dir restart.0.1]"
puts $fp "append_varwallprop [file join $def_varwall_dir geombc.dat.1]"
close $fp

#
#  Call pre-processor
#
puts "Run cvpresolver."
catch {exec $PRESOLVER [file join $def_varwall_dir variable_steady_cylinder.cvpre]} msg
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

set infp [open ../generic/solver.inp.deformable r]

set outfp [open [file join $def_varwall_dir solver.inp] w]
fconfigure $outfp -translation lf

while {[gets $infp line] >= 0} {
  regsub -all my_initial_time_increment $line 0.0004 line
  regsub -all my_number_of_time_steps $line [expr $timesteps] line
  regsub -all my_deformable_flag $line True line
  regsub -all my_variablewall_flag $line True line
  regsub -all my_rho_infinity $line 0.0 line
  regsub -all my_step_construction $line "0 1 0 1 0 1 0 1 0 1  \# this is the standard five iteration" line
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
  set npflag "-np"
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

puts "Reduce restart files to vtp vtu"
if [catch {exec $POSTSOLVER -indir $def_varwall_sim_dir -outdir $def_varwall_dir -start 0 -stop $timesteps -incr 25 -sim_units_mm -vtkcombo -vtu cylinder_results.vtu -vtp cylinder_results.vtp} msg] {
   puts $msg
   return -code error "ERROR running postsolver!"
}


 }


#cd $fullrundir

###
###
###    
###   DEFORMABLE PULSATILE CASE
###
###
###

file copy [file join $def_steady_dir restart.0.0] [file join $def_pulse_dir restart.0.1]
file copy [file join $def_steady_dir geombc.dat.1] [file join $def_pulse_dir geombc.dat.1]

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

set infp [open ../generic/solver.inp.deformable r]

set outfp [open [file join $def_pulse_dir solver.inp] w]
fconfigure $outfp -translation lf


while {[gets $infp line] >= 0} {
  regsub -all my_initial_time_increment $line 0.0004 line
  regsub -all my_number_of_time_steps $line [expr $timesteps] line
  regsub -all my_deformable_flag $line True line
  regsub -all my_rho_infinity $line 0.0 line
  regsub -all my_step_construction $line "0 1 0 1 0 1 0 1   \# this is the standard four iteration" line
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
  set npflag "-np"
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

puts "Reduce restart files to vtp vtu"
if [catch {exec $POSTSOLVER -indir $def_pulse_sim_dir -outdir $def_pulse_dir -start 0 -stop $timesteps -incr 250 -sim_units_mm -vtkcombo -vtu cylinder_results.vtu -vtp cylinder_results.vtp} msg] {
   puts $msg
   return -code error "ERROR running postsolver!"
}





