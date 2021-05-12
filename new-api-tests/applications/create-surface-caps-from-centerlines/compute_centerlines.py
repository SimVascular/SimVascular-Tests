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

def compute_centerlines(surface, node_ids, file_prefix):
    print('----- compute_centerlines -----')
    print('selected_node_ids: ' + str(node_ids)) 
    inlet_ids = node_ids[0:1]
    outlet_ids = node_ids[1:] 
    centerlines_polydata = sv.vmtk.centerlines(surface, inlet_ids, outlet_ids)
    file_name = file_prefix+"-centerlines.vtp"
    writer = vtk.vtkXMLPolyDataWriter()
    writer.SetFileName(file_name)
    writer.SetInputData(centerlines_polydata)
    writer.Update()
    writer.Write()

def main():
    file_name = sys.argv[1]
    file_prefix, file_extension = os.path.splitext(file_name)

    ## Create renderer and graphics window.
    win_width = 500
    win_height = 500
    renderer, renderer_window = gr.init_graphics(win_width, win_height)

    ## Read in surface.
    surface = Surface()
    surface.read(file_name)
    model_polydata = surface.geometry
    gr_geom = gr.add_geometry(renderer, model_polydata, color=[0.8, 0.8, 8.0])
    print("Num nodes: {0:d}".format(model_polydata.GetNumberOfPoints()))
    print("Num faces: {0:d}".format(model_polydata.GetNumberOfCells()))

    ## Display window.
    interactor = gr.init_picking(renderer_window, renderer, surface.geometry, {'c': (compute_centerlines,file_prefix)})
    interactor.Start()

if __name__ == '__main__':
    main()

