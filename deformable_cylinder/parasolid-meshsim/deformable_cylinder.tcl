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
set gOptions(meshing_solid_kernel) Parasolid
set gOptions(meshing_kernel) MeshSim
solid_setKernel -name Parasolid
mesh_setKernel -name MeshSim

set num_procs ""
set selected_LS ""
set run_varwall ""

# shared functions
source ../../common/executable_names.tcl

# custom functions
source deformable_cylinder_specific.tcl

# run example
source ../generic/deformable_cylinder_generic.tcl

