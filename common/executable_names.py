# central area to change name of executables
import os
#hard code for now  
gExternalPrograms = {}
import sys

if sys.platform == "darwin":
    gExternalPrograms['cvpresolver'] = '/usr/local/sv/svsolver/2019-01-19/svpre'
    gExternalPrograms['cvpostsolver'] = '/usr/local/sv/svsolver/2019-01-19/svpost'
    gExternalPrograms['mpiexec'] = '/usr/local/sv/svsolver/2019-01-19/bin/mpiexec'
    gExternalPrograms['cvflowsolver'] = '/usr/local/sv/svsolver/2019-01-19/svsolver'
    gExternalPrograms['cvadaptor'] = ''
elif sys.platform == "linux2":
    gExternalPrograms['cvpresolver'] = '/usr/local/sv/svsolver/2019-02-07/svpre'
    gExternalPrograms['cvpostsolver'] = '/usr/local/sv/svsolver/2019-02-07/svpost'
    gExternalPrograms['mpiexec'] = '/usr/local/sv/svsolver/2019-02-07/bin/mpiexec'
    gExternalPrograms['cvflowsolver'] = '/usr/local/sv/svsolver/2019-02-07/svsolver'
    gExternalPrograms['cvadaptor'] = ''
elif sys.platform == "win32" or sys.platform =="cygwin":
    gExternalPrograms['cvpresolver'] = 'C:/Program Files/SimVascular/svSolver/2019-05-28/svpre-bin.exe'
    gExternalPrograms['cvpostsolver'] = 'C:/Program Files/SimVascular/svSolver/2019-05-28/svpost-bin.exe'
    gExternalPrograms['mpiexec'] = 'C:/Program Files/Microsoft MPI/bin/mpiexec.exe'
    gExternalPrograms['cvflowsolver'] = 'C:/Program Files/SimVascular/svSolver/2019-05-28/svsolver-nompi-bin.exe'
    gExternalPrograms['cvadaptor'] = ''
else:
    raise ValueError("System unrecognized")

PRESOLVER = gExternalPrograms['cvpresolver']
POSTSOLVER = gExternalPrograms['cvpostsolver']
MPIEXEC =gExternalPrograms['mpiexec']
SOLVER = gExternalPrograms['cvflowsolver']
FLOWSOLVER_CONFIG = os.path.dirname(gExternalPrograms['cvflowsolver'])
ADAPTOR = gExternalPrograms['cvadaptor']

