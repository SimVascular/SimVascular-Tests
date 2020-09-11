import os, pwd
import sys
import sv
import vtk
sys.path.insert(1, '../../graphics/')
import graphics as gr

## Create renderer and graphics window.
win_width = 500
win_height = 500
renderer, renderer_window = gr.init_graphics(win_width, win_height)

model_name = 'outer'
model_name = 'inner'
modeler = sv.modeling.Modeler(sv.modeling.Kernel.POLYDATA)
model1 = modeler.read('aorta-'+model_name+'-model.vtp')
model2 = modeler.read('right_iliac-'+model_name+'-model.vtp')

## Perform a Boolean union.
vessel_union = modeler.union(model1, model2)
face_ids = vessel_union.compute_boundary_faces(angle=50.0)
face_ids = vessel_union.get_face_ids()
print("Vessel wall model face IDs: " + str(face_ids))
vessel_union_pd = vessel_union.get_polydata()
gr.add_geometry(renderer, vessel_union_pd, color=[1.0, 1.0, 1.0], wire=True)
file_format = "vtp"
vessel_union.write(file_name=model_name+"-union", format=file_format)

## Display window.
gr.display(renderer_window)

