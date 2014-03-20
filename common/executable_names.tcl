
# central area to change name of executables

set PRESOLVER     $gExternalPrograms(cvpresolver)
set POSTSOLVER    $gExternalPrograms(cvpostsolver)
set MPIEXEC       $gExternalPrograms(mpiexec)
set SOLVER        $gExternalPrograms(cvflowsolver)
set FLOWSOLVER_CONFIG [file dirname $gExternalPrograms(cvflowsolver)] 
set ADAPTOR       $gExternalPrograms(cvadaptor)
set OPOSTSOLVER   $gExternalPrograms(osmscpostsolver)

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
set OPOSTSOLVER   [glob $env(SIMVASCULAR_HOME)/Code/Bin/osmscpostsolver*.exe]
}

if {0 == 1} {
set PRESOLVER     presolver
set POSTSOLVER    postsolver
set MPIEXEC       /usr/bin/mpiexec
set SOLVER        mysolver
set FLOWSOLVER_CONFIG [file dirname $gExternalPrograms(cvflowsolver)] 
set ADAPTOR       myadaptor
set OPOSTSOLVER   mypost
}

