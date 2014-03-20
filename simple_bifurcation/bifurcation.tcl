#
#   Copyright (c) 2009-2012 Open Source Medical Software Corporation
#   All rights reserved.  
#
#  This script requires the following files:
#     solver.inp
#  and should be sourced interactively from simvascular
#

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
# prompt user for mesh type
#

set bifurcation_mesh_option [tk_dialog .askthem "Select the Mesh to Use" "Select the desired mesh" question 0 "  Coarse Isotropic Mesh  " "  Refined Mesh  "  "  Dense Mesh  "]
incr bifurcation_mesh_option

set rundir [clock format [clock seconds] -format "%m-%d-%Y-%H%M%S"]
set fullrundir [file join [pwd] $rundir]
file mkdir $fullrundir

if {$num_procs == 1} {
  set fullsimdir $fullrundir
} else {
  set fullsimdir [file join $fullrundir $num_procs-procs_case]
}

# copy files into rundir
file copy bifurcation.xmt_txt [file join $fullrundir bifurcation.xmt_txt]
file copy bifurcation-flow-files [file join $fullrundir flow-files]

#
# prompt user about BC
#

set use_resistance [tk_dialog .askthem "Select Outlet B.C." "Select Outlet B.C." question 0 "  Zero Pressure  " "   Resistance   " "  Impedance  "]

if {$use_resistance == 2} {
  set use_init_flow_type [tk_dialog .askthem "Select Initial Flow Type" "Select Initial Flow Type" question 0 "  Steady Flow  " "  Pulsatile Flow  "]
} else {
  set use_init_flow_type -1
}

#
# prompt user for the number of timesteps
#

set timesteps [tk_dialog .askthem "Select the Number of Time Steps" "Select the Number of Time Steps" question 0 "  5  " "  15  " "  25  " "  50  " "  100  " "  200  " " 400  " "  800  "]
set timesteps [lindex [list 5 15 25 50 100 200 400 800] $timesteps]

puts "Number of timesteps: $timesteps"

#
# prompt user for the number of periods
#

if {$use_resistance != 2} {
  set num_periods [tk_dialog .askthem "Select the Number of Cycles" "Select the Number of Cycles" question 0 "  2  " "  3  " "  4  " "  5  " "  6  "]
  set num_periods [lindex [list 2 3 4 5 6] $num_periods]
} else {
  set num_periods [tk_dialog .askthem "Select the Number of Cycles (pass 1)" "Select the Number of Cycles (pass 1)" question 0 "  2  " "  3  " "  4  " "  5  " "  6  "]
  set num_periods [lindex [list 2 3 4 5 6] $num_periods]
  set num_periods2 [tk_dialog .askthem "Select the Number of Cycles (pass 2)" "Select the Number of Cycles (pass 2)" question 0 "  2  " "  3  " "  4  " "  5  " "  6  "]
  set num_periods2 [lindex [list 2 3 4 5 6] $num_periods2]
}

puts "Number of periods: $num_periods"

# create model, mesh, and bc files
source bifurcation-create_model_and_mesh.tcl
demo_create_model $fullrundir
demo_create_mesh $fullrundir $bifurcation_mesh_option
demo_create_bc_files $fullrundir 


#
#  Create script file for cvpresolver
#
foreach i [mymesh Print] {
  set [lindex $i 0] [lindex $i 1]
}

puts "Create script file for presolver."
set fp [open [file join $fullrundir bifurcation.svpre] w]
if {$use_ascii_format > 0} {
  puts $fp "ascii_format"
}
puts $fp "verbose"
puts $fp "mesh_vtu [file join $fullrundir mesh-complete bifurcation.mesh.vtu]"
puts $fp "adjacency [file join $fullrundir mesh-complete bifurcation.xadj.gz]"
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

#
#  more files needed by solver
#

