
# central area to change name of executables

if [file exists override_executable_names.tcl] {
  source override_executable_names.tcl
} else {
  if {[info vars PRESOLVER] == ""} {
      set PRESOLVER     $gExternalPrograms(svpre)
  }
  if {[info vars POSTSOLVER] == ""} {
      set POSTSOLVER    $gExternalPrograms(svpost)
  }
  if {[info vars MPIEXEC] == ""} {
	set MPIEXEC       $gExternalPrograms(mpiexec)
  }
  if {[info vars SOLVER] == ""} {
	set SOLVER        $gExternalPrograms(svsolver-mpi)
  }
  if {[info vars FLOWSOLVER_CONFIG] == ""} {
	set FLOWSOLVER_CONFIG [file dirname $gExternalPrograms(svsolver-mpi)]
  }
}

