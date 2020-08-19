'''Test setting a POLYDATA model using a PolyData object.
'''
import sv
import sys
import vtk
sys.path.insert(1, '../graphics/')
import graphics as gr

## Read PolyData.
file_name = "../data/models/loft-test-interpolate.vtp"
reader = vtk.vtkXMLPolyDataReader()
reader.SetFileName(file_name) 
reader.Update()
read_polydata = reader.GetOutput()

## Create a model from the PolyData object.
model = sv.modeling.PolyData()
model.set_surface(surface=read_polydata)

## Compute boundary faces.
face_ids = model.compute_boundary_faces(angle=60.0)
print("Model face IDs: " + str(face_ids))

## Test capping.
polydata = model.get_polydata()
capped_polydata = sv.vmtk.cap_with_ids(surface=polydata, fill_id=1, increment_id=True)

## Write the model.
if True:
    file_name = "loft-model-written"
    file_format = "vtp"
    model.write(file_name=file_name, format=file_format)

## Create renderer and graphics window.
win_width = 500
win_height = 500
renderer, renderer_window = gr.init_graphics(win_width, win_height)

## Add model polydata.
gr.add_geometry(renderer, capped_polydata, color=[1.0, 0.0, 0.0], wire=False, edges=True)
#gr.add_geometry(renderer, polydata, color=[1.0, 0.0, 0.0], wire=False, edges=True)

# Display window.
gr.display(renderer_window)



