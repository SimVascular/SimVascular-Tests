'''Test TetGen get polydata.
'''
import sv
import sys
import vtk
sys.path.insert(1, '../graphics/')
import graphics as gr
from mesh_utils import setup_mesher

## Create a mesher and load a model.
mesher = setup_mesher(sv.meshing.Kernel.TETGEN)

## Get the model polydata.
#
mesh_model_polydata = mesher.get_model_polydata()

## Create renderer and graphics window.
win_width = 500
win_height = 500
renderer, renderer_window = gr.init_graphics(win_width, win_height)

gr.add_geometry(renderer, mesh_model_polydata, color=[0.0, 1.0, 1.0], wire=True, edges=True)

gr.display(renderer_window)


