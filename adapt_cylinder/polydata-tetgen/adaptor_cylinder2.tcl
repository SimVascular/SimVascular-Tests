
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

