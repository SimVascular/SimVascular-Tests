'''
Test the sv.geometry.BlendOptions() class. 
'''
from pathlib import Path
import sv
import vtk

options = sv.geometry.BlendOptions()

#-------------------
# print all options
#-------------------
print("\n\nOptions values: ")
[ print("  {0:s}:{1:s}".format(key,str(value))) for (key, value) in sorted(options.get_values().items()) ]
print("\n\n")