if {$use_resistance != 2 || $use_init_flow_type == 1} {
  file copy [file join $fullrundir bct.dat.inflow] [file join $fullrundir bct.dat]
} else {
  file copy [file join $fullrundir bct.dat.inflow.steady] [file join $fullrundir bct.dat]
}
set fp [open [file join $fullrundir numstart.dat] w]
fconfigure $fp -translation lf
puts $fp "0"
close $fp

set infp [open solver.inp.bifurcation r]

set outfp [open $fullrundir/solver.inp w]
fconfigure $outfp -translation lf

if {$use_ascii_format == 0} {
   set file_format binary
} else {
   set file_format ascii
}

while {[gets $infp line] >= 0} {
  regsub -all my_initial_time_increment $line [expr 1.1/$timesteps] line
  regsub -all my_number_of_time_steps $line [expr $num_periods*$timesteps] line
  regsub -all "\#resistance_sim" $line {} line
  if {$selected_LS} {
       regsub -all "\#leslib_linear_solver" $line {} line
  } else {
       regsub -all "\#memls_linear_solver" $line {} line
  }
  regsub -all my_output_format $line $file_format line
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
#  Create vis files
#
puts "Reduce restart files."
if {$use_ascii_format != 0} {
  set aflag "-nonbinary"
} else {
  set aflag ""
}

for {set i [expr $endstep - $timesteps + 1]} {$i <= $endstep} {incr i} {
   if [catch {exec $POSTSOLVER -dir $fullsimdir -sn $i $aflag -bflux -vis [file join $fullsimdir bifurcation_res$i.vis]} msg] {
     puts $msg
     return -code error "ERROR running cvpostsolver!"
   }
}
if [catch {exec $POSTSOLVER -dir $fullsimdir -sn 1 $aflag -vismesh [file join $fullsimdir bifurcation_mesh.vis]} msg] {
  puts $msg
  return -code error "ERROR running cvpostsolver!"
}

#
#  Create ParaView files (and calc vol flow through outlets)
#

source bifurcation-calc_flow.tcl

catch {repos_deleteList [repos_subList myrespara*]}
catch {repos_deleteList [repos_subList mytractpara*]}

catch {repos_delete -obj mymeshpara}
catch {xwrite Delete}

post_readVisMesh -file [file join $fullsimdir bifurcation_mesh.vis.gz] -obj mymeshpara

puts "Convert to ParaView."

# flow rate stuff
catch {unset lookup}
foreach i [bifurcation GetFaceIds] {
set lookup([bifurcation GetFaceAttr -faceId $i -attr gdscName]) \
    [bifurcation GetFaceNormal -face $i -u 0 -v 0]
}
catch {repos_delete -obj lt_iliac}
catch {repos_delete -obj rt_iliac}
catch {repos_delete -obj inflow}
repos_readXMLPolyData [file join $fullrundir mesh-complete mesh-surfaces lt_iliac.vtp] lt_iliac
repos_readXMLPolyData [file join $fullrundir mesh-complete mesh-surfaces rt_iliac.vtp] rt_iliac
repos_readXMLPolyData [file join $fullrundir mesh-complete mesh-surfaces inflow.vtp] inflow
set flow_lt_iliac 0
set flow_rt_iliac 0
set flow_inflow 0
set total_flow_lt_iliac 0
set total_flow_rt_iliac 0
set total_flow_inflow 0
catch {unset flows_lt_iliac}
catch {unset flows_rt_iliac}
catch {unset flows_inflow}

for {set i [expr $endstep - $timesteps + 1]} {$i <= $endstep} {incr i} {
  catch {repos_delete -obj myrespara$i}
  catch {repos_delete -obj mytractpara$i}
    post_readVisRes -file [file join $fullsimdir bifurcation_res$i.vis.gz] -grid mymeshpara -result myrespara$i -traction mytractpara$i
  set theMesh [repos_exportToVtk -src mymeshpara]
  set pressure [[[repos_exportToVtk -src myrespara$i] GetPointData] GetScalars]
  set velocity [[[repos_exportToVtk -src myrespara$i] GetPointData] GetVectors]
  set traction [[[repos_exportToVtk -src mytractpara$i] GetPointData] GetVectors]
  $pressure SetName pressure
  $velocity SetName velocity
  $traction SetName traction
  [$theMesh GetPointData] SetScalars $pressure
  [$theMesh GetPointData] SetVectors $velocity
  [$theMesh GetPointData] AddArray $traction
  

  vtkXMLDataSetWriter xwrite
  xwrite SetInputDataObject $theMesh
  xwrite SetFileName [file join $fullsimdir bifurcation-[format "%03i" $i].vtu]
  xwrite Write

  # flow rate stuff
  demoFlowThruFace $theMesh lt_iliac $lookup(lt_iliac) flow flow_lt_iliac
  demoFlowThruFace $theMesh rt_iliac $lookup(rt_iliac) flow flow_rt_iliac
  demoFlowThruFace $theMesh inflow $lookup(inflow) flow flow_inflow
  lappend flows_lt_iliac $flow_lt_iliac
  lappend flows_rt_iliac $flow_rt_iliac
  lappend flows_inflow $flow_inflow
  set total_flow_lt_iliac [expr $total_flow_lt_iliac + $flow_lt_iliac]
  set total_flow_rt_iliac [expr $total_flow_rt_iliac + $flow_rt_iliac]
  set total_flow_inflow   [expr $total_flow_inflow + $flow_inflow]

  [$theMesh GetPointData] RemoveArray pressure
  [$theMesh GetPointData] RemoveArray velocity
  [$theMesh GetPointData] RemoveArray traction

  xwrite Delete
}

# calculate flow rate
set avg_lt_iliac [expr $total_flow_lt_iliac/double([llength [repos_subList myrespara*]])]
set avg_rt_iliac [expr $total_flow_rt_iliac/double([llength [repos_subList myrespara*]])]
set avg_inflow   [expr $total_flow_inflow/double([llength [repos_subList myrespara*]])]
printList $flows_lt_iliac
printList $flows_rt_iliac
printList $flows_inflow
puts "lt iliac avg: $avg_lt_iliac"
puts "rt iliac avg: $avg_rt_iliac"
puts "inflow   avg: $avg_inflow"

# create mean pressure / velcoity object
catch {repos_delete -obj avgpointdata}
catch {repos_delete -obj avgtract}
post_calcAvgPointData -inputPdList [repos_subList myrespara*] -result avgpointdata
#post_calcAvgPointData -inputPdList [repos_subList mytractpara*] -result avgtractdata
set theMesh [repos_exportToVtk -src mymeshpara]
set pressure [[[repos_exportToVtk -src avgpointdata] GetPointData] GetScalars]
set velocity [[[repos_exportToVtk -src avgpointdata] GetPointData] GetVectors]
#set traction [[[repos_exportToVtk -src avgtract] GetPointData] GetVectors]
$pressure SetName mean_pressure
$velocity SetName mean_velocity
#$traction SetName mean_traction
[$theMesh GetPointData] SetScalars $pressure
[$theMesh GetPointData] SetVectors $velocity
[$theMesh GetPointData] RemoveArray $traction

vtkXMLDataSetWriter xwrite
xwrite SetInputDataObject $theMesh
xwrite SetFileName [file join $fullsimdir mean-bifurcation.vtu]
xwrite Write
xwrite Delete
if {$use_resistance == 2} {
    set pfp [open [file join $fullrundir "mean.pressures"] w]
  fconfigure $pfp -translation lf
  set numPvals [$pressure GetNumberOfTuples]
  puts $pfp $numPvals
    for {set i 0} {$i < $numPvals} {incr i} {
     puts $pfp [$pressure GetTuple1 $i]
    }
  close $pfp
}
[$theMesh GetPointData] RemoveArray mean_pressure
[$theMesh GetPointData] RemoveArray mean_velocity

catch {repos_delete -obj avgpointdata}
catch {repos_delete -obj avgtract}

repos_deleteList [repos_subList myrespara*]
repos_deleteList [repos_subList mytractpara*]

#
#  only do second pass if we are doing impedance
#

if {$use_resistance == 2} {

#
#  create the impt.dat file
#

source bifurcation-create-imptdat.tcl

set outlets [list {lt_iliac           0.360  24000} \
	          {rt_iliac           0.360  24000}]
set period 1.1
set numPts $timesteps
if {$timesteps < 30} {
  set numKeptModes $timesteps
} else {
  set numKeptModes 30
}
set scale_to_mm_flag 1

file delete [file join $fullrundir impt.dat]
create_imptdat_file $outlets $period $numPts $numKeptModes $scale_to_mm_flag
if {$num_procs > 1} {
    file copy [file join $fullrundir impt.dat] $fullsimdir
}

file delete [file join $fullrundir Qhistor.dat]
set fp [open [file join $fullrundir Qhistor.dat] w]
fconfigure $fp -translation lf
puts $fp $timesteps
for {set i 0} {$i <= $timesteps} {incr i} {
  if {$use_init_flow_type == 0} {
    puts $fp "$avg_lt_iliac $avg_rt_iliac"
  } else {
    if {$i < $timesteps} {
      puts $fp "[lindex $flows_lt_iliac $i] [lindex $flows_rt_iliac $i]"
    } else {
      puts $fp "[lindex $flows_lt_iliac 0] [lindex $flows_rt_iliac 0]"
    }
  }
}
close $fp
if {$num_procs > 1} {
  file copy [file join $fullrundir Qhistor.dat] $fullsimdir
}

#
#  more files needed by solver
#

file rename [file join $fullrundir bct.dat] [file join $fullrundir bct.dat.pass1]
file copy [file join $fullrundir bct.dat.inflow] [file join $fullrundir bct.dat]
file rename [file join $fullrundir solver.inp] [file join $fullrundir solver.inp.pass1]


set infp [open solver.inp.bifurcation r]

set outfp [open $fullrundir/solver.inp w]
fconfigure $outfp -translation lf

if {$use_ascii_format == 0} {
   set file_format binary
} else {
   set file_format ascii
}

while {[gets $infp line] >= 0} {
  regsub -all my_initial_time_increment $line [expr 1.1/$timesteps] line
  regsub -all my_number_of_time_steps $line [expr $num_periods2*$timesteps] line
  regsub -all "\#impedance_sim" $line {} line
  if {$selected_LS} {
       regsub -all "\#leslib_linear_solver" $line {} line
  } else {
       regsub -all "\#memls_linear_solver" $line {} line
  }
  regsub -all my_output_format $line $file_format line
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

set fp [open [file join $fullrundir solver.log] w]
puts $fp "Start running solver..."
close $fp

set ::tail_solverlog {}
tail [file join $fullrundir solver.log] .+ 1000 ::tail_solverlog
trace variable ::tail_solverlog w handle

exec $MPIEXEC -wdir $fullrundir $npflag $num_procs -env FLOWSOLVER_CONFIG $FLOWSOLVER_CONFIG $SOLVER solver.inp >>& [file join $rundir solver.log] &

set endstep 0
while {$endstep < [expr ($num_periods+$num_periods2)*$timesteps]} {
  set waittwoseconds 0
  after 2000 set waittwoseconds 1
  vwait waittwoseconds
  set fp [open [file join $fullsimdir "numstart.dat"] r]
  gets $fp endstep
  close $fp
  set endstep [string trim $endstep]
}

cancelTail [file join $fullrundir solver.log]

#
#  move previous steps vis files out of the way
#
#file mkdir pass1
#foreach i [glob [file join $fullsimdir bifurcation_*vis.gz]] {
#    file rename $i [file join pass1 $i]
#}

#
#  Create vis files
#
puts "Reduce restart files."
if {$use_ascii_format != 0} {
  set aflag "-nonbinary"
} else {
  set aflag ""
}

for {set i [expr $endstep - $timesteps + 1]} {$i <= $endstep} {incr i} {
   if [catch {exec $POSTSOLVER -dir $fullsimdir -sn $i $aflag -bflux -vis [file join $fullsimdir bifurcation2_res$i.vis]} msg] {
     puts $msg
     return -code error "ERROR running cvpostsolver!"
   }
}
if [catch {exec $POSTSOLVER -dir $fullsimdir -sn 1 $aflag -vismesh [file join $fullsimdir bifurcation2_mesh.vis]} msg] {
  puts $msg
  return -code error "ERROR running cvpostsolver!"
}

#
#  Create ParaView files
#

catch {repos_deleteList [repos_subList myrespara*]}
catch {repos_deleteList [repos_subList mytractpara*]}

catch {repos_delete -obj mymeshpara}
catch {xwrite Delete}

post_readVisMesh -file [file join $fullsimdir bifurcation2_mesh.vis.gz] -obj mymeshpara

puts "Convert to ParaView."
for {set i [expr $endstep - $timesteps + 1]} {$i <= $endstep} {incr i} {
  catch {repos_delete -obj myrespara$i}
  catch {repos_delete -obj mytractpara$i}
  post_readVisRes -file [file join $fullsimdir bifurcation2_res$i.vis.gz] -grid mymeshpara -result myrespara$i -traction mytractpara$i
  set theMesh [repos_exportToVtk -src mymeshpara]
  set pressure [[[repos_exportToVtk -src myrespara$i] GetPointData] GetScalars]
  set velocity [[[repos_exportToVtk -src myrespara$i] GetPointData] GetVectors]
  set traction [[[repos_exportToVtk -src mytractpara$i] GetPointData] GetVectors]
  $pressure SetName pressure
  $velocity SetName velocity
  $traction SetName traction
  [$theMesh GetPointData] SetScalars $pressure
  [$theMesh GetPointData] SetVectors $velocity
  [$theMesh GetPointData] AddArray $traction
  

  vtkXMLDataSetWriter xwrite
  xwrite SetInputDataObject $theMesh
  xwrite SetFileName [file join $fullsimdir bifurcation2-[format "%03i" $i].vtu]
  xwrite Write

  [$theMesh GetPointData] RemoveArray pressure
  [$theMesh GetPointData] RemoveArray velocity
  [$theMesh GetPointData] RemoveArray traction

  xwrite Delete
}

# create mean pressure / velcoity object
catch {repos_delete -obj avgpointdata}
catch {repos_delete -obj avgtract}
post_calcAvgPointData -inputPdList [repos_subList myrespara*] -result avgpointdata
#post_calcAvgPointData -inputPdList [repos_subList mytractpara*] -result avgtractdata
set theMesh [repos_exportToVtk -src mymeshpara]
set pressure [[[repos_exportToVtk -src avgpointdata] GetPointData] GetScalars]
set velocity [[[repos_exportToVtk -src avgpointdata] GetPointData] GetVectors]
#set traction [[[repos_exportToVtk -src avgtract] GetPointData] GetVectors]
$pressure SetName mean_pressure
$velocity SetName mean_velocity
#$traction SetName mean_traction
[$theMesh GetPointData] SetScalars $pressure
[$theMesh GetPointData] SetVectors $velocity
[$theMesh GetPointData] RemoveArray $traction

vtkXMLDataSetWriter xwrite
xwrite SetInputDataObject $theMesh
xwrite SetFileName [file join $fullsimdir mean-bifurcation2.vtu]
xwrite Write
xwrite Delete
[$theMesh GetPointData] RemoveArray mean_pressure
[$theMesh GetPointData] RemoveArray mean_velocity

catch {repos_delete -obj avgpointdata}
catch {repos_delete -obj avgtract}

repos_deleteList [repos_subList myrespara*]
repos_deleteList [repos_subList mytractpara*]

}
