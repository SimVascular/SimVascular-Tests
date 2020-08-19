'''
Test the sv.geometry.LoftOptions() class. 
'''
from pathlib import Path
import sv
import vtk

options = sv.geometry.LoftOptions()

#-------------------
# print all options
#-------------------
print("\n\nOptions values: ")
[ print("  {0:s}:{1:s}".format(key,str(value))) for (key, value) in sorted(options.get_values().items()) ]
print("\n\n")
