#!/usr/bin/env python
"""This script is used to create an SV model from a closed segmentation surface. 

The 
"""
import argparse
import os
import sys

from centerlines import Centerlines
from surface import Surface
sys.path.insert(1, '../../graphics/')
import graphics as gr

def parse_args():
    '''Parse command-line arguments.
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument("--surface-file",  required=True, help="Input surface (.vtp or .vtk) file.")
    args = parser.parse_args()

    if len(sys.argv) == 1:
       parser.print_help()
       sys.exit(1)

    return args

def main():

    # Get command-line arguments.
    args = parse_args()

    ## Create renderer and graphics window.
    win_width = 500
    win_height = 500
    renderer, renderer_window = gr.init_graphics(win_width, win_height)

    ## Read in the segmentation surface.
    surface_file_name = args.surface_file 
    surface = Surface(gr, renderer_window, renderer)
    surface.read(surface_file_name)
    gr_geom = gr.add_geometry(renderer, surface.geometry, color=[0.8, 0.8, 8.0])
    gr_geom.GetProperty().SetOpacity(0.5)

    ## Create a Centerlines object used to clip the surface.
    centerlines = Centerlines()
    centerlines.graphics = gr
    centerlines.surface = surface
    centerlines.window = renderer_window 
    centerlines.renderer = renderer

    print("---------- Alphanumeric Keys ----------")
    print("c - Compute centerlines.")
    print("m - Create a model from the surface and centerlines.")
    print("q - Quit")
    print("s - Select a centerline source point.")
    print("t - Select a centerline target point.")

    ## Create a mouse interactor for selecting centerline points.
    picking_keys = ['s', 't']
    event_table = {
        'c': surface.compute_centerlines,
        'm': (centerlines.create_model, surface),
        's': surface.add_centerlines_source_node,
        't': surface.add_centerlines_target_node
    }
    interactor = gr.init_picking(renderer_window, renderer, surface.geometry, picking_keys, event_table)

    ## Display window.
    interactor.Start()

if __name__ == '__main__':
    main()

