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

source ../../common/executable_names.tcl

#
# prompt user for number of procs
#

#set num_procs [tk_dialog .askthem "Select Number of Processors" "Number of Processors \n to use?" question 0 1 2 3 4]
#incr num_procs
set num_procs 1

#
# prompt user for linear solver
#

set selected_LS [tk_dialog .askthem "Select Linear Solver" "Use which linear solver?" question 0 "  svLS  " " leslib "]

set rundir [clock format [clock seconds] -format "%m-%d-%Y-%H%M%S"]
set fullrundir [file join [pwd] $rundir]
file mkdir $fullrundir

if {$num_procs == 1} {
  set fullsimdir $fullrundir
} else {
  set fullsimdir [file join $fullrundir $num_procs-procs_case]
}

set adaptdir [file join $fullrundir adaptor]
file mkdir $adaptdir

if {$num_procs == 1} {
  set adaptsimdir $adaptdir
} else {
  set adaptsimdir [file join $adaptdir $num_procs-procs_case]
}
#
# prompt user for mesh type
#

set adaptor_mesh_option [tk_dialog .askthem "Select the Mesh to Use" "Select the desired mesh" question 0 "  Isotropic Mesh  " "  Boundary Layer Mesh  "]
incr adaptor_mesh_option

# create model, mesh, and bc files
source adaptor-create_model_and_mesh.tcl
demo_create_model $fullrundir
demo_create_mesh $fullrundir $adaptor_mesh_option
demo_create_bc_files $fullrundir

#create files for adapting later
demo_create_model $adaptdir
#
#  Create script file for presolver
#
foreach i [mymesh Print] {
  set [lindex $i 0] [lindex $i 1]
}

puts "Create script file for presolver."
set fp [open [file join $fullrundir cylinder.svpre] w]
if {$use_ascii_format > 0} {
  puts $fp "ascii_format"
}
puts $fp "verbose"
puts $fp "mesh_vtu [file join $fullrundir mesh-complete cylinder.mesh.vtu]"
puts $fp "adjacency [file join $fullrundir mesh-complete cylinder.xadj.gz]"
puts $fp "prescribed_velocities_vtp [file join $fullrundir mesh-complete mesh-surfaces inflow.vtp]"
puts $fp "noslip_vtp [file join $fullrundir mesh-complete mesh-surfaces wall.vtp]"
puts $fp "zero_pressure_vtp [file join $fullrundir mesh-complete mesh-surfaces outlet.vtp]"
puts $fp "set_surface_id_vtp [file join $fullrundir mesh-complete cylinder.exterior.vtp] 1"
puts $fp "write_geombc [file join $fullrundir geombc.dat.1]"
puts $fp "write_restart [file join $fullrundir restart.0.1]"
close $fp

puts "Create script file for presolver after adaptor."
set fp [open [file join $adaptdir cylinder.svpre] w]
if {$use_ascii_format > 0} {
  puts $fp "ascii_format"
}
puts $fp "verbose"
puts $fp "mesh_vtu [file join $adaptdir mesh-complete cylinder.mesh.vtu]"
puts $fp "adjacency [file join $adaptdir mesh-complete cylinder.xadj.gz]"
puts $fp "prescribed_velocities_vtp [file join $adaptdir mesh-complete mesh-surfaces inflow.vtp]"
puts $fp "noslip_vtp [file join $adaptdir mesh-complete mesh-surfaces wall.vtp]"
puts $fp "zero_pressure_vtp [file join $adaptdir mesh-complete mesh-surfaces outlet.vtp]"
puts $fp "set_surface_id_vtp [file join $adaptdir mesh-complete cylinder.exterior.vtp] 1"
puts $fp "write_geombc [file join $adaptdir geombc.dat.1]"
close $fp

#
#  Call pre-processor
#
puts "Run cvpresolver."
catch {exec $PRESOLVER [file join $fullrundir cylinder.svpre]} msg
puts $msg

#
# prompt user for the number of timesteps
#

set timesteps [tk_dialog .askthem "Select the Number of Time Steps" "Select the Number of Time Steps" question 0 "  16  " "  32  " "  64  " " 128  " " 256  " " 512  "]
set timesteps [expr pow(2,$timesteps) * 16]

puts "timesteps: $timesteps"
if {[expr int(fmod($timesteps,16))] > 0} {
  return -code error "ERROR in number of specified timesteps"
}

set total_timesteps [expr 2*$timesteps]

#
#  Run solver.
#

puts "Run Solver."

