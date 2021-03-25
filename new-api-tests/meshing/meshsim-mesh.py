'''Test MeshSim interface.
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

try:
    sys.path.insert(1, str(parent_path / 'graphics'))
    import graphics as gr
except:
    print("Can't find the new-api-tests/graphics package.")

## Create a MeshSim mesher.
#
mesher = sv.meshing.MeshSim()
#mesher = sv.meshing.create_mesher(sv.meshing.Kernel.MESHSIM)

## Load the aorta iliac model.
#
file_name = str(data_path / 'meshing' / 'aorta-iliac.xmt_txt') 
mesher.load_model(file_name)

## Mesh face info:  
#
face_info = mesher.get_model_face_info()
print("Mesh face info: ")
for key in face_info:
    print("  {0:s}:  {1:s}".format(key, str(face_info[key])))

## Create options object.
#
global_edge_size = { 'edge_size':0.4, 'absolute':True }
options = sv.meshing.MeshSimOptions(global_edge_size=global_edge_size, surface_mesh_flag=True, volume_mesh_flag=True)
print(str(type(options)))

## Set local (face) edge size.
#
#options.local_edge_size =  [ {'face_id':63, 'edge_size':0.1, 'absolute':True } ]
options.local_edge_size =  [ {'face_id':'wall_aorta', 'edge_size':0.1, 'absolute':True } ]

#options.local_edge_size =  [ {'face_id':'wall_right_iliac', 'edge_size':1.0, 'absolute':True } ]

#options.local_edge_size.append( {'face_id':2, 'edge_size':2.0, 'absolute':True } )

## Generate the mesh. 
#
mesher.generate_mesh(options)

#mesher.write_mesh(file_name='aorta-iliac-mesh.vtu')

## Show the mesh.
#
show_mesh = True
if show_mesh:
    win_width = 500
    win_height = 500
    renderer, renderer_window = gr.init_graphics(win_width, win_height)

    #mesh_polydata = gr.convert_ug_to_polydata(mesh)
    mesh_surface = mesher.get_surface()
    #gr.add_geometry(renderer, mesh_surface, color=[1.0, 1.0, 1.0], wire=True, edges=True)
    gr.add_geometry(renderer, mesh_surface, color=[1.0, 1.0, 1.0], wire=False, edges=True)

    #mesh_model_polydata = mesher.get_model_polydata()
    #gr.add_geometry(renderer, mesh_model_polydata, color=[0.0, 1.0, 1.0], wire=True, edges=True)

    #face1_polydata = mesher.get_face_polydata(1)
    #gr.add_geometry(renderer, face1_polydata, color=[1.0, 0.0, 0.0], wire=False, edges=True)

    #face2_polydata = mesher.get_face_polydata(2)
    #gr.add_geometry(renderer, face2_polydata, color=[0.0, 1.0, 0.0], wire=False, edges=True)

    #face3_polydata = mesher.get_face_polydata(3)
    #gr.add_geometry(renderer, face3_polydata, color=[0.0, 0.0, 1.0], wire=False, edges=True)

    gr.display(renderer_window)

