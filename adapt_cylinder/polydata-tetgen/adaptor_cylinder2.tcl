#
#   Copyright (c) 2015 Stanford University
#   All rights reserved.  
#
#   Portions of the code Copyright (c) 2009-2012 Open Source Medical Software Corporation
#
#  This script requires the following files:
#     solver.inp
#  and should be sourced interactively from SimVascular
#

global gOptions
set gOptions(meshing_solid_kernel) PolyData
set gOptions(meshing_kernel) TetGen
solid_setKernel -name PolyData
mesh_setKernel -name TetGen

set num_procs ""
set selected_LS ""

# shared functions
source ../../common/executable_names.tcl

# custom functions
source adaptor_cylinder_specific.tcl

# run example
source ../generic/adaptor_cylinder_generic.tcl

