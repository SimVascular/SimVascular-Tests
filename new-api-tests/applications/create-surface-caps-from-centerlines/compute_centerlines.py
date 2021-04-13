#!/usr/bin/env python

'''This script computes centerlines for a surface.

   Centerline source and target points are selected interactively. The first point selected is the source,
   the remaining points are the targets.
'''
import sys
import sv
import os
import vtk
from surface import Surface

sys.path.insert(1, '../../graphics/')
import graphics as gr

def compute_centerlines(surface, node_ids):
    print('----- compute_centerlines -----')
    print('selected_node_ids: ' + str(node_ids)) 
    inlet_ids = node_ids[0:1]
    outlet_ids = node_ids[1:] 
    centerlines_polydata = sv.vmtk.centerlines(surface, inlet_ids, outlet_ids)
    file_name = "centerlines-result.vtp"
    writer = vtk.vtkXMLPolyDataWriter()
    writer.SetFileName(file_name)
    writer.SetInputData(centerlines_polydata)
    writer.Update()
    writer.Write()

if __name__ == '__main__':
    surface_file_name = sys.argv[1]

    ## Create renderer and graphics window.
    win_width = 500
    win_height = 500
    renderer, renderer_window = gr.init_graphics(win_width, win_height)

    ## Read in surface.
    surface = Surface()
    surface.read(surface_file_name)
    gr_geom = gr.add_geometry(renderer, surface.geometry, color=[0.8, 0.8, 8.0])

    ## Display window.
    interactor = gr.init_picking(renderer_window, renderer, surface.geometry, {'c':compute_centerlines})
    interactor.Start()


