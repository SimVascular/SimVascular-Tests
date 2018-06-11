# central area to change name of executables
import os
#hard code for now  
gExternalPrograms = {}
gExternalPrograms['cvpresolver'] = '/usr/local/sv/svsolver/2017-08-14/svpre'
gExternalPrograms['cvpostsolver'] = '/usr/local/sv/svsolver/2017-08-14/svpost'
gExternalPrograms['mpiexec'] = '/usr/local/sv/svsolver/2017-08-14/bin/mpiexec'
gExternalPrograms['cvflowsolver'] = '/usr/local/sv/svsolver/2017-08-14/svsolver'
gExternalPrograms['cvadaptor'] = ''
PRESOLVER = gExternalPrograms['cvpresolver']
POSTSOLVER = gExternalPrograms['cvpostsolver']
MPIEXEC =gExternalPrograms['mpiexec']
SOLVER = gExternalPrograms['cvflowsolver']
FLOWSOLVER_CONFIG = os.path.dirname(gExternalPrograms['cvflowsolver'])
ADAPTOR = gExternalPrograms['cvadaptor']

