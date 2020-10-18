'''Test MeshSim get_model_face_info().
'''
import sv
import sys
import vtk
import vtk
sys.path.insert(1, '../graphics/')
import graphics as gr

## Create a MeshSim mesher.
#
#mesher = sv.meshing.MeshSim()
mesher = sv.meshing.create_mesher(sv.meshing.Kernel.MESHSIM)

## Load the aorta iliac model.
#
# face id="1647" name="wall_right_iliac" type="wall" 
# face id="1638" name="right_iliac" type="cap" 
# face id="1692" name="wall_aorta" type="wall" 
# face id="1685" name="aorta" type="cap" 
# face id="1683" name="aorta_2" type="cap" 
#
mdir = "../data/meshing/"
mesher.load_model(mdir+"aorta-iliac.xmt_txt")
#mesher.load_model("/home/parkerda/SimVascular/DemoProject/Models/parasolid-demo.xmt_txt")

## Mesh face info:  
#
#  {101 13 {wall_right_iliac}}  
#  {76 7 {right_iliac}}  
#  {73 63 {wall_aorta}}  
#  {96 57 {aorta}}  
#  {98 60 {aorta_2}} 
#
#

face_info = mesher.get_model_face_info()
print("Mesh face info: ")
for key in face_info:
    print("  {0:s}:  {1:s}".format(key, str(face_info[key])))

face_ids = mesher.get_model_face_ids()
print("Mesh face ids: " + str(face_ids))

