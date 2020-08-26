'''Test setting MeshSim options using MeshSimOptions Python class.
'''
import sv
import sys

## Create options object.
#
global_edge_size = { 'edge_size':0.1, 'absolute':True }
options = sv.meshing.MeshSimOptions(global_edge_size=global_edge_size, surface_mesh_flag=True, volume_mesh_flag=True)
print(str(type(options)))

#------------------
# global_curvature 
#------------------
if False:
    print(" ")
    print("Set global curvature ... ")
    options.global_curvature = {'curvature':4.0, 'absolute':True }
    print("Global curvature: " + str(options.global_curvature))

#------------------
# global_edge_size 
#------------------
if False:
    print(" ")
    print("Set global edge size ... ")
    options.global_edge_size = {'edge_size':4.0, 'absolute':True } 
    print("Global edge size: " + str(options.global_edge_size))
    #
    # Test error conditions.
    #options.global_edge_size = {'edge_size':1, 'absolute':True } 
    #options.global_edge_size = {'edge_size':'a', 'absolute':True } 

#-----------------
# local_edge_size 
#-----------------
if False:
    print("Set local edge size ... ")
    options.local_edge_size =  [ {'face_id':1, 'edge_size':1.0, 'absolute':True } ]
    options.local_edge_size.append( {'face_id':2, 'edge_size':2.0, 'absolute':True } ) 
    # Test error conditions.
    options.local_edge_size =  {'face_id':1, 'edge_size':1.0, 'absolute':True }
    options.local_edge_size.append( {'face_id':2, 'edge_siz':2.0, 'absolute':True } ) 

#-----------------
# local_curvature 
#-----------------
if False:
    print("Set local curvature ... ")
    options.local_curvature =  [ {'face_id':1, 'curvature':1.0, 'absolute':True } ]
    options.local_curvature.append( {'face_id':2, 'curvature':2.0, 'absolute':True } )
    # Test error conditions.
    options.local_curvature.append( {'id':2, 'curvature':2.0, 'absolute':True } )

#--------------------
# local_min_curvature 
#--------------------
if True:
    print("Set local min curvature ... ")
    options.local_min_curvature =  [ {'face_id':1, 'min_curvature':1.0, 'absolute':True } ]
    options.local_min_curvature.append( {'face_id':2, 'min_curvature':2.0, 'absolute':True } )

#-------------------
# surface_mesh_flag
#-------------------
if False:
    print("Set surface mesh flag ... ")
    options.surface_mesh_flag = True 
    # Test error conditions.
    #options.surface_mesh_flag = 1 

#----------------------
# surface_optimization 
#----------------------
if True:
    print("Set surface optimization ... ")
    options.surface_optimization = 2
    # Test error conditions.
    #options.surface_optimization = -1

#------------------
# volume_mesh_flag
#------------------
if False:
    print("Set volume mesh flag ... ")
    options.volume_mesh_flag = True 
    # Test error conditions.

#----------------------
# volume_optimization 
#----------------------
if False:
    print("Set volume optimization ... ")
    options.volume_optimization = 4
    # Test error conditions.

#---------------
# print options 
#---------------
print("Options ... ")
values = options.get_values()
for k,v in values.items():
    print("{0:s}: {1:s}".format(k,str(v)))

c_options = sv.meshing.MeshSimOptions(global_edge_size=global_edge_size, surface_mesh_flag=True, volume_mesh_flag=True)
#c_options.parse_options(options)


