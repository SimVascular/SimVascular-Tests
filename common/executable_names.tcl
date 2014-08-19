
# central area to change name of executables

#set PRESOLVER     $gExternalPrograms(cvpresolver)
#set POSTSOLVER    $gExternalPrograms(cvpostsolver)
#set MPIEXEC       $gExternalPrograms(mpiexec)
#set SOLVER        $gExternalPrograms(cvflowsolver)
#set FLOWSOLVER_CONFIG [file dirname $gExternalPrograms(pwd)] 
#set ADAPTOR       $gExternalPrograms(cvadaptor)

if {0 == 1} {

  set SVRELEASEDIR  "C:/Program Files (x86)/SimVascular/sv/1362614537"
  set SVRELEASEDIR  "C:/Program Files (x86)/SimVascular/sv/1365232876"
  #set PRESOLVER     [glob $env(SIMVASCULAR_HOME)/Code/Bin/presolver*.exe]
  set PRESOLVER     "$SVRELEASEDIR/presolver-bin.exe"
  set MPIEXEC       "$SVRELEASEDIR/mpiexec.exe"
  set SOLVER        "$SVRELEASEDIR/flowsolver-bin.exe"
  set FLOWSOLVER_CONFIG [file dirname $SOLVER] 
  set POSTSOLVER    "$SVRELEASEDIR/postsolver-bin.exe"
  set ADAPTOR       "$SVRELEASEDIR/adaptor-bin.exe"

}

if {0 == 1} {
  set PRESOLVER     /home/danschi/Development/svDevelopment/simvascular_reorg/Code/Bin/presolver.exe
  set POSTSOLVER    /home/danschi/Development/svDevelopment/simvascular_reorg/Code/mypost
  set MPIEXEC       /usr/local/bin/mpiexec
  set SOLVER        /home/danschi/Development/svDevelopment/simvascular_reorg/Code/mysolver
  set FLOWSOLVER_CONFIG [file dirname $gExternalPrograms(cvflowsolver)] 
  set ADAPTOR       /home/danschi/Development/svDevelopment/simvascular_reorg/Code/myadaptor
}

if {0 == 1} {
  set PRESOLVER     /Users/jmerkow/code/SimVascular/bin/simvascular-development/Bin/presolver
  set POSTSOLVER    /Users/jmerkow/code/SimVascular/bin/simvascular-development/mypost
  set MPIEXEC       /usr/local/bin/mpiexec
  set SOLVER        /Users/jmerkow/code/SimVascular/bin/simvascular-development/mysolver
  set FLOWSOLVER_CONFIG [file dirname $gExternalPrograms(cvflowsolver)] 
  set ADAPTOR       /Users/jmerkow/code/SimVascular/bin/simvascular-development/myadaptor
}

if {1 == 1} {
  set PRESOLVER     /home/jameson/Code/SimVascular/bin/simvascular-dev/Bin/presolver
  set POSTSOLVER    /home/jameson/Code/SimVascular/bin/simvascular-dev/mypost
  set MPIEXEC       /usr/bin/mpiexec
  set SOLVER        /home/jameson/Code/SimVascular/bin/simvascular-dev/mysolver
  set FLOWSOLVER_CONFIG [file dirname $gExternalPrograms(cvflowsolver)] 
  set ADAPTOR       /home/jameson/Code/SimVascular/bin/simvascular-dev/myadaptor
}