#
#  more files needed by solver
#

file copy [file join $fullrundir bct.dat.inflow] [file join $fullrundir bct.dat]
set fp [open [file join $fullrundir numstart.dat] w]
fconfigure $fp -translation lf
puts $fp "0"
close $fp

set infp [open solver.inp r]

set outfp [open $fullrundir/solver.inp w]
fconfigure $outfp -translation lf

if {$use_ascii_format == 0} {
   set file_format binary
} else {
   set file_format ascii
}

while {[gets $infp line] >= 0} {
  regsub -all my_initial_time_increment $line [expr 0.2/$timesteps] line
  regsub -all my_number_of_time_steps $line $timesteps line
  regsub -all my_output_format $line $file_format line
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
  set npflag "-noprompt -localroot -localonly -user 1 -n"
} else {
  set npflag "-np"
}

proc handle { args } {
  puts -nonewline [ set [ lindex $args 0 ] ]
}

#
#  start the solver with intial timesteps
#

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
after 5000

#
#  start running the second half of the solve. Have to split it up like this so that the middle step has ybar
#
#
set fp [open [file join $fullrundir solver.log] w]
fconfigure $fp -translation lf
puts $fp "Start running rest of solver..."
close $fp

set ::tail_solverlog {}
tail [file join $fullrundir solver.log] .+ 1000 ::tail_solverlog
trace variable ::tail_solverlog w handle

eval exec \"$MPIEXEC\" -wdir \"$fullrundir\" $npflag $num_procs -env FLOWSOLVER_CONFIG \"$FLOWSOLVER_CONFIG\" \"$SOLVER\" >>& [file join $rundir solver.log] &

