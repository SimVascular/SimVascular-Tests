#
#   Copyright (c) 2009-2012 Open Source Medical Software Corporation
#   All rights reserved.  
#
#  This script requires the following files:
#     solver.inp
#  and should be sourced interactively from SimVascular
#

set use_ascii_format 0

source ../../common/executable_names.tcl

#
# prompt user for number of procs
#
#
# sometimes we have to invert the normal to the inflow surface
global guiABC

#set num_procs [tk_dialog .askthem "Select Number of Processors" "Number of Processors \n to use?" question 0 1 2 3 4]
#incr num_procs
set num_procs 1

# having lots of problems with the line intersection with
# the edge boundary to calcuate the ratio map, so hack it here
source geom_createRatioMap.tcl

# let's use tetgen and polydata solids!
global gOptions 
set gOptions(meshing_kernel) TetGen
mesh_setKernel -name TetGen
set gOptions(meshing_solid_kernel) PolyData
solid_setKernel -name PolyData

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
source adaptor_create_model_and_mesh.tcl
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
puts $fp "mesh_and_adjncy_vtu [file join $fullrundir mesh-complete cylinder.mesh.vtu]"
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
puts $fp "mesh_and_adjncy_vtu [file join $adaptdir mesh-complete cylinder.mesh.vtu]"
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

file copy [file join $fullrundir bct.vtp.inflow] [file join $fullrundir bct.vtp]

set fp [open [file join $fullrundir numstart.dat] w]
fconfigure $fp -translation lf
puts $fp "0"
close $fp

set infp [open ../generic/solver.inp r]

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
puts "Running Post Solver for first run"
set adapt_step [expr int($timesteps)]
set adapt_start $adapt_step
if [catch {exec $POSTSOLVER -start 0 -stop $total_timesteps -incr 1 -indir $fullsimdir -outdir $fullsimdir -vtkcombo -vtu cylinder_results.vtu -vtp cylinder_results.vtp} msg] {
  puts $msg
  return -code error "ERROR running postsolver!"
}
puts $msg

puts "Reduce restart files."
if {$use_ascii_format != 0} {
  set aflag "-nonbinary"
} else {
  set aflag ""
}

#
#  Run the adaptor
#
#  Parameter Setup
global gObjects
global gFilenames

set adaptobject /new/adapt/object
catch {repos_delete -obj $adaptobject}

set out_mesh_dir [file join $fullsimdir adaptor/mesh-complete/]
file mkdir $out_mesh_dir
set mesh_file [file join $fullsimdir cylinder_results.vtu]
set solid_file [file join $fullsimdir cylinder.vtp]
set discreteFlag 0
set adaptorsphere {-1 0 0 0 0}
set maxRefineFactor 0.01
set maxCoarseFactor 0.75
set reductionRatio 0.1
set solution [file join $fullsimdir "ybar.$adapt_step.0"]
set error_file [file join $fullsimdir "ybar.$adapt_step.0"]
set out_solution [file join $fullsimdir "adaptor/restart.$adapt_step.1"]
set stepNumber $adapt_step

set gOptions(meshing_kernel) TetGen
set gOptions(meshing_solid_kernel) PolyData
set gFilenames($solid_file) $solid_file

puts "Running the adaptor..."

adapt_newObject -result $adaptobject
$adaptobject CreateInternalMeshObject
$adaptobject LoadModel -file $solid_file
$adaptobject LoadMesh -file $mesh_file
$adaptobject SetAdaptOptions -flag strategy -value 1
puts "Set strategy"
$adaptobject SetAdaptOptions -flag metric_option -value 2
puts "Set option"
$adaptobject SetAdaptOptions -flag ratio -value $reductionRatio
puts "Set ratio"
$adaptobject SetAdaptOptions -flag hmin -value $maxRefineFactor
puts "Set hmin"
$adaptobject SetAdaptOptions -flag hmax -value $maxCoarseFactor
puts "Set hmax"
$adaptobject SetAdaptOptions -flag instep -value 0
puts "Set instep"
$adaptobject SetAdaptOptions -flag outstep -value $adapt_step
puts "Set outstep"
$adaptobject SetMetric -input $mesh_file
puts "Set metric"
$adaptobject SetupMesh
puts "Set up mesh"
$adaptobject RunAdaptor
$adaptobject GetAdaptedMesh
$adaptobject TransferSolution       
$adaptobject TransferRegions
$adaptobject WriteAdaptedSolution -file $out_solution
set mesh /adapt/internal/meshobject
mesh_writeCompleteMesh $mesh cyl cylinder $out_mesh_dir

#set guiABC(invert_face_normal) 1
demo_create_bc_files $adaptdir
file copy [file join $adaptdir bct.vtp.inflow] [file join $adaptdir bct.vtp]
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

if [catch {exec $POSTSOLVER -indir $adaptdir -outdir $adaptdir -start $adapt_start -stop $adapt_step -incr 1 -sim_units_mm -vtkcombo -vtu cylinder_results.vtu -vtp cylinder_results.vtp} msg] {
   puts $msg
   return -code error "ERROR running postsolver!"
}


#
#  compare the two solutions
#

source ../generic/adaptor_compare_with_analytic.tcl

