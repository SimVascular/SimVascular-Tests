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
import deformable_cylinder as pc
import cylinder_create_model_polydata
import deformable_cylinder_create_mesh_tetgen as mesh 
import executable_names

# options:
pc.num_procs = 1
pc.selected_LS = 'svLS'
pc.run_varwall = 'Yes'


if pc.num_procs ==-1:
    pc.num_procs = raw_input("Number of Processors to use (1-4)?")

#
# prompt user for linear solver
#
if pc.selected_LS == -1:
    pc.selected_LS = raw_input("Use which linear solver? svLS or leslib ?")


if pc.run_varwall == -1:
    pc.run_varwall = raw_input("Variable Wall Selection: Add a variable wall demo? No or Yes?")

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

rigid_steady_dir = fullrundir +'/rigid_steady'
def_steady_dir = fullrundir + '/deformable_steady'
def_pulse_dir = fullrundir + '/deformable_pulsatile'
def_varwall_dir = fullrundir + '/deformable_varwall'

os.mkdir(rigid_steady_dir)
os.mkdir(def_steady_dir)
os.mkdir(def_pulse_dir)
os.mkdir(def_varwall_dir)

if (int(pc.num_procs) == 1):
  rigid_steady_sim_dir = rigid_steady_dir
  def_steady_sim_dir = def_steady_dir
  def_pulse_sim_dir = def_pulse_dir
  def_varwall_sim_dir = def_varwall_dir
else:
  rigid_steady_sim_dir = rigid_steady_dir + str(int(pc.num_procs)-pc.procs_case)
  def_steady_sim_dir = def_steady_dir + str(int(pc.num_procs)-pc.procs_case)
  def_pulse_sim_dir = def_pulse_dir + str(int(pc.num_procs)-pc.procs_case)
  def_varwall_sim_dir = def_varwall_dir + str(int(pc.num_procs)-pc.procs_case)

# copy files into rundir
from shutil import copytree
copytree("../generic-py/deformable-flow-files", (fullrundir + "/flow-files"))

# create model, mesh, and bc files
if pc.gOptions["meshing_solid_kernel"] == 'PolyData':
    solidfn = cylinder_create_model_polydata.demo_create_model(fullrundir)

if pc.gOptions["meshing_kernel"] =='TetGen':
    mesh.deformable_cylinder_create_mesh_TetGen(solidfn,fullrundir)


#
#  Create script file for presolver
#

print("Create script file for steady bct.")
SVPRE = fullrundir + '/steady_bct.svpre'
f= open(SVPRE,'w+')
f.write('mesh_and_adjncy_vtu %s\n' % (fullrundir + '/mesh-complete/cylinder.mesh.vtu'))

f.write('fluid_density 0.00106\n')
f.write('fluid_viscosity 0.004\n')
f.write('bct_period 1.1\n')
f.write('bct_analytical_shape parabolic\n')
f.write('bct_point_number 2\n')
f.write('bct_fourier_mode_number 1\n')
f.write('bct_create %s %s\n' % (fullrundir + '/mesh-complete/mesh-surfaces/inflow.vtp', fullrundir +'/flow-files/inflow.flow.steady'))
f.write('bct_write_dat %s\n' % (fullrundir + '/bct_steady.dat'))
f.write('bct_write_vtp %s\n' % (fullrundir + '/bct_steady.vtp'))
f.close()
    
#
#  Call pre-processor
#

print('Run cvpresolver for steady bct.')

