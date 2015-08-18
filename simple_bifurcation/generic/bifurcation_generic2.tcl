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

#
# prompt user for mesh type
#

if {$bifurcation_mesh_option == ""} {
  set bifurcation_mesh_option [tk_dialog .askthem "Select the Mesh to Use" "Select the desired mesh" question 0 "  Coarse Isotropic Mesh  " "  Refined Mesh  "  "  Dense Mesh  "]
  incr bifurcation_mesh_option
}

#
# prompt user about BC
#

if {$use_resistance == ""} {
  set use_resistance [tk_dialog .askthem "Select Outlet B.C." "Select Outlet B.C." question 0 "  Zero Pressure  " "   Resistance   "]
}

#
# prompt user for the number of timesteps
#

if {$timesteps == ""} {
  set timesteps [tk_dialog .askthem "Select the Number of Time Steps" "Select the Number of Time Steps" question 0 "  5  " "  15  " "  25  " "  50  " "  100  " "  200  " " 400  " "  800  "]
  set timesteps [lindex [list 5 15 25 50 100 200 400 800] $timesteps]
}

puts "Number of timesteps: $timesteps"

#
# prompt user for the number of periods
#

if {$num_periods == ""} {
  set num_periods [tk_dialog .askthem "Select the Number of Cycles" "Select the Number of Cycles" question 0 "  2  " "  3  " "  4  " "  5  " "  6  "]
  set num_periods [lindex [list 2 3 4 5 6] $num_periods]
}

puts "Number of periods: $num_periods"

set rundir [clock format [clock seconds] -format "%m-%d-%Y-%H%M%S"]
set fullrundir [file join [pwd] $rundir]
file mkdir $fullrundir

if {$num_procs == 1} {
  set fullsimdir $fullrundir
} else {
  set fullsimdir [file join $fullrundir $num_procs-procs_case]
}

# copy files into rundir
file copy ../generic/bifurcation-flow-files [file join $fullrundir flow-files]

# create model, mesh, and bc files
set solidfn [bifurcation_create_model_$gOptions(meshing_solid_kernel) $fullrundir]
bifurcation_create_mesh_$gOptions(meshing_kernel) $solidfn $bifurcation_mesh_option $fullrundir

#
#  Create script file for cvpresolver
#

puts "Create script file for presolver."
set fp [open [file join $fullrundir bifurcation.svpre] w]
puts $fp "mesh_and_adjncy_vtu [file join $fullrundir mesh-complete bifurcation.mesh.vtu]"
puts $fp "prescribed_velocities_vtp [file join $fullrundir mesh-complete mesh-surfaces inflow.vtp]"
puts $fp "noslip_vtp [file join $fullrundir mesh-complete walls_combined.vtp]"
puts $fp "zero_pressure_vtp [file join $fullrundir mesh-complete mesh-surfaces lt_iliac.vtp]"
puts $fp "set_surface_id_vtp [file join $fullrundir mesh-complete bifurcation.exterior.vtp] 1"
if {$use_resistance >= 1} {
  puts $fp "set_surface_id_vtp [file join $fullrundir mesh-complete mesh-surfaces lt_iliac.vtp] 2"
}
puts $fp "zero_pressure_vtp [file join $fullrundir mesh-complete mesh-surfaces rt_iliac.vtp]"
if {$use_resistance >= 1} {
    puts $fp "set_surface_id_vtp [file join $fullrundir mesh-complete mesh-surfaces rt_iliac.vtp] 3"
}

puts $fp "fluid_density 0.00106"
puts $fp "fluid_viscosity 0.004"
puts $fp "bct_period 1.1"
puts $fp "bct_analytical_shape womersley"
puts $fp "bct_point_number 201"
puts $fp "bct_fourier_mode_number 10"
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
catch {exec $PRESOLVER [file join $fullrundir bifurcation.svpre]} msg
puts $msg

#
#  Run solver.
#

puts "Run Solver."

set infp [open ../generic/solver.inp r]

set outfp [open $fullrundir/solver.inp w]
fconfigure $outfp -translation lf

while {[gets $infp line] >= 0} {
  regsub -all my_initial_time_increment $line [expr 1.1/$timesteps] line
  regsub -all my_number_of_time_steps $line [expr $num_periods*$timesteps] line
  regsub -all "\#resistance_sim" $line {} line
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

set fp [open [file join $fullrundir solver.log] w]
fconfigure $fp -translation lf
puts $fp "Start running solver..."
close $fp

eval exec \"$MPIEXEC\" -wdir \"$fullrundir\" $npflag $num_procs -env FLOWSOLVER_CONFIG \"$FLOWSOLVER_CONFIG\" \"$SOLVER\" >>& [file join $rundir solver.log] &

set waittwoseconds 0
after 10000 set waittwoseconds 1
vwait waittwoseconds
set ::tail_solverlog {}
tail [file join $fullrundir solver.log] .+ 1000 ::tail_solverlog
trace variable ::tail_solverlog w handle

set endstep 0
while {$endstep < [expr $num_periods*$timesteps]} {
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
#  Create results files
#
puts "Reduce restart files."

set beginstep [expr $endstep - $timesteps + 1]

puts "exec $POSTSOLVER -indir $fullsimdir -outdir $fullsimdir -start $beginstep -stop $endstep -incr 1 -sim_units_mm -vtkcombo -vtu bifurcation_results.vtu -vtp bifurcation_results.vtp"

if [catch {exec $POSTSOLVER -indir $fullsimdir -outdir $fullrundir -start $beginstep -stop $endstep -incr 1 -sim_units_mm -vtkcombo -vtu bifurcation_results.vtu -vtp bifurcation_results.vtp} msg] {
   puts $msg
   return -code error "ERROR running postsolver!"
}

# output all the results into text files

set vtxFileName [file join $fullrundir bifurcation_results.vtp]
set mesh_surface_vtk_filenames [list \
  [file join $fullrundir mesh-complete mesh-surfaces lt_iliac.vtp] \
  [file join $fullrundir mesh-complete mesh-surfaces rt_iliac.vtp] \
  [file join $fullrundir mesh-complete mesh-surfaces inflow.vtp] \
			       ]
set skipWalls 0
set sim_units mm
set outFlowFileName           [file join $fullrundir bifurcation-results-flows.txt]
set outPressureFileName       [file join $fullrundir bifurcation-results-pressures.txt]
set outAveragesFileName       [file join $fullrundir bifurcation-results-averages.txt]
set outAveragesUnitsFileName  [file join $fullrundir bifurcation-results-averages-in-mm.txt]

vtx_TemporalFlowThruFaces $vtxFileName \
                          $mesh_surface_vtk_filenames \
                          $skipWalls \
                          $sim_units \
                          $outFlowFileName \
                          $outPressureFileName \
                          $outAveragesFileName \
                          $outAveragesUnitsFileName


set resfn [file join $fullrundir bifurcation_results.vtu]

puts "Reading simulation results ($resfn)."
set resReader tmp-results-reader
catch {$resReader Delete}
vtkXMLUnstructuredGridReader $resReader
$resReader SetFileName $resfn
$resReader Update

catch {repos_delete -obj lt_iliac}
catch {repos_delete -obj rt_iliac}
catch {repos_delete -obj inflow}
repos_readXMLPolyData [file join $fullrundir mesh-complete mesh-surfaces lt_iliac.vtp] lt_iliac
repos_readXMLPolyData [file join $fullrundir mesh-complete mesh-surfaces rt_iliac.vtp] rt_iliac
repos_readXMLPolyData [file join $fullrundir mesh-complete mesh-surfaces inflow.vtp] inflow


