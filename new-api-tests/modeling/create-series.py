'''This scipt tests creating a model Series and writing it to an SV Model .mdl file.

   [TODO:DaveP] There are no Series methods to add a model.
'''
from pathlib import Path
import sv
import sys
import vtk
sys.path.insert(1, '../graphics/')
import graphics as gr

## Create the Series object. 
#
series= sv.modeling.Series()

#num_models = series.get_num_times()
#print("  Number of models: {0:d}".format(num_models))

### Write group.
file_name = "create-series.mdl"
#series.write(file_name)

