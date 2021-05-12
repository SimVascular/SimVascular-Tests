'''Test the ROM simulation class. 

   Generate a reduced-order modeling (ROM) simulation input file.

   Use the centerlines and faces from the Demo project.
'''
import os
from pathlib import Path
import sv
import sys
import vtk

## Set some directory paths. 
script_path = Path(os.path.realpath(__file__)).parent
parent_path = Path(os.path.realpath(__file__)).parent.parent
data_path = parent_path / 'data'

## Create a ROM simulation.
input_dir = str(script_path / 'input') + os.sep
rom_simulation = sv.simulation.ROM() 

## Create ROM simulation parameters.
params = sv.simulation.ROMParameters()

## Mesh parameters.
mesh_params = params.MeshParameters()

## Model parameters.
model_params = params.ModelParameters()
model_params.name = "demo"
model_params.inlet_face_names = ['cap_aorta' ] 
model_params.outlet_face_names = ['cap_right_iliac', 'cap_aorta_2' ] 
model_params.centerlines_file_name = input_dir + 'centerlines.vtp' 

## Fluid properties.
fluid_props = params.FluidProperties()

## Set wall properties.
#
print("Set wall properties ...")
material = params.WallProperties.OlufsenMaterial()
print("Material model: {0:s}".format(str(material)))

## Set boundary conditions.
#
bcs = params.BoundaryConditions()
#bcs.add_resistance(face_name='outlet', resistance=1333)
bcs.add_velocities(face_name='inlet', file_name=input_dir+'inflow.flow')
bcs.add_rcr(face_name='cap_right_iliac', Rp=90.0, C=0.0008, Rd=1200)
bcs.add_rcr(face_name='cap_aorta_2', Rp=100.0, C=0.0004, Rd=1100)

## Set solution parameters. 
#
solution_params = params.Solution()
solution_params.time_step = 0.001
solution_params.num_time_steps = 1000

## Write a 1D solver input file.
#
output_dir = str(script_path / 'output')
rom_simulation.write_input_file(model_order=1, model=model_params, mesh=mesh_params, fluid=fluid_props, 
  material=material, boundary_conditions=bcs, solution=solution_params, directory=output_dir)

## Run a simulation.
#
#fluid_simulation.run(parameters=fluid_params, use_mpi=True, num_processes=4)


