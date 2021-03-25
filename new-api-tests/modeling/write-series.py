'''This scipt tests writing a SV Model .mdl file.
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

## Read an SV model group file. 
#
home = str(Path.home())
file_name = str(data_path / 'DemoProject' / 'Models' / 'demo.mdl')
print("Read SV mdl file: {0:s}".format(file_name))
series= sv.modeling.Series(file_name)
num_models = series.get_num_times()
print("  Number of models: {0:d}".format(num_models))

## Write group.
file_name = str(script_path / "group-write-test.mdl")
series.write(file_name)

