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

modeler = sv.modeling.Modeler(sv.modeling.Kernel.POLYDATA)
inner_model = modeler.read('demo_aorta_inner.vtp')
#inner_model = modeler.read('aorta-inner.vtp')
face_ids = inner_model.compute_boundary_faces(angle=50.0)
print("Inner Model face IDs: " + str(face_ids))

outer_model = modeler.read('demo_aorta_outer.vtp')
#outer_model = modeler.read('aorta-outer.vtp')
face_ids = outer_model.compute_boundary_faces(angle=50.0)
print("Outer Model face IDs: " + str(face_ids))
#gr.add_geometry(renderer, outer_model.get_polydata(), color=[0.0, 0.8, 0.0], wire=False)

## Perform a Boolean subtract.
vessel_wall = modeler.subtract(main=outer_model, subtract=inner_model)
face_ids = vessel_wall.compute_boundary_faces(angle=50.0)
face_ids = vessel_wall.get_face_ids()
print("Vessel wall model face IDs: " + str(face_ids))
vessel_wall_pd = vessel_wall.get_polydata()
#gr.add_geometry(renderer, vessel_wall_pd, color=[1.0, 1.0, 1.0], wire=True)
file_format = "vtp"
vessel_wall.write(file_name="vessel_wall", format=file_format)

## Get polydata.
face1_polydata = vessel_wall.get_face_polydata(face_id=1)
gr.add_geometry(renderer, face1_polydata, color=[1.0, 1.0, 1.0], wire=True)

face2_polydata = vessel_wall.get_face_polydata(face_id=2)
#print("Num points: " + str(face_polydata.GetNumberOfPoints()))
#print("Num cells: " + str(face_polydata.GetNumberOfCells()))
gr.add_geometry(renderer, face2_polydata, color=[1.0, 1.0, 0.0], wire=False)

## Display window.
gr.display(renderer_window)

