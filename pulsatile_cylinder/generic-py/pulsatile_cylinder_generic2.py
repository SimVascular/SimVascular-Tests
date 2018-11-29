# Copyright (c) Stanford University, The Regents of the University of
#               California, and others.
#
# All Rights Reserved.
#
# See Copyright-SimVascular.txt for additional details.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject
# to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
# IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER
# OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

#
# prompt user for number of procs
#
import os
from sys import path
path.append("../polydata-tetgen-py")
import pulsatile_cylinder as pc
import cylinder_create_model_polydata
import pulsatile_cylinder_create_mesh_tetgen as mesh 
import string
import executable_names


if pc.num_procs ==-1:
    pc.num_procs = raw_input("Number of Processors to use (1-4)?")

#
# prompt user for linear solver
#
if pc.selected_LS == -1:
    selected_LS = raw_input("Use which linear solver? svLS or leslib ?")

#
# prompt user for mesh type
#
if pc.pulsatile_mesh_option == -1:
    pulsatile_mesh_option = raw_input("Select the Mesh to Use: Isotropic Mesh or Boundary Layer Mesh ?")

#
# prompt user for the number of timesteps
#
if pc.timesteps == -1:
    timesteps = raw_input("Select the Number of Time Steps 16, 32, 64, 128, 256, 512?")
    pc.timesteps = timesteps

#
#  do work!
#
import datetime
now = datetime.datetime.now()
rundir = str(now.month)+'-'+str(now.day)+ '-' + str(now.year) + '-' + \
    str(now.hour) + str(now.minute) + str(now.second)
    
pwd = os.getcwd()+'/'
fullrundir = pwd+rundir
os.mkdir(fullrundir)

if (int(pc.num_procs) == 1):
  fullsimdir = fullrundir
else:
  fullsimdir = fullrundir + str(int(pc.num_procs)-pc.procs_case)

# create model, mesh, and bc files
if pc.gOptions["meshing_solid_kernel"] == 'PolyData':
    solidfn = cylinder_create_model_polydata.demo_create_model(fullrundir)
    #solidfn = cylinder_create_model_polydata.demo_create_cylinder(fullrundir)
    #solidfn = cylinder_create_model_polydata.demo_loft_cylinder(fullrundir)

if pc.gOptions["meshing_kernel"] =='TetGen':
    mesh.pulsatile_cylinder_create_mesh_TetGen(solidfn,fullrundir,pulsatile_mesh_option)


import pulsatile_cylinder_create_bc_files_generic as bc
bc.pulsatile_cylinder_create_flow_files_generic(fullrundir)

#
#  Create script file for presolver
#

print "Create script file for presolver."
SVPRE = fullrundir + '/cylinder.svpre'
f= open(SVPRE,'w+')
f.write('mesh_and_adjncy_vtu %s\n' % (fullrundir + '/mesh-complete/cylinder.mesh.vtu'))
f.write('prescribed_velocities_vtp %s\n' % (fullrundir + '/mesh-complete/mesh-surfaces/inflow.vtp'))
f.write('noslip_vtp %s\n' %(fullrundir +'/mesh-complete/mesh-surfaces/wall.vtp'))
f.write('zero_pressure_vtp %s\n' % (fullrundir + '/mesh-complete/mesh-surfaces/outlet.vtp'))
f.write('set_surface_id_vtp %s 1\n' % (fullrundir + '/mesh-complete/cylinder.exterior.vtp'))

f.write('fluid_density 0.00106\n')
f.write('fluid_viscosity 0.004\n')
f.write('bct_period 0.2\n')
f.write('bct_analytical_shape plug\n')
f.write('bct_point_number 201\n')
f.write('bct_fourier_mode_number 10\n')
f.write('bct_create %s %s\n' % (fullrundir + '/mesh-complete/mesh-surfaces/inflow.vtp', fullrundir +'/flow-files/inflow.flow'))
f.write('bct_write_dat %s\n' % (fullrundir + '/bct.dat'))
f.write('bct_write_vtp %s\n' % (fullrundir + '/bct.vtp'))

f.write('write_numstart 0 %s\n' % (fullrundir+'/numstart.dat'))

f.write('write_geombc %s\n' % (fullrundir + '/geombc.dat.1'))
f.write('write_restart %s\n' % (fullrundir +'/restart.0.1'))
f.close()
    
#
#  Call pre-processor
#

print('Run cvpresolver.')
cmd = executable_names.PRESOLVER+' '+ fullrundir+'/cylinder.svpre'

import subprocess
try:
    proc = subprocess.Popen([executable_names.PRESOLVER, (fullrundir+'/cylinder.svpre')], stdout=subprocess.PIPE)
    (out, err) = proc.communicate()
    print out
except:
    print "Error running presolver"


timesteps = int(timesteps)
if (timesteps%16>0):
  raise ValueError("ERROR in number of specified timesteps")

total_timesteps = 2*timesteps

#
#  Run solver.
#

print('Run Solver.')

directory = os.path.dirname(os.path.realpath(__file__))
infp = open(directory+'/solver.inp', 'rU')

outfp = open(fullrundir+'/solver.inp', 'w+')

for line in infp:
    line = string.replace(line,'my_initial_time_increment', str(0.2/timesteps))
    line = string.replace(line,'my_number_of_time_steps', str(total_timesteps))
    if (selected_LS=='leslib'):
        line = string.replace(line,'#leslib_linear_solver', "")
    else:
        line = string.replace(line,'#memls_linear_solver', "")
    outfp.write(line)
infp.close()
outfp.close()


from sys import platform

if platform == "win32":
    npflag = '-np'
else:
    npflag = '-np'
    
def handle(args):
    print(args(0)),
    
fp =open(fullrundir + '/solver.log','w+')
fp.write('Start running solver...')
fp.close()

try:
    cmd = 'cd'+' '+fullrundir+ ' && '+ executable_names.SOLVER+ (' '+fullrundir+'/solver.inp')+' >> '+(fullrundir+'/solver.log')
    os.system(cmd)
except:
    print "Error running solver"

endstep=0
fp =open(fullrundir + '/numstart.dat','rU')
last = fp.readline()
fp.close()
print "Total number of timesteps finished: " + last.replace(' ','')
endstep = int(last.replace(' ',''))
##
##
##  Create ParaView files
##
print "Reduce restart files."
#

try:
    proc = subprocess.Popen([executable_names.POSTSOLVER, '-indir', fullsimdir, '-outdir',fullrundir,'-start','1', '-stop',str(endstep),'-incr','1','-sim_units_mm','-vtkcombo','-vtu','cylinder_results.vtu','-vtp','cylinder_results.vtp'], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    (out, err) = proc.communicate()
    print out
    print err
except:
    print "Error running postsolver"
#
##  compare results
##
#
path.append("./../generic-py")
import pulsatile_cylinder_compare_with_analytic_generic