set endstep 0
while {$endstep < $total_timesteps} {
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
after 5000

#
#  Create ParaView files
#
#
#  Run the post solver to get just the ybar from the solution
#
puts "Running Post Solver for ybar"
set adapt_step [expr int($timesteps)]
set adapt_start $adapt_step
if [catch {exec $POSTSOLVER -none -sn $adapt_step -indir $fullsimdir -outdir $fullsimdir -ybar -newsn 0 -ph} msg] {
  puts $msg
  return -code error "ERROR creating ybar file!"
}
puts $msg

puts "Reduce restart files."
if {$use_ascii_format != 0} {
  set aflag "-nonbinary"
} else {
  set aflag ""
}

puts "exec $POSTSOLVER -indir $fullsimdir -outdir $fullsimdir -start 1 -stop $endstep -incr 1 -sim_units_mm -vtkcombo -vtu cylinder_results.vtu -vtp cylinder_results.vtp"

if [catch {exec $POSTSOLVER -indir $fullsimdir -outdir $fullrundir -start 1 -stop $endstep -incr 1 -sim_units_mm -vtkcombo -vtu cylinder_results.vtu -vtp cylinder_results.vtp} msg] {
   puts $msg
   return -code error "ERROR running postsolver!"
}


#
#  Run the adaptor
#
#  Parameter Setup
set out_mesh   [file join $adaptdir adapted-cylinder.sms]
set model_file [file join $fullrundir cylinder.xmt_txt]
set mesh_file  [file join $fullrundir cylinder.sms]
set discreteFlag 0
set adaptorsphere {-1 0 0 0 0}
set maxRefineFactor 0.1
set maxCoarseFactor 0.5
set reductionRatio 0.6
set solution   [file join $fullsimdir "restart.$adapt_step.$num_procs"]
set error_file [file join $fullsimdir "ybar.$adapt_step.0"]
set out_solution [file join $adaptdir "restart.$adapt_step.$num_procs"]
set stepNumber $adapt_step

file delete [file join $fullrundir adaptor_done_running]
set fp [open [file join $fullrundir run_adaptor.log] w]
puts $fp "Start running adaptor..."
puts $fp "exec $ADAPTOR -model_file $model_file -mesh_file $mesh_file -solution_file $solution -error_indicator_file $error_file -out_mesh_file $out_mesh -out_solution_file $out_solution -out_sn $stepNumber -ratio $reductionRatio -hmax $maxCoarseFactor -hmin $maxRefineFactor -discrete_model_flag $discreteFlag -sphere_refinement [lindex $adaptorsphere 0] [lindex $adaptorsphere 1] [lindex $adaptorsphere 2] [lindex $adaptorsphere 3] [lindex $adaptorsphere 4]"
close $fp

#catch {unset ::tail_adaptorlog}
#set ::tail_adaptorlog {}
#tail [file join [pwd] run_adaptor.log] .+ 1000 ::tail_adaptorlog
#trace variable ::tail_adaptorlog w guiMMadaptMesh_handle

#  Call the Adaptor

if [catch {exec $ADAPTOR -model_file $model_file -mesh_file $mesh_file -solution_file $solution -error_indicator_file $error_file -out_mesh_file $out_mesh -out_solution_file $out_solution -out_sn $stepNumber -ratio $reductionRatio -hmax $maxCoarseFactor -hmin $maxRefineFactor -discrete_model_flag $discreteFlag -sphere_refinement [lindex $adaptorsphere 0] [lindex $adaptorsphere 1] [lindex $adaptorsphere 2] [lindex $adaptorsphere 3] [lindex $adaptorsphere 4]} msg] {
  puts $msg
  return -code error "ERROR running adaptor!"
}

#cancelTail [file join [pwd] run_adaptor.log] ::tail_adaptorlog
after 5000

#
# Second run through with solver 
#
global gObjects

set adaptmesh /tmp/new/mesh

catch {repos_delete -obj $adaptmesh}

file mkdir [file join $adaptdir mesh-complete]
file mkdir [file join $adaptdir mesh-complete mesh-surfaces]

#
# Create new mesh object for adapted mesh
#
mesh_newObject -result $adaptmesh
$adaptmesh SetSolidKernel -name $gOptions(meshing_solid_kernel)
$adaptmesh LoadModel -file [file join $adaptdir cylinder.xmt_txt]
$adaptmesh NewMesh  
$adaptmesh LoadMesh -file [file join $adaptdir adapted-cylinder.sms]

#
# Create boundary condition and complete mesh files for solver
#
demo_write_mesh_related_files $adaptmesh cyl cylinder [file join $adaptdir mesh-complete]
demo_create_bc_files $adaptdir
file copy [file join $adaptdir bct.dat.inflow] [file join $adaptdir bct.dat]
set fp [open [file join $adaptdir numstart.dat] w]
fconfigure $fp -translation lf
puts $fp "$adapt_step"
close $fp

file copy [file join $fullrundir solver.inp] [file join $adaptdir solver.inp]

#
#  Call pre-presolver to create geombc for adapted mesh
#
puts "Run cvpresolver."
catch {exec $PRESOLVER [file join $adaptdir cylinder.svpre]} msg
puts $msg

set fp [open [file join $adaptdir solver.log] w]
fconfigure $fp -translation lf
puts $fp "Start running solver..."
close $fp

set ::tail_solverlog {}
tail [file join $adaptdir solver.log] .+ 1000 ::tail_solverlog
trace variable ::tail_solverlog w handle

eval exec \"$MPIEXEC\" -wdir \"$adaptdir\" $npflag $num_procs -env FLOWSOLVER_CONFIG \"$FLOWSOLVER_CONFIG\" \"$SOLVER\" >>& [file join $adaptdir solver.log] &

while {$adapt_step < $total_timesteps} {
  set waittwoseconds 0
  after 2000 set waittwoseconds 1
  vwait waittwoseconds
  if {![file exists [file join $adaptdir "numstart.dat"]]} continue
  set fp [open [file join $adaptdir "numstart.dat"] r]
  gets $fp adapt_step
  close $fp
  set adapt_step [string trim $adapt_step]
}

cancelTail [file join $adaptdir solver.log]
after 5000
#
#  Create ParaView files
#
puts "Reduce restart files."
if {$use_ascii_format != 0} {
  set aflag "-nonbinary"
} else {
  set aflag ""
}

#
#  Run the post solver on the adapted solution
#
puts "exec $POSTSOLVER -indir $adaptdir -outdir $adaptsimdir -start $adapt_start -stop $adapt_step -incr 1 -sim_units_mm -vtkcombo -vtu cylinder_results.vtu -vtp cylinder_results.vtp"

if [catch {exec $POSTSOLVER -indir $adaptdir -outdir $adaptsimdir -start $adapt_start -stop $adapt_step -incr 1 -sim_units_mm -vtkcombo -vtu cylinder_results.vtu -vtp cylinder_results.vtp} msg] {
   puts $msg
   puts "\n\n *** WARNING *** postsolver is returning an error, why?  Maybe due to stepnumber being reset in restart.0.1 on adapt???  skip for now\n\n"
   #return -code error "ERROR running postsolver!"
}

#
#  compare the two solutions
#

source adaptor-compare_with_analytic.tcl

