#
#   Copyright (c) 2015 Stanford University
#   All rights reserved.  
#
#   Execute this file in SimVascular Console:
#   source steady-cylinder.tcl

#   Portions of the code Copyright (c) 2009-2012 Open Source Medical Software Corporation
#   All rights reserved.  
#
#  This script requires the following files:
#     solver.inp
#  and should be sourced interactively from SimVascular
#
#
solid_setKernel -name PolyData
mesh_setKernel -name TetGen
set gOptions(meshing_kernel) TetGen
set gOptions(meshing_solid_kernel) PolyData

set num_procs ""
set selected_LS ""


# shared functions
source ../../common/executable_names.tcl

# custom functions
source cylinder_create_model_polydata.tcl
source steady_cylinder_create_mesh_tetgen.tcl

# run example
source ../generic/steady_cylinder_generic2.tcl
