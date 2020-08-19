''' Test replacing control points. 
'''
import sv 
import sys
sys.path.insert(1, '../graphics/')
import graphics as gr

## Control points.
cpt1 = [2.0, 0.0, 0.0] 
cpt2 = [3.0, 0.0, 0.0] 
cpt3 = [4.0, 0.0, 0.0] 
cpt4 = [5.0, 0.0, 0.0] 

## Create Path object.
path = sv.pathplanning.Path()

## Add control points.
path.add_control_point(cpt1)
path.add_control_point(cpt2)
path.add_control_point(cpt3)
path.add_control_point(cpt4)

## Print control points.
control_points = path.get_control_points()
print("Number of control points: {0:d}".format(len(control_points)))
for i,pt in enumerate(control_points):
    print("i: {0:d}  point: {1:s}".format(i, str(pt)))

## Replace at a location.
#
#  0 <= location >= number of control points.
cpt = [-4.0, 0.0, 0.0] 
path.replace_control_point(3, cpt) 

## Error tests.
# 

## Print control points.
control_points = path.get_control_points()
print("\nNumber of new control points: {0:d}".format(len(control_points)))
for i,pt in enumerate(control_points):
    print("i: {0:d}  point: {1:s}".format(i, str(pt)))


