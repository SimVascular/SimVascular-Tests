'''Test getting a model from the SV Data Manager.

   This is tested using the Demo Project.

Expected output:

  Number of models: 1
  Model type: <class 'solid.PolyData'>
  Model Face IDs: [1, 2, 3, 4, 5]
  Model polydata: num nodes: 8351
  Model polydata: num polygons: 16698

'''
import sv
import vtk
  
## Create a Python model object from the SV Data Manager 'Models/aorta' node. 
#
model_name = "demo"
model_group = sv.dmg.get_model(model_name)
num_models = model_group.get_num_models()
print("Number of models: {0:d}".format(num_models))

## Get the model for the 0th time step.
#
model = model_group.get_model(0)
print("Model type: " + str(type(model)))
face_ids = model.get_face_ids()
print("Model Face IDs: {0:s}".format(str(face_ids)))

model_polydata = model.get_polydata()
print("Model polydata: num nodes: {0:d}".format(model_polydata.GetNumberOfPoints()))
print("Model polydata: num polygons: {0:d}".format(model_polydata.GetNumberOfCells()))


