'''
Test MeshSim options. 

**** This is no loner used. ****
'''
import sv
import vtk

## Create a MeshSim mesher.
'''
mesher = sv.meshing.create_mesher(sv.meshing.Kernel.MESHSIM)
mesher.set_solid_modeler_kernel(sv.solid.Kernel.PARASOLID)
mesher.load_model("m1.xmt_txt")
'''

## Set meshing options.
#
print("Create meshing options ... ")
global_edge_size = {'edge_size':0.1, 'absolute':True}
options = sv.meshing.MeshSimOptions(global_edge_size=global_edge_size, surface_mesh_flag=True, volume_mesh_flag=True)

#------------------
# global_curvature 
#------------------
if False:
    print("Set global curvature ... ")
    options.global_curvature = {'curvature':1.0, 'absolute':True } 

    ## Check error handling.
    #options.global_curvature = {'curvature':'a', 'absolute':True }

#-----------------
# local_curvature 
#-----------------
if True:
    print("Set local curvature ... ")
    
    ## Must use set_local_curvature() and add_local_curvature() methods.
    #
    options.local_curvature = [ {'face_id':1, 'curvature':1.0, 'absolute':True } ]
    #options.set_local_curvature(face_id=1, curvature=1.0, absolute=True)
    options.add_local_curvature(face_id=2, curvature=2.0, absolute=True)

    ## Can't use Python list methods.
    #
    #options.local_curvature = [ {'face_id':1, 'curvature':1.0, 'absolute':True } ]
    #options.local_curvature.append( {'face_id':3, 'curvature':3.0, 'absolute':True } )
    #print("  options.local_curvature: " + str(options.local_curvature))

    ## Check error handling.
    #
    #options.local_curvature = {'face_id':1, 'curvature':1.0, 'absolute':True }
    #options.local_curvature = [ {'face_id':1, 'edge':1.0, 'absolute':True } ]
    #options.local_curvature = [ {'edge':1.0, 'absolute':True } ]

#-----------------
# local_edge_size 
#-----------------
#
if False:
    print("Set local edge size ... ")
    #local_edge_size = {'face_id':1, 'edge_size':1.0}
    #options.local_edge_size = [ {'face_id':1, 'edge_size':1.0}, {'face_id':2, 'edge_size':2.0} ]
    #options.local_edge_size.append( {'face_id':3, 'edge_size':3.0} )
    #options.local_edge_size.clear()

    # use set and add to build list.
    options.set_local_edge_size(face_id=1, edge_size=1.0)
    options.add_local_edge_size(face_id=2, edge_size=2.0)
    #options.add_local_edge_size(face_id='a', edge_size=2.0)
    #options.add_local_edge_size(ace_id=1, edge_size=2.0)

    # These errors won't be found until we set options.
    options.local_edge_size.append( {'ace_id':3, 'edge_size':3.0} )

#-------------------
# surface_mesh_flag
#-------------------
#
#options.surface_mesh_flag = False
#print("options.surface_mesh_flag: " + str(options.surface_mesh_flag))

#-------------------
# print all options
#-------------------
#
print("Options values ... ")
[ print("  {0:s}:{1:s}".format(key,str(value))) for (key, value) in sorted(options.get_values().items()) ]

'''
opt_values = options.get_values()
local_curvature = opt_values['local_curvature']
print(type(local_curvature))
for i,item in enumerate(local_curvature):
    print(">>>> " + str(i))
    print(type(item))
    print(item)
'''

#help(options)

#--------------------
# Set mesher options
#--------------------
#
#mesher.set_options(options)