import subprocess
try:
    proc = subprocess.Popen([executable_names.PRESOLVER, (fullrundir+'/steady_bct.svpre')], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    (out, err) = proc.communicate()
    print(out)
except:
    print("Error running presolver")


#
#  Create script file for presolver
#

print("Create script file for pulsatile bct.")
SVPRE = fullrundir + '/pulsatile_bct.svpre'
f= open(SVPRE,'w+')
f.write('mesh_and_adjncy_vtu %s\n' % (fullrundir + '/mesh-complete/cylinder.mesh.vtu'))

f.write('fluid_density 0.00106\n')
f.write('fluid_viscosity 0.004\n')
f.write('bct_period 1.1\n')
f.write('bct_analytical_shape parabolic\n')
f.write('bct_point_number 276\n')
f.write('bct_fourier_mode_number 10\n')
f.write('bct_create %s %s\n' % (fullrundir + '/mesh-complete/mesh-surfaces/inflow.vtp', fullrundir +'/flow-files/inflow.flow.pulsatile'))
f.write('bct_write_dat %s\n' % (fullrundir + '/bct_pulsatile.dat'))
f.write('bct_write_vtp %s\n' % (fullrundir + '/bct_pulsatile.vtp'))
f.close()
    
#
#  Call pre-processor
#

print('Run cvpresolver for pulsatile bct.')

try:
    proc = subprocess.Popen([executable_names.PRESOLVER, (fullrundir+'/pulsatile_bct.svpre')], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    (out, err) = proc.communicate()
    print(out)
except:
    print("Error running presolver")
    
from shutil import copyfile
copyfile(fullrundir+'/bct_steady.dat',rigid_steady_dir + "/bct.dat")
copyfile(fullrundir+'/bct_steady.dat',def_steady_dir + "/bct.dat")
copyfile(fullrundir+'/bct_pulsatile.dat',def_pulse_dir + "/bct.dat")
copyfile(fullrundir+'/bct_steady.dat',def_varwall_dir + "/bct.dat")

copyfile(fullrundir+'/bct_steady.vtp',rigid_steady_dir + "/bct.vtp")
copyfile(fullrundir+'/bct_steady.vtp',def_steady_dir + "/bct.vtp")
copyfile(fullrundir+'/bct_pulsatile.vtp',def_pulse_dir + "/bct.vtp")
copyfile(fullrundir+'/bct_steady.vtp',def_varwall_dir + "/bct.vtp")


#
#   Create presolver script file for rigid wall steady
#

print("Create script file for rigid wall steady.")
SVPRE = rigid_steady_dir + '/rigid_steady_cylinder.svpre'
f= open(SVPRE,'w+')
f.write('mesh_and_adjncy_vtu %s\n' % (fullrundir + '/mesh-complete/cylinder.mesh.vtu'))
f.write('prescribed_velocities_vtp %s\n' % (fullrundir + '/mesh-complete/mesh-surfaces/inflow.vtp'))
f.write('noslip_vtp %s\n' % (fullrundir + '/mesh-complete/mesh-surfaces/wall.vtp'))
f.write('pressure_vtp %s %f\n' % ((fullrundir+'/mesh-complete/mesh-surfaces/outlet.vtp'),11649.0))
f.write('set_surface_id_vtp %s 1\n' % (fullrundir + '/mesh-complete/cylinder.exterior.vtp'))
f.write('set_surface_id_vtp %s 2\n' % (fullrundir + '/mesh-complete/mesh-surfaces/outlet.vtp'))

f.write('initial_pressure 12000.0\n')
f.write('initial_velocity 0.0 0.0 0.1\n')

f.write('write_numstart 0 %s\n' % (rigid_steady_dir+'/numstart.dat'))
f.write('write_geombc %s\n' % (rigid_steady_dir + '/geombc.dat.1'))
f.write('write_restart %s\n' % (rigid_steady_dir +'/restart.0.1'))
f.close()

#
#  Call pre-processor
#

print('Run cvpresolver')
try:
    proc = subprocess.Popen([executable_names.PRESOLVER, (rigid_steady_dir+'/rigid_steady_cylinder.svpre')], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    (out, err) = proc.communicate()
    print(out)
except:
    print("Error running presolver")


timesteps = 100
print("Number of timesteps: 100")

#
#  Run solver.
#

print('Run Solver.')

directory = os.path.dirname(os.path.realpath(__file__))
infp = open(directory+'/solver.inp.deformable', 'rU')

outfp = open(rigid_steady_dir+'/solver.inp', 'w+')

for line in infp:
    line = line.replace('my_initial_time_increment', '0.001')
    line = line.replace('my_number_of_time_steps', '100')
    line = line.replace('my_deformable_flag', 'False')
    #line = line.replace('my_rho_infinity', '0.5')
    line = line.replace('my_step_construction', "0 1 0 1 0 1    # this is the standard three iteration")
    if (pc.selected_LS=='leslib'):
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
    
fp =open(rigid_steady_dir + '/solver.log','w+')
fp.write('Start running solver...')
fp.close()

try:
    #cmd = 'cd'+' '+rigid_steady_dir+ ' && '+ executable_names.SOLVER+ (' '+rigid_steady_dir+'/solver.inp')+' >> '+(rigid_steady_dir+'/solver.log')
    cmd = 'cd'+' '+'"'+rigid_steady_dir+'"'+' && '+'"'+executable_names.SOLVER+'"'+' '+'"'+rigid_steady_dir+'/solver.inp'+'"'
    print(cmd)
    os.system(cmd)
except:
    print("Error running solver")

endstep=0
fp =open(rigid_steady_sim_dir+'/numstart.dat','rU')
last = fp.readline()
fp.close()
print("Total number of timesteps finished: " + last.replace(' ',''))
endstep = int(last.replace(' ',''))
##
##
##  Create ParaView files
##
print("Reduce restart files.")
#
try:
    #proc = subprocess.Popen([executable_names.POSTSOLVER, '-indir', rigid_steady_sim_dir, '-outdir',rigid_steady_dir,'-sn',str(endstep), '-ph', '-td', '-sol', '-newsn', '0'], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    cmd = 'cd'+' '+'"'+fullrundir+'"'+' && '+'"'+executable_names.POSTSOLVER+'"' + ' -indir ' + '"'+ rigid_steady_sim_dir +'"'+ ' -outdir '+'"'+ rigid_steady_dir +'"'+ ' -sn '+ str(endstep) + ' -ph '+ ' -td ' + ' -sol ' + ' -newsn ' + '0' 
    print(cmd)
    os.system(cmd)
except:
    print("Error running postsolver")
    
try:
    #proc = subprocess.Popen([executable_names.POSTSOLVER, '-indir', rigid_steady_sim_dir, '-outdir',rigid_steady_dir,'-start','0', '-stop',str(timesteps),'-incr','25','-sim_units_mm','-vtkcombo','-vtu','cylinder_results.vtu','-vtp','cylinder_results.vtp'], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    cmd = 'cd'+' '+'"'+fullrundir+'"'+' && '+'"'+executable_names.POSTSOLVER+'"' + ' -indir ' + '"'+ rigid_steady_sim_dir +'"'+ ' -outdir '+'"'+ rigid_steady_dir +'"'+ ' -start '+ '0' + ' -stop '+ str(timesteps) + ' -incr ' + '25' + ' -sim_units_mm ' + ' -vtkcombo ' + ' -vtu ' + 'cylinder_results.vtu' + ' -vtp ' + 'cylinder_results.vtp'
    print(cmd)
    os.system(cmd)
except:
    print("Error running postsolver")
    
copyfile(rigid_steady_dir+'/restart.0.0',def_steady_dir + "/restart.0.1")

###
###
###    
###   DEFORMABLE STEADY CASE
###
###
###

#
#   Create presolver script file for rigid wall steady
#

print("Create script file for deformable wall steady.")
SVPRE = def_steady_dir + '/deformable_steady_cylinder.svpre'
f= open(SVPRE,'w+')
f.write('mesh_and_adjncy_vtu %s\n' % (fullrundir + '/mesh-complete/cylinder.mesh.vtu'))
f.write('prescribed_velocities_vtp %s\n' % (fullrundir + '/mesh-complete/mesh-surfaces/inflow.vtp'))
f.write('deformable_wall_vtp %s\n' % (fullrundir + '/mesh-complete/mesh-surfaces/wall.vtp'))
f.write('pressure_vtp %s %f\n' % ((fullrundir+'/mesh-complete/mesh-surfaces/outlet.vtp'),11649.000000))
f.write('set_surface_id_vtp %s 1\n' % (fullrundir + '/mesh-complete/cylinder.exterior.vtp'))
f.write('set_surface_id_vtp %s 2\n' % (fullrundir + '/mesh-complete/mesh-surfaces/outlet.vtp'))

f.write('deformable_E 414400.0\n')
f.write('deformable_thickness 1.0\n')
f.write('deformable_nu 0.5\n')
f.write('deformable_pressure 12000.0\n')
f.write('deformable_kcons 0.833333\n')
f.write('deformable_solve_displacements\n')
f.write('wall_displacements_write_vtp %s\n' % (def_steady_dir+'/walldisp.vtp'))

f.write('write_numstart 0 %s\n' % (def_steady_dir+'/numstart.dat'))
f.write('write_geombc %s\n' % (def_steady_dir + '/geombc.dat.1'))
f.write('append_displacements %s\n' % (def_steady_dir +'/restart.0.1'))
f.close()
#
#  Call pre-processor
#

print('Run cvpresolver')
try:
    proc = subprocess.Popen([executable_names.PRESOLVER, (def_steady_dir+'/deformable_steady_cylinder.svpre')], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    (out, err) = proc.communicate()
    print(out)
except:
    print("Error running presolver")
timesteps = 100
print("Number of timesteps: 100")

#
#  Run solver.
#

print('Run Solver.')

directory = os.path.dirname(os.path.realpath(__file__))
infp = open(directory+'/solver.inp.deformable', 'rU')

outfp = open(def_steady_dir+'/solver.inp', 'w+')

for line in infp:
    line = line.replace('my_initial_time_increment', '0.0004')
    line = line.replace('my_number_of_time_steps', '100')
    line = line.replace('my_deformable_flag', 'True')
    line = line.replace('my_rho_infinity', '0.0')
    line = line.replace('my_step_construction', "0 1 0 1 0 1 0 1    # this is the standard three iteration")
    if (pc.selected_LS=='leslib'):
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

    
fp =open(def_steady_dir + '/solver.log','w+')
fp.write('Start running solver...')
fp.close()

try:
    #cmd = 'cd'+' '+def_steady_dir+ ' && '+ executable_names.SOLVER+ (' '+def_steady_dir+'/solver.inp')+' >> '+(def_steady_dir+'/solver.log')
    cmd = 'cd'+' '+'"'+def_steady_dir+'"'+' && '+'"'+executable_names.SOLVER+'"'+' '+'"'+def_steady_dir+'/solver.inp'+'"'
    print(cmd)
    os.system(cmd)
except:
    print("Error running solver")

endstep=0
fp =open(def_steady_sim_dir+'/numstart.dat','rU')
last = fp.readline()
fp.close()
print("Total number of timesteps finished: " + last.replace(' ',''))
endstep = int(last.replace(' ',''))
##
##
##  Create ParaView files
##
print("Reduce restart files.")
#
try:
    #proc = subprocess.Popen([executable_names.POSTSOLVER, '-indir', def_steady_sim_dir, '-outdir',def_steady_dir,'-sn',str(endstep), '-ph', '-td', '-sol', '-newsn', '0'], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    cmd = 'cd'+' '+'"'+fullrundir+'"'+' && '+'"'+executable_names.POSTSOLVER+'"' + ' -indir ' + '"'+ def_steady_sim_dir +'"'+ ' -outdir '+'"'+ def_steady_dir +'"'+ ' -sn '+ str(endstep) + ' -ph '+ ' -td ' + ' -sol ' + ' -newsn ' + '0' 
    print(cmd)
    os.system(cmd)
except:
    print("Error running postsolver")
    
try:
    #proc = subprocess.Popen([executable_names.POSTSOLVER, '-indir', def_steady_sim_dir, '-outdir',def_steady_dir,'-start','0', '-stop',str(timesteps),'-incr','25','-sim_units_mm','-vtkcombo','-vtu','cylinder_results.vtu','-vtp','cylinder_results.vtp'], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    cmd = 'cd'+' '+'"'+fullrundir+'"'+' && '+'"'+executable_names.POSTSOLVER+'"' + ' -indir ' + '"'+ def_steady_sim_dir +'"'+ ' -outdir '+'"'+ def_steady_dir +'"'+ ' -start '+ '0' + ' -stop '+ str(timesteps) + ' -incr ' + '25' + ' -sim_units_mm ' + ' -vtkcombo ' + ' -vtu ' + 'cylinder_results.vtu' + ' -vtp ' + 'cylinder_results.vtp'
    print(cmd)
    os.system(cmd)
except:
    print("Error running postsolver")
    
if pc.run_varwall=='Yes':
###
###
###    
###   VARIABLE STEADY CASE
###
###
###
    copyfile(rigid_steady_dir+'/restart.0.0',def_varwall_dir + "/restart.0.1")
    print("Create script file for variable wall steady.")
    SVPRE = def_varwall_dir + '/variable_steady_cylinder.svpre'
    f= open(SVPRE,'w+')
    f.write('mesh_and_adjncy_vtu %s\n' % (fullrundir + '/mesh-complete/cylinder.mesh.vtu'))
    f.write('prescribed_velocities_vtp %s\n' % (fullrundir + '/mesh-complete/mesh-surfaces/inflow.vtp'))
    f.write('deformable_wall_vtp %s\n' % (fullrundir + '/mesh-complete/mesh-surfaces/wall.vtp'))
    f.write('pressure_vtp %s %f\n' % ((fullrundir+'/mesh-complete/mesh-surfaces/outlet.vtp'),11649.00000))
    f.write('set_surface_id_vtp %s 1\n' % (fullrundir + '/mesh-complete/cylinder.exterior.vtp'))
    f.write('set_surface_id_vtp %s 2\n' % (fullrundir + '/mesh-complete/mesh-surfaces/outlet.vtp'))
    f.write('set_surface_thickness_vtp %s 1.5\n' % (fullrundir + '/mesh-complete/mesh-surfaces/inflow.vtp'))
    f.write('set_surface_thickness_vtp %s 0.5\n' % (fullrundir + '/mesh-complete/mesh-surfaces/outlet.vtp'))
    f.write("solve_varwall_thickness\n")
    f.write("set_surface_E_vtp %s %i\n" % ((fullrundir + '/mesh-complete/mesh-surfaces/inflow.vtp'),518000))
    f.write("set_surface_E_vtp %s %i\n" % ((fullrundir + '/mesh-complete/mesh-surfaces/outlet.vtp'),310800))
    f.write("solve_varwall_E\n")
    f.write("varwallprop_write_vtp %s\n" % (def_varwall_dir+'/varwallprop.vtp'))
    
    f.write('deformable_nu 0.5\n')
    f.write('deformable_pressure 12000.0\n')
    f.write('deformable_kcons 0.833333\n')
    f.write('deformable_solve_displacements\n')
    f.write('wall_displacements_write_vtp %s\n' % (def_varwall_dir+'/walldisp.vtp'))
    
    f.write('write_numstart 0 %s\n' % (def_varwall_dir+'/numstart.dat'))
    f.write('write_geombc %s\n' % (def_varwall_dir + '/geombc.dat.1'))
    f.write('append_displacements %s\n' % (def_varwall_dir +'/restart.0.1'))
    f.write('append_varwallprop %s\n' % (def_varwall_dir +'/geombc.dat.1'))
    f.close()
    #
    #  Call pre-processor
    #
    
    print('Run cvpresolver')
    try:
        proc = subprocess.Popen([executable_names.PRESOLVER, (def_varwall_dir+'/variable_steady_cylinder.svpre')], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        (out, err) = proc.communicate()
        print(out)
    except:
        print("Error running presolver")
    timesteps = 200
    print("Number of timesteps: 200")
    
    #
    #  Run solver.
    #
    
    print('Run Solver.')
    
    directory = os.path.dirname(os.path.realpath(__file__))
    infp = open(directory+'/solver.inp.deformable', 'rU')
    
    outfp = open(def_varwall_dir+'/solver.inp', 'w+')
    
    for line in infp:
        line = line.replace('my_initial_time_increment', '0.0004')
        line = line.replace('my_number_of_time_steps', '200')
        line = line.replace('my_deformable_flag', 'True')
        line = line.replace('my_variablewall_flag', 'True')
        line = line.replace('my_rho_infinity', '0.0')
        line = line.replace('my_step_construction', "0 1 0 1 0 1 0 1 0 1  # this is the standard five iteration")
        if (pc.selected_LS=='leslib'):
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
        
    fp =open(def_steady_dir + '/solver.log','w+')
    fp.write('Start running solver...')
    fp.close()
    
    try:
        #cmd = 'cd'+' '+def_varwall_dir+ ' && '+ executable_names.SOLVER+ (' '+def_varwall_dir+'/solver.inp')+' >> '+(def_varwall_dir+'/solver.log')
        cmd = 'cd'+' '+'"'+def_varwall_dir+'"'+' && '+'"'+executable_names.SOLVER+'"'+' '+'"'+def_varwall_dir+'/solver.inp'+'"'
        print(cmd)
        os.system(cmd)
    except:
        print("Error running solver")
    
    endstep=0
    fp =open(def_varwall_sim_dir+'/numstart.dat','rU')
    last = fp.readline()
    fp.close()
    print("Total number of timesteps finished: " + last.replace(' ',''))
    endstep = int(last.replace(' ',''))
    ##
    ##
    ##  Create ParaView files
    ##
    print("Reduce restart files.")
    #
    try:
        #proc = subprocess.Popen([executable_names.POSTSOLVER, '-indir', def_varwall_sim_dir, '-outdir',def_varwall_dir,'-sn',str(endstep), '-ph', '-td', '-sol', '-newsn', '0'], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        cmd = 'cd'+' '+'"'+fullrundir+'"'+' && '+'"'+executable_names.POSTSOLVER+'"' + ' -indir ' + '"'+ def_varwall_sim_dir +'"'+ ' -outdir '+'"'+ def_varwall_dir +'"'+ ' -sn '+ str(endstep) + ' -ph '+ ' -td ' + ' -sol ' + ' -newsn ' + '0' 
        print(cmd)
        os.system(cmd)
    except:
        print("Error running postsolver")
        
    try:
        #proc = subprocess.Popen([executable_names.POSTSOLVER, '-indir', def_varwall_sim_dir, '-outdir',def_varwall_dir,'-start','0', '-stop',str(timesteps),'-incr','25','-sim_units_mm','-vtkcombo','-vtu','cylinder_results.vtu','-vtp','cylinder_results.vtp'], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        cmd = 'cd'+' '+'"'+fullrundir+'"'+' && '+'"'+executable_names.POSTSOLVER+'"' + ' -indir ' + '"'+ def_varwall_sim_dir +'"'+ ' -outdir '+'"'+ def_varwall_dir +'"'+ ' -start '+ '0' + ' -stop '+ str(timesteps) + ' -incr ' + '25' + ' -sim_units_mm ' + ' -vtkcombo ' + ' -vtu ' + 'cylinder_results.vtu' + ' -vtp ' + 'cylinder_results.vtp'
        print(cmd)
        os.system(cmd)
    except:
        print("Error running postsolver")
        
###
###
###    
###   DEFORMABLE PULSATILE CASE
###
###
###

copyfile(def_steady_dir+'/restart.0.0',def_pulse_dir + "/restart.0.1")
copyfile(def_steady_dir+'/geombc.dat.1',def_pulse_dir + "/geombc.dat.1")

timesteps = 2750
print("Number of timesteps: 2750")
    
#
#  Run solver.
#
    
print('Run Solver.')

fp = open(def_pulse_dir+'/numstart.dat','w')
fp.write('0')
fp.close()

directory = os.path.dirname(os.path.realpath(__file__))
infp = open(directory+'/solver.inp.deformable', 'rU')

outfp = open(def_pulse_dir+'/solver.inp', 'w+')

for line in infp:
    line = line.replace('my_initial_time_increment', '0.0004')
    line = line.replace('my_number_of_time_steps', '2750')
    line = line.replace('my_deformable_flag', 'True')
    line = line.replace('my_rho_infinity', '0.0')
    line = line.replace('my_step_construction', "0 1 0 1 0 1 0 1   # this is the standard four iteration")
    if (pc.selected_LS=='leslib'):
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
    
fp =open(def_pulse_dir + '/solver.log','w+')
fp.write('Start running solver...')
fp.close()

try:
    #cmd = 'cd'+' '+def_pulse_dir+ ' && '+ executable_names.SOLVER+ (' '+def_pulse_dir+'/solver.inp')+' >> '+(def_pulse_dir+'/solver.log')
    cmd = 'cd'+' '+'"'+def_pulse_dir+'"'+' && '+'"'+executable_names.SOLVER+'"'+' '+'"'+def_pulse_dir+'/solver.inp'+'"'
    print(cmd)
    os.system(cmd)
except:
    print("Error running solver")

endstep=0
fp =open(def_pulse_sim_dir+'/numstart.dat','rU')
last = fp.readline()
fp.close()
print("Total number of timesteps finished: " + last.replace(' ',''))
endstep = int(last.replace(' ',''))
##
##
##  Create ParaView files
##
print("Reduce restart files.")
#
try:
    #proc = subprocess.Popen([executable_names.POSTSOLVER, '-indir', def_pulse_sim_dir, '-outdir',def_pulse_dir,'-sn',str(endstep), '-ph', '-td', '-sol', '-newsn', '0'], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    cmd = 'cd'+' '+'"'+fullrundir+'"'+' && '+'"'+executable_names.POSTSOLVER+'"' + ' -indir ' + '"'+ def_pulse_sim_dir +'"'+ ' -outdir '+'"'+ def_pulse_dir +'"'+ ' -sn '+ str(endstep) + ' -ph '+ ' -td ' + ' -sol ' + ' -newsn ' + '0' 
    print(cmd)
    os.system(cmd)
except:
    print("Error running postsolver")
    
try:
    #proc = subprocess.Popen([executable_names.POSTSOLVER, '-indir', def_pulse_sim_dir, '-outdir',def_pulse_dir,'-start','0', '-stop',str(timesteps),'-incr','250','-sim_units_mm','-vtkcombo','-vtu','cylinder_results.vtu','-vtp','cylinder_results.vtp'], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    cmd = 'cd'+' '+'"'+fullrundir+'"'+' && '+'"'+executable_names.POSTSOLVER+'"' + ' -indir ' + '"'+ def_pulse_sim_dir +'"'+ ' -outdir '+'"'+ def_pulse_dir +'"'+ ' -start '+ '0' + ' -stop '+ str(timesteps) + ' -incr ' + '250' + ' -sim_units_mm ' + ' -vtkcombo ' + ' -vtu ' + 'cylinder_results.vtu' + ' -vtp ' + 'cylinder_results.vtp'
    print(cmd)
    os.system(cmd)
except:
    print("Error running postsolver")
#
##  compare results
##
#
#source ../generic/pulsatile_cylinder_compare_with_analytic_generic.tcl

