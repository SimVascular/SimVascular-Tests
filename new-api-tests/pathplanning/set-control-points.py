'''Test setting a list of control points. 
'''
import sv 
import sys
sys.path.insert(1, '../graphics/')
import graphics as gr

## Control points.
points = [ [2.0, 0.2, 2.2], 
           [3.0, 0.3, 3.3],
           [4.0, 0.4, 4.4],
           [5.0, 0.5, 5.5] 
]

## Create Path object.
path = sv.pathplanning.Path()

## Add control points.
path.set_control_points(points)

control_points = path.get_control_points()
print("Number of control points: {0:d}".format(len(control_points)))
for i,pt in enumerate(control_points): 
    print("{0:d}  {1:s}".format(i, str(pt)))

curve_points = path.get_curve_points()
print("Number of curve points: {0:d}".format(len(curve_points)))

