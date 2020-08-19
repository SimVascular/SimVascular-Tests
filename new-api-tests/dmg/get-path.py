'''Test getting a path from the SV Data Manager.

This is tested using the Demo Project.
'''
import sv
  
## Create a Python path object from the SV Data Manager 'Paths/aorta' node. 
#
path_name = "aorta"
path = sv.dmg.get_path(path_name)
control_points = path.get_control_points()
print("Get '{0:s}' path.".format(path_name))
print("Number of control points: {0:d}".format(len(control_points)))
print("Control points: ")
for i,pt in enumerate(control_points):
    print("{0:d} {1:s}".format(i,str(pt)))

