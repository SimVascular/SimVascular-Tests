#
#   Copyright (c) 2009-2012 Open Source Medical Software Corporation
#   All rights reserved.  
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
set bifurcation_mesh_option ""
set use_resistance ""
set timesteps ""
set num_periods ""

# shared functions
source ../../common/executable_names.tcl

# custom functions
source bifurcation_create_model_polydata.tcl
source bifurcation_create_mesh_tetgen.tcl

# run example
source ../generic/bifurcation_generic2.tcl
