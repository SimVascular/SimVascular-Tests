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
import bifurcation
import bifurcation_create_model_polydata
import bifurcation_create_mesh_tetgen as mesh 
import string
import executable_names
import sys


if bifurcation.num_procs ==-1:
    if sys.version_info <(3,0):
        bifurcation.num_procs = raw_input("Number of Processors to use (1-4)?")
    else:
        bifurcation.num_procs = input("Number of Processors to use (1-4)?")

#
# prompt user for linear solver
#
if bifurcation.selected_LS == -1:
    bifurcation.selected_LS ="svLS"

#
# prompt user for mesh type
#
if bifurcation.bifurcation_mesh_option == -1:
    if sys.version_info <(3,0):
        bifurcation.bifurcation_mesh_option = raw_input("Select the Mesh to Use: Coarse Isotropic Mesh, Refined Mesh or Dense Mesh?")
    else:
        bifurcation.bifurcation_mesh_option = input("Select the Mesh to Use: Coarse Isotropic Mesh, Refined Mesh or Dense Mesh?")


#
# prompt user about BC
#
if bifurcation.use_resistance == -1:
    if sys.version_info < (3,0):
        use_resistance= raw_input("Select Outlet B.C: Zero Pressure or Resistance?")
    else:
        use_resistance= input("Select Outlet B.C: Zero Pressure or Resistance?")


#
# prompt user for the number of timesteps
#
if bifurcation.timesteps == -1:
    if sys.version_info < (3,0):
        timesteps = raw_input("Select the Number of Time Steps 5, 15, 25, 50, 100, 200, 400, 800?")
    else:
        timesteps = input("Select the Number of Time Steps 5, 15, 25, 50, 100, 200, 400, 800?")

    timesteps = int(timesteps)
#
# prompt user for the number of periods
#

if bifurcation.num_periods == -1:
    if sys.version_info < (3,0):
        num_periods = raw_input("Select the Number of Cycles: 2, 3, 4, 5, 6 ?")
    else:
        num_periods = input("Select the Number of Cycles: 2, 3, 4, 5, 6 ?")

print ("Number of periods: %s" % num_periods)

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

if (int(bifurcation.num_procs) == 1):
  fullsimdir = fullrundir
else:
  fullsimdir = fullrundir + str(int(bifurcation.num_procs)-bifurcation.procs_case)

# copy files into rundir
from shutil import copytree
copytree("../generic-py/bifurcation-flow-files", (fullrundir + "/flow-files"))

# create model, mesh, and bc files
if bifurcation.gOptions["meshing_solid_kernel"] == 'PolyData':
    solidfn = bifurcation_create_model_polydata.demo_create_model(fullrundir)

if bifurcation.gOptions["meshing_kernel"] =='TetGen':
    mesh.bifurcation_create_mesh_TetGen(solidfn,fullrundir,bifurcation.bifurcation_mesh_option)

#
#  Create script file for presolver
#

print ("Create script file for presolver.")
SVPRE = fullrundir + '/bifurcation.svpre'
f= open(SVPRE,'w+')
f.write('mesh_and_adjncy_vtu %s\n' % (fullrundir + '/mesh-complete/bifurcation.mesh.vtu'))
f.write('prescribed_velocities_vtp %s\n' % (fullrundir + '/mesh-complete/mesh-surfaces/inflow.vtp'))
f.write('noslip_vtp %s\n' %(fullrundir +'/mesh-complete/walls_combined.vtp'))
f.write('zero_pressure_vtp %s\n' % (fullrundir + '/mesh-complete/mesh-surfaces/lt_iliac.vtp'))
f.write('set_surface_id_vtp %s 1\n' % (fullrundir + '/mesh-complete/bifurcation.exterior.vtp'))
if use_resistance =='Resistance':
  f.write('set_surface_id_vtp %s 2\n' % (fullrundir + '/mesh-complete/mesh-surfaces/lt_iliac.vtp'))
f.write('zero_pressure_vtp %s\n' % (fullrundir + '/mesh-complete/mesh-surfaces/rt_iliac.vtp'))
if use_resistance =='Resistance':
  f.write('set_surface_id_vtp %s 3\n' % (fullrundir + '/mesh-complete/mesh-surfaces/rt_iliac.vtp'))

f.write('fluid_density 0.00106\n')
f.write('fluid_viscosity 0.004\n')
f.write('bct_period 1.1\n')
f.write('bct_analytical_shape womersley\n')
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

import subprocess
try:
    proc = subprocess.Popen([executable_names.PRESOLVER, (fullrundir+'/bifurcation.svpre')], stdout=subprocess.PIPE)
    (out, err) = proc.communicate()
    print (out)
    print (err)
except:
    print ("Error running presolver")

#
#  Run solver.
#

print('Run Solver.')

directory = os.path.dirname(os.path.realpath(__file__))
infp = open(directory+'/solver.inp', 'rU')

outfp = open(fullrundir+'/solver.inp', 'w+')

for line in infp:
    line = line.replace('my_initial_time_increment', str(1.1/timesteps))
    line = line.replace('my_number_of_time_steps', str(timesteps*int(num_periods)))
    line = line.replace('#resistance_sim','')
    if (bifurcation.selected_LS=='leslib'):
        line = line.replace('#leslib_linear_solver', "")
    else:
        line = line.replace('#svls_linear_solver', "")
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
    print ("Error running solver")

endstep=0
fp =open(fullrundir + '/numstart.dat','rU')
last = fp.readline()
fp.close()
print ("Total number of timesteps finished: " + last.replace(' ',''))
endstep = int(last.replace(' ',''))
##
##
##  Create ParaView files
##
print ("Reduce restart files.")
#

try:
    proc = subprocess.Popen([executable_names.POSTSOLVER, '-indir', fullsimdir, '-outdir',fullrundir,'-start','1', '-stop',str(endstep),'-incr','1','-sim_units_mm','-vtkcombo','-vtu','bifurcation_results.vtu','-vtp','bifurcation_results.vtp'], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    (out, err) = proc.communicate()
    print (out)
    print (err)
except:
    print ("Error running postsolver")
#
##  compare results
##
#
#source ../generic/pulsatile_cylinder_compare_with_analytic_generic.tcl

