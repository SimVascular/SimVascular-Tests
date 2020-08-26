'''Test the Fluid simulation class. 
'''
import sv
import sys
import vtk
sys.path.insert(1, '../../graphics/')
import graphics as gr

## Create a fluid simulation.
fluid_simulation = sv.simulation.Fluid() 
#print("Simulation type: " + str(type(fluid_simulation)))

## Create  fluid simulation parameters.
#
fluid_params = sv.simulation.FluidParameters()
#print("fluid_params str: " + str(fluid_params))
#print("fluid_params type: " + str(type(fluid_params)))

## Set initial conditions.
#
ics = fluid_params.initial_conditions 
ics.pressure = 0.01
ics.velocity = [1.0, 1.0, 1.0]
print("Simulation ICs: {0:s}".format(str(ics)))

## Set boundary conditions.
#
bcs = fluid_params.boundary_conditions 
bcs.add_resistance(face_name='outlet', resistance=1333)
bcs.add_velocities(face_name='inlet', file_name='inflow.flow')

## Set wall properties conditions.
#
print(str(fluid_params.wall_properties))

## Set solution parameters. 
#
solution_params = fluid_params.solution 
solution_params.time_step = 0.001
solution_params.num_time_steps = 1000
solution_params.restart_write_frequency = 100

## Write a solver.in file.
#fluid_simulation.write_solver_input_file(parameters=fluid_params)

## Run a simulation.
#
#fluid_simulation.run(parameters=fluid_params, use_mpi=True, num_processes=4)


