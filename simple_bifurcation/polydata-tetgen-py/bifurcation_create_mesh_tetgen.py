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
try:
    import pyRepository
except:
    from __init__ import *
import mesh_utils
def bifurcation_create_mesh_TetGen (solidfn,dstdir,bifurcation_mesh_option):

  #
  #  Mesh the solid
  #

  print ("Creating mesh.")

  # create meshsim style script file
  fp= open(dstdir+'/bifurcation.tgs','w+')
  fp.write("msinit\n")
  fp.write("logon %s \n" % (dstdir +'/bifurcation.logfile'))
  fp.write("loadModel %s\n" % solidfn)
  fp.write("setSolidModel\n")
  fp.write("newMesh\n")
  fp.write("option surface 1\n")
  fp.write("option volume 1\n")
  if bifurcation_mesh_option == 'Coarse Isotropic Mesh':
      fp.write("option GlobalEdgeSize 1.2\n")
      fp.write("wallFaces wall\n")
  elif (bifurcation_mesh_option == 'Refined Mesh'):
      fp.write("option GlobalEdgeSize 1.2\n")
      fp.write("wallFaces wall\n")
      fp.write("sphereRefinement 0.5 10.0 16.0 0.0 -95.0\n")
  elif (bifurcation_mesh_option == 'Dense Mesh'):
      fp.write("option GlobalEdgeSize 0.75\n")
      fp.write("wallFaces wall\n")
  fp.write("option QualityRatio 1.4\n")
  fp.write("option NoBisect 1\n")
  fp.write("generateMesh\n")
  fp.write("writeMesh %s vtu 0\n" % (dstdir + '/bifurcation.sms'))
  fp.write("deleteMesh\n")
  fp.write("deleteModel\n")
  fp.write("logoff\n")
  fp.close()

  try:
      pyRepository.repos_delete("mymesh")
  except:
      pass
      
  mesh_utils.mesh_readTGS(dstdir+'/bifurcation.tgs', 'mymesh')

  print ("Writing out mesh surfaces.")
  os.mkdir(dstdir+'/mesh-complete')
  os.mkdir(dstdir+'/mesh-complete/mesh-surfaces')

  mesh_utils.mesh_writeCompleteMesh('mymesh','bifurcation','bifurcation',dstdir+'/mesh-complete')
