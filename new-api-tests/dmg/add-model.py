'''Test adding a model to the SV Data Manager.

    This is tested using the Demo Project.
'''
from pathlib import Path
import sv

## Create a model from an SV file.
#
home = str(Path.home())
file_name = home + "/SimVascular/DemoProject/Models/demo.mdl"
print("Read SV mdl file: {0:s}".format(file_name))
demo_models = sv.modeling.Series(file_name)
num_models = demo_models.get_num_times()
print("Number of models: {0:d}".format(num_models))

## Add the Python model object under the SV Data Manager 'Model' nodes
#  as a new  node named 'new_demo'.
#
sv.dmg.add_model("new_demo", demo_models)

