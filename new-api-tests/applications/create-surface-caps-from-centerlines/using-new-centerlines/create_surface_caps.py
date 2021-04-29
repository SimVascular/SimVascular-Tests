#!/usr/bin/env python
"""This script caps a surface based on the new centerlines file format. 
"""
import argparse
import sys
import os
import logging

from centerlines import Centerlines
from surface import Surface
sys.path.insert(1, '../../../graphics/')
import graphics as gr

if __name__ == '__main__':
    surface_file_name = sys.argv[1]
    centerlines_file_name = None 
    if len(sys.argv) == 3:
        centerlines_file_name = sys.argv[2]

    ## Create renderer and graphics window.
    win_width = 500
    win_height = 500
    renderer, renderer_window = gr.init_graphics(win_width, win_height)

    ## Read in surface.
    surface = Surface()
    surface.read(surface_file_name)
    gr_geom = gr.add_geometry(renderer, surface.geometry, color=[0.8, 0.8, 8.0])
    gr_geom.GetProperty().SetOpacity(0.5)
    #interactor = gr.init_picking(renderer_window, renderer, surface.geometry)

    ## Read in centerlines.
    centerlines = Centerlines()
    centerlines.graphics = gr
    centerlines.renderer = renderer
    centerlines.surface = surface.geometry
    centerlines.read(centerlines_file_name)
    #gr.add_geometry(renderer, centerlines.geometry, color=[0.0, 0.8, 0.0], line_width=3)

    ## Show the branches extracted from the centerlines. 
    centerlines.show_branches()

    ## Clip the surfce ends. 
    clipped_surface = centerlines.remove_surface_ends()
    centerlines.write_clipped_surface(clipped_surface, "clipped_surface.vtp")

    ## Display window.
    gr.display(renderer_window)


