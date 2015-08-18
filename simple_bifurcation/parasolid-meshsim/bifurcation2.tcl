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

solid_setKernel -name Parasolid
mesh_setKernel -name MeshSim
set gOptions(meshing_kernel) MeshSim
set gOptions(meshing_solid_kernel) Parasolid

set num_procs ""
set selected_LS ""
set bifurcation_mesh_option ""
set use_resistance ""
set timesteps ""
set num_periods ""

# shared functions
source ../../common/executable_names.tcl

# custom functions
source bifurcation_create_model_parasolid.tcl
source bifurcation_create_mesh_meshsim.tcl

# run example
source ../generic/bifurcation_generic2.tcl
