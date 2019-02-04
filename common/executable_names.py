# central area to change name of executables
import os
#hard code for now  
gExternalPrograms = {}
import sys

if sys.platform == "darwin":
    gExternalPrograms['cvpresolver'] = '/usr/local/sv/svsolver/2017-08-14/svpre'
    gExternalPrograms['cvpostsolver'] = '/usr/local/sv/svsolver/2017-08-14/svpost'
    gExternalPrograms['mpiexec'] = '/usr/local/sv/svsolver/2017-08-14/bin/mpiexec'
    gExternalPrograms['cvflowsolver'] = '/usr/local/sv/svsolver/2017-08-14/svsolver'
    gExternalPrograms['cvadaptor'] = ''
elif sys.platform == "linux2":
    gExternalPrograms['cvpresolver'] = '/usr/local/sv/svsolver/2017-08-14/svpre'
    gExternalPrograms['cvpostsolver'] = '/usr/local/sv/svsolver/2017-08-14/svpost'
    gExternalPrograms['mpiexec'] = '/usr/local/sv/svsolver/2017-08-14/bin/mpiexec'
    gExternalPrograms['cvflowsolver'] = '/usr/local/sv/svsolver/2017-08-14/svsolver'
    gExternalPrograms['cvadaptor'] = ''
elif sys.platform == "win32" or sys.platform =="cygwin":
    gExternalPrograms['cvpresolver'] = 'C:/Program Files/SimVascular/svSolver/2017-08-23/svpre-bin.exe'
    gExternalPrograms['cvpostsolver'] = 'C:/Program Files/SimVascular/svSolver/2017-08-23/svpost-bin.exe'
    gExternalPrograms['mpiexec'] = 'C:/Program Files/Microsoft MPI/bin/mpiexec.exe'
    gExternalPrograms['cvflowsolver'] = 'C:/Program Files/SimVascular/svSolver/2017-08-23/svsolver-nompi-bin.exe'
    gExternalPrograms['cvadaptor'] = ''
else:
    raise ValueError("System unrecognized")

PRESOLVER = gExternalPrograms['cvpresolver']
POSTSOLVER = gExternalPrograms['cvpostsolver']
MPIEXEC =gExternalPrograms['mpiexec']
SOLVER = gExternalPrograms['cvflowsolver']
FLOWSOLVER_CONFIG = os.path.dirname(gExternalPrograms['cvflowsolver'])
ADAPTOR = gExternalPrograms['cvadaptor']

