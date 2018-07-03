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
#  user defined list of res files to compare
#
import pulsatile_cylinder as pc
import pulsatile_cylinder_generic2 as gen
import math
try:
    import pyMath
    import pyRepository
    import pyGeom
except:
    from __init__ import *
import vtk


timesteps = int(pc.timesteps)
timesteps = 16
tlist = [0.025, 0.075,0.125,0.175]
toverTlist = [0.125,0.375,0.625,0.875]

simstepnumlist = [int(timesteps*(1 + tlist[0]/0.2)) + 1,\
                  int(timesteps*(1 + tlist[1]/0.2)) + 1,\
                  int(timesteps*(1 + tlist[2]/0.2)) + 1,\
                  int(timesteps*(1 + tlist[3]/0.2)) + 1]
         
fullrundir = gen.fullrundir
resfn = fullrundir + '/cylinder_results.vtu'

viscosity = 0.004
density = 0.00106
T = 0.2
Vbar = 135
radius = 2.0
omega = 2.0*math.pi/T

pts = []
for i in range(0,256):
    dt = T/255.0
    t = float(i)*dt
    Vmean = Vbar*(1.0+math.sin(2*math.pi*t/T))
    area = math.pi*radius*radius
    pts.append([t, -Vmean*area])
    
terms = pyMath.math_FFT(pts, 2,256)
try:
    pyRepository.repos_delete('outflow')
except:
    pass
    
import os
import stat
os.chmod(fullrundir+'/mesh-complete/mesh-surfaces', 0o777)
pyRepository.repos_readXMLPolyData('outflow',fullrundir+'/mesh-complete/mesh-surfaces/outlet.vtp')
numPts = pyGeom.geom_numPts('outflow')
outflowObj = pyRepository.repos_exportToVtk('outflow')
outflowScalars = outflowObj.GetPointData().GetScalars()

print ("Reading simulation results: " + resfn)
resReader = vtk.vtkXMLUnstructuredGridReader()
resReader.SetFileName(resfn)
resReader.Update()

# now calculate flow rate for each time point
countem = 0

for stepnum in simstepnumlist:
    time = tlist[countem]
    countem = countem+1
    myVectors = vtk.vtkFloatArray()
    myVectors.SetNumberOfComponents(3)
    myVectors.Allocate(1000,1000)
    
    pointData = resReader.GetOutput().GetPointData()
    nm = '00000'
    nm = list(nm)
    stpnum = list(str(stepnum))
    nm[-len(stpnum):]=stpnum[-len(stpnum):]
    nm = ''.join(nm)
    objVectors = pointData.GetArray('velocity_'+nm)
    
    for i in range(0,int(numPts)):
        node = outflowScalars.GetValue(i)
        # nodes in vtk start at 0, so subtract 1 off
        node = node-1
        vec = objVectors.GetTuple3(node)
        myVectors.InsertNextTuple3(vec[0],vec[1],vec[2])
        
    outflowObj.GetPointData().SetVectors(myVectors)
    try:
        pyRepository.repos_delete('outflowTmp')
    except:
        pass
    pyRepository.repos_importVtkPd(outflowObj,'outflowTmp')
    
    fp = open(fullrundir+'/profiles_for_'+str(time),'w+')
    fp.write("radius\tr/R\tanalytic\t")
    fp.write("%d\t\n"% stepnum)
    
    analytic = []
    result = []
    xR = []
    for j in range(-20,21):
        r = float(j)/10.
        fp.write("%.4f\t%.4f\t"%(r,r/radius))
        womersley = pyMath.math_computeWomersley(terms,time,viscosity,omega,density,radius,r)
        if abs(r)!=2:
            tmpvec = pyGeom.geom_interpolateVector('outflowTmp',[r,0.,0.])
        else:
            tmpvec = [0]
        
        if len(tmpvec)==3:
            fp.write("%.4f\t%.4f\t\n"%(womersley,tmpvec[2]))
        else:
            fp.write("%.4f\t\t\n"%(womersley))
            
    fp.close()


