'''Test getting the mesh surface.
'''
import sv
import sys
import vtk
sys.path.insert(1, '../graphics/')
import graphics as gr
from mesh_utils import setup_mesher

## Create a mesher and load a model.
mesher = setup_mesher(sv.meshing.Kernel.TETGEN)

## Load a mesh. 
mdir = "../data/meshing/"
mesher.load_mesh(volume_file=mdir+'cylinder-mesh.vtu', surface_file=mdir+'cylinder-mesh.vtp')

## Get the model polydata.
#
mesh_surface = mesher.get_surface()

## Create renderer and graphics window.
win_width = 500
win_height = 500
renderer, renderer_window = gr.init_graphics(win_width, win_height)

gr.add_geometry(renderer, mesh_surface, color=[0.0, 1.0, 1.0], wire=True, edges=True)

gr.display(renderer_window)


