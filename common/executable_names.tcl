
# central area to change name of executables

set PRESOLVER     $gExternalPrograms(svpre)
set POSTSOLVER    $gExternalPrograms(svpost)
set MPIEXEC       $gExternalPrograms(mpiexec)
set SOLVER        $gExternalPrograms(svsolver-mpi)
set FLOWSOLVER_CONFIG [file dirname $gExternalPrograms(svsolver-mpi)] 

if {0 == 1} {

  set SVRELEASEDIR  "C:/Program Files (x86)/SimVascular/sv/1437247112"
  set PRESOLVER     "$SVRELEASEDIR/presolver-bin.exe"
#  set MPIEXEC       "$SVRELEASEDIR/mpiexec.exe"
  set SOLVER        "$SVRELEASEDIR/flowsolver-bin.exe"
  set FLOWSOLVER_CONFIG [file dirname $SOLVER] 
  set POSTSOLVER    "$SVRELEASEDIR/postsolver-bin.exe"

}

if {0 == 1} {
  set PRESOLVER     /home/danschi/Development/svDevelopment/simvascular_reorg/Code/Bin/presolver.exe
  set POSTSOLVER    /home/danschi/Development/svDevelopment/simvascular_reorg/Code/mypost
  set MPIEXEC       /usr/local/bin/mpiexec
  set SOLVER        /home/danschi/Development/svDevelopment/simvascular_reorg/Code/mysolver
  set FLOWSOLVER_CONFIG [file dirname $gExternalPrograms(svsolver-mpi)] 
}

if {0 == 1} {
set MY_SIMVASCULAR_HOME "/Users/adamupdegrove/Documents/Software/SimVascular/Master"
set PRESOLVER     "$MY_SIMVASCULAR_HOME/Code/Build/mypre"
set POSTSOLVER    "$MY_SIMVASCULAR_HOME/Code/Build/mypost"
set MPIEXEC       /opt/local/bin/mpiexec-mpich-gcc49
set SOLVER        "$MY_SIMVASCULAR_HOME/Code/Build/mysolver"
set FLOWSOLVER_CONFIG [file dirname $gExternalPrograms(svsolver-mpi)] 
}

if {0 == 1} {
set MY_SIMVASCULAR_HOME "/home/adamupdegrove/Documents/Software/SimVascular/Master"
set PRESOLVER     "$MY_SIMVASCULAR_HOME/Code/Build/mypre"
set POSTSOLVER    "$MY_SIMVASCULAR_HOME/Code/Build/mypost"
set MPIEXEC       /usr/bin/mpiexec
set SOLVER        "$MY_SIMVASCULAR_HOME/Code/Build/mysolver"
set FLOWSOLVER_CONFIG [file dirname $gExternalPrograms(svsolver-mpi)] 
}
