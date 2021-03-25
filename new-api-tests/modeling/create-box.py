'''Test creating a box.
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

# Create a modeler.
oc_modeler = sv.modeling.Modeler(sv.modeling.Kernel.OPENCASCADE)
modeler = sv.modeling.Modeler(sv.modeling.Kernel.POLYDATA)
print("Modeler type: " + str(type(modeler)))
print("  kernel: " + modeler.kernel)
print("OC Modeler type: " + str(oc_modeler))
print("  kernel: " + oc_modeler.kernel)

## Create a box.
print("Create a box ...")
center = [0.0, 0.0, 0.0]
width = 2.0 
length = 4.0 
height = 6.0
box = modeler.box(center, width=width, length=length, height=height)
print("  Box type: " + str(type(box)))
box_pd = box.get_polydata()
print("  Box: num nodes: {0:d}".format(box_pd.GetNumberOfPoints()))
#
oc_box = oc_modeler.box(center, width=width, length=length, height=height)
print("  OC Box type: " + str(type(oc_box)))
oc_box_pd = oc_box.get_polydata()
print("  OC Box: num nodes: {0:d}".format(oc_box_pd.GetNumberOfPoints()))

## Create renderer and graphics window.
win_width = 500
win_height = 500
renderer, renderer_window = gr.init_graphics(win_width, win_height)

## Add model polydata.
gr.add_geometry(renderer, box_pd, color=[0.0, 1.0, 0.0], wire=True, edges=False)
gr.add_geometry(renderer, oc_box_pd, color=[1.0, 0.0, 0.0], wire=True, edges=False)

## Add a sphere.
gr.add_sphere(renderer, center=center, radius=0.1, color=[1.0, 1.0, 1.0], wire=True)

pt1 = center
pt2 = [ center[0]+width/2.0, center[1], center[2] ] 
gr.add_line(renderer, pt1, pt2, color=[0.5, 0.0, 0.0], width=4)

pt1 = center
pt2 = [ center[0], center[1]+height/2, center[2] ] 
gr.add_line(renderer, pt1, pt2, color=[0.0, 0.5, 0.0], width=4)

pt1 = center
pt2 = [ center[0], center[1], center[2]+length/2.0 ] 
gr.add_line(renderer, pt1, pt2, color=[0.0, 0.0, 0.5], width=4)

# Display window.
gr.display(renderer_window)



