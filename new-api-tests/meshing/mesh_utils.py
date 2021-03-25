'''Utilities. 
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

def setup_mesher(kernel):

    if kernel == sv.meshing.Kernel.TETGEN:
        mesher = sv.meshing.TetGen()
        # Load a model.
        file_name = str(data_path / 'meshing' / 'cylinder-model.vtp')
        print("[setup_mesher] Model file name: {0:s}".format(file_name))
        mesher.load_model(file_name)

    return mesher

