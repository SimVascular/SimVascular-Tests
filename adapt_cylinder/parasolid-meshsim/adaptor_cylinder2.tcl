
global gOptions
set gOptions(meshing_solid_kernel) Parasolid
set gOptions(meshing_kernel) MeshSim
solid_setKernel -name Parasolid
mesh_setKernel -name MeshSim

set num_procs ""
set selected_LS ""

# shared functions
source ../../common/executable_names.tcl

# custom functions
source adaptor_cylinder_specific.tcl

# run example
source ../generic/adaptor_cylinder_generic.tcl

