'''This scripts tests creating a PathSeries and writing it to a .pth file.
'''
import json 
import sv 

## Create a Series object. 
path_series = sv.pathplanning.Series()

## Create Path object.
path = sv.pathplanning.Path()

# Read control points.
with open('aorta-control-points.json') as json_file:
    control_points = json.load(json_file)

# Add control points.
for pt in control_points:
    path.add_control_point(pt)

## Add path to series.
path_series.set_path(path=path, time=0)
path_series.set_path_id(1)

print("Path series:")
print("  Number of paths: {0:d}".format(path_series.get_num_paths()))

## Write the path series to a file.
path_series.write("test-series.pth")

