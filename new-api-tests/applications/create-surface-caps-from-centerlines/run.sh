#!/bin/bash

svp='/Users/parkerda/software/ktbolt/SimVascular/build/SimVascular-build/sv --python -- '

file=H-009_M6__28_surfacemesh.vtk 

file=H-015_M6__17_surfacemesh.vtk 

file=H-030_J0__27_surfacemesh.vtk

file=H-030_M6__17_surfacemesh.vtk 

file=H-019_J0__11_surfacemesh.vtk 

file=H-053_J0__06_surfacemesh.vtk 

$svp create_surface_caps.py --surface-file=./data/${file} --clip-distance=0.2  --clip-width-scale=1.1

