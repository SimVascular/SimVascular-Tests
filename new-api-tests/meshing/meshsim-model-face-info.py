'''Test MeshSim get_model_face_info().
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
file_name = str(data_path / 'meshing' / 'aorta-iliac.xmt_txt')
mesher.load_model(file_name)

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

