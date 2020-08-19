'''This scipt tests writing a SV Model .mdl file.
'''
from pathlib import Path
import sv
import sys
import vtk
sys.path.insert(1, '../graphics/')
import graphics as gr

## Read an SV model group file. 
#
home = str(Path.home())
file_name = "../data/DemoProject/Models/demo.mdl"
print("Read SV mdl file: {0:s}".format(file_name))
series= sv.modeling.Series(file_name)
num_models = series.get_num_times()
print("  Number of models: {0:d}".format(num_models))

## Write group.
file_name = "group-write-test.mdl"
series.write(file_name)

