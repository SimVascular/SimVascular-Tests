#
#   Copyright (c) 2009-2012 Open Source Medical Software Corporation
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

# sometimes we have to invert the normal to the inflow surface
global guiABC
set guiABC(invert_face_normal) 0

# having lots of problems with the line intersection with
# the edge boundary to calcuate the ratio map, so hack it here
source geom_createRatioMap.tcl

# shared functions
source ../../common/executable_names.tcl
source ../generic/steady_cylinder_create_bc_files_generic.tcl

# custom functions
source cylinder_create_model_polydata.tcl
source steady_cylinder_create_mesh_tetgen.tcl

# run example
source ../generic/steady_cylinder_generic.tcl
