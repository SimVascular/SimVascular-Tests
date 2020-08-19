'''Test creating a POLYDATA model from a PolyData object.
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
model = sv.modeling.PolyData(surface=read_polydata)
polydata = model.get_polydata()

## Compute boundary faces.
face_ids = model.compute_boundary_faces(angle=60.0)
print("Model face IDs: " + str(face_ids))

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
gr.add_geometry(renderer, polydata, color=[1.0, 0.0, 0.0], wire=False, edges=True)

# Display window.
gr.display(renderer_window)



