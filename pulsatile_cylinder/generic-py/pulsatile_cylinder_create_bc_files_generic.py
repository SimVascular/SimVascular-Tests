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
import os
import math
import pyMath
def pulsatile_cylinder_create_flow_files_generic (dstdir):

  # Write sinusodial flowrate
  print "Generating sinusodial volumetric flow waveform."
  T = 0.2
  Vbar =135
  radius = 2

  # calculate FFT terms
  pts =[]
  os.mkdir(dstdir+'/flow-files')
  fp= open(dstdir+'/flow-files/inflow.flow','w+')
  fp.write("#  Time (sec)   Flow (cc/sec)\n")
  for i in range(0,256):
      dt = T/255.0
      t = i*dt
      Vmean = Vbar*(1.0+math.sin(2*math.pi*t/T))
      area = math.pi*radius*radius
      pts.append([t, Vmean*area])
      fp.write("%f %f\n"% (t, Vmean*area))
  fp.close()
  
  print "Calculate analytic profile for outlet. (not done!!)"
  terms = pyMath.math_FFT(pts, 256,2)
    
  return terms
