'''Test compute boundary faces method. 

   Select different modeling kernels using command line arguments

       1) o = OpenCascade

          compute_boundary_faces.py o 

       2) p = Parasolid 

          compute_boundary_faces.py p 

       3) no args for stl 

          compute_boundary_faces.py 

'''
import sv
import vtk
import sys
sys.path.insert(1, '../graphics/')
import graphics as gr

## Create a modeler.
mdir = "../data/models/"
modeler = None 
if len(sys.argv) == 2:
    if sys.argv[1] == 'o':
        modeler = sv.modeling.Modeler(sv.modeling.Kernel.OPENCASCADE)
        file_name = "cylinder.brep"
        print("Create OPENCASCADE modeler")
    elif sys.argv[1] == 'p':
        modeler = sv.modeling.Modeler(sv.modeling.Kernel.PARASOLID)
        file_name = "cylinder.xmt_txt"
        print("Create PARASOLID modeler")

if modeler == None:
    modeler = sv.modeling.Modeler(sv.modeling.Kernel.POLYDATA)
    file_name = "cylinder.stl"
    print("Create POLYDATA modeler")

## Read a model.
file_name = mdir + file_name
print("Read modeling model file: " + file_name)
model = modeler.read(file_name)
print("Model type: " + str(type(model)))

## Compute boundary faces.
if modeler.kernel == sv.modeling.Kernel.POLYDATA:
    face_ids = model.compute_boundary_faces(angle=60.0)
face_ids = model.get_face_ids()
print("Model face IDs: " + str(face_ids))

## Create renderer and graphics window.
win_width = 500
win_height = 500
renderer, renderer_window = gr.init_graphics(win_width, win_height)

## Add model polydata.
model_pd = model.get_polydata()
gr.add_geometry(renderer, model_pd, color=[0.0, 1.0, 0.0], wire=False, edges=False)

# Display window.
gr.display(renderer_window)

