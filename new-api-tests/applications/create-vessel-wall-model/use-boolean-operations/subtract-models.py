import os, pwd
import sys
import sv
import vtk
sys.path.insert(1, '../../../graphics/')
import graphics as gr

## Create renderer and graphics window.
win_width = 500
win_height = 500
renderer, renderer_window = gr.init_graphics(win_width, win_height)

modeler = sv.modeling.Modeler(sv.modeling.Kernel.POLYDATA)
inner_model = modeler.read('inner-union.vtp')
face_ids = inner_model.compute_boundary_faces(angle=50.0)

outer_model = modeler.read('outer-union.vtp')
face_ids = outer_model.compute_boundary_faces(angle=50.0)
print("Outer Model face IDs: " + str(face_ids))

## Perform a Boolean subtract.
vessel_wall = modeler.subtract(main=outer_model, subtract=inner_model)
face_ids = vessel_wall.compute_boundary_faces(angle=50.0)
face_ids = vessel_wall.get_face_ids()
print("Vessel wall model face IDs: " + str(face_ids))
vessel_wall_pd = vessel_wall.get_polydata()
file_format = "vtp"
vessel_wall.write(file_name="vessel-wall", format=file_format)

gr.add_geometry(renderer, vessel_wall_pd, color=[1.0, 1.0, 1.0], wire=True)

## Display window.
gr.display(renderer_window)

