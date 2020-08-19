'''Test TetGen options class.
'''
import sv
import vtk

## Set meshing options.
#
print("Set meshing options ... ")
options = sv.meshing.TetGenOptions(global_edge_size=0.1, surface_mesh_flag=True, volume_mesh_flag=True)
print("Options type {0:s} ".format(str(type(options))))

#------------------ 
# global_edge_size
#------------------ 
#
#options.global_edge_size = "a"
#options.global_edge_size = 0.5

#----------
# add_hole
#----------
# [TODO:DaveP] [I'm not sure what this does.
#
#options.add_hole = 1.0
#options.add_hole = ["a", 2.0, 3.0]
#options.add_hole = [1.0, 2.0]
#options.add_hole = [1.0, 2.0, 3.0]
#print("options.add_hole: " + str(options.add_hole))

#-------------------
# surface_mesh_flag
#-------------------
#
#options.surface_mesh_flag = False
#print("options.surface_mesh_flag: " + str(options.surface_mesh_flag))

#options.quiet = True 
#print("options.quiet: " + str(options.quiet))

#-----------------
# Local edge size 
#-----------------
# options.local_edge_size is a list of {'face_id': int, 'edge_size': float}.
#
values = []
values.append( {'face_id': 1, 'edge_size': 0.1} )
#options.local_edge_size = values 
#options.local_edge_size.append( options.LocalEdgeSize(face_id=2, edge_size=0.2) )

#options.local_edge_size.append( {'face_id': 1, 'edge_size': 0.1} )

#----------------------------
# Radius meshing centerlines 
#----------------------------
if False:
    centerlines_file = "../data/meshing/demo-centerlines.vtp"
    reader = vtk.vtkXMLPolyDataReader()
    reader.SetFileName(centerlines_file)
    reader.Update()
    centerlines = reader.GetOutput()
    options.radius_meshing_centerlines = centerlines 

#-------------------
# Radius meshing on 
#-------------------
#options.radius_meshing_on = True
# Error checking.
#options.radius_meshing_on = 1

#----------------------
# Radius meshing scale 
#----------------------
#options.radius_meshing_scale = 0.4 
# Error checking.
#options.radius_meshing_scale = -0.4 
#options.radius_meshing_scale = "-0.4 "

#-----------------------
# Set sphere refinement 
#-----------------------
'''
if False:
    values = []
    values.append( { 'edge_size':0.1, 'radius':3.74711,  'center':[0.496379, 0.752667, 1.794] } )
    values.append( { 'edge_size':0.2, 'radius':2.0,  'center':[2.0, 2.7, 2.4] })
    values.append( { 'edge_size':0.3, 'radius':3.0,  'center':[3.0, 3.7, 3.4] })
    values.append( { 'edge_size':0.4, 'radius':4.0,  'center':[4.0, 4.7, 4.4] })
    values.append( { 'edge_size':0.5, 'radius':5.0,  'center':[5.0, 5.7, 5.5] })
    options.sphere_refinement = values
else:
    options.sphere_refinement.append( { 'edge_size':0.2, 'radius':2.0,  'center':[2.0, 2.7, 2.4] })
    options.sphere_refinement.append( { 'edge_size':0.3, 'radius':3.0,  'center':[3.0, 3.7, 3.4] })
    options.sphere_refinement.append( { 'edge_size':0.4, 'radius':4.0,  'center':[4.0, 4.7, 4.4] })

    value = options.SphereRefinement(edge_size=0.3, radius=3.74711, center=[3.496379, 3.752667, 3.794])
    print(str(value))
    options.sphere_refinement.append( value )

for value in options.sphere_refinement:
    print("value: " + str(value))

options.sphere_refinement_on = True
'''

#--------------------
# Set boundary layer 
#---------------------
options.boundary_layer_inside = False 

#-------------------
# print all options
#-------------------
print("Options values: ")
[ print("  {0:s}:{1:s}".format(key,str(value))) for (key, value) in sorted(options.get_values().items()) ]
#help(options)

#--------------------
# Set mesher options
#--------------------
#
#mesher.set_options(options)


