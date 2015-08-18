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

solid_setKernel -name PolyData
mesh_setKernel -name TetGen
set gOptions(meshing_kernel) TetGen
set gOptions(meshing_solid_kernel) PolyData

set num_procs ""
set selected_LS ""
set pulsatile_mesh_option ""
set timesteps ""

# shared functions
source ../../common/executable_names.tcl

# custom functions
source cylinder_create_model_polydata.tcl
source pulsatile_cylinder_create_mesh_tetgen.tcl

# run example
source ../generic/pulsatile_cylinder_generic2.tcl
