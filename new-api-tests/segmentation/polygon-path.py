'''Test creating a polygon segmentation using a curve point on a path.
'''
import json
import sv
import sys
import vtk
sys.path.insert(1, '../graphics/')
import graphics as gr

def create_segmentation(renderer, path, path_index):
    ''' Create a segmentation from a path curve point.
    '''
    control_points = [
      [-3.15842433564831, -1.07767837122083,  13.490209437441081],  
      [-2.14692030096194, -0.763005597167648, 14.23620401811786],  
      [-1.4866329531651,  -1.79294709610986,  14.099553553154692],  
      [-1.6130709645804,  -2.87930015282473,  13.47775803366676],  
      [-2.27335832035169, -3.03586243308382,  13.015448896447197],  
      [-3.0741323401453, -2.14261536573758,    13.001546733081341]
    ]

    print("Create segmentation ...")    

    # Get path curve frame.
    print("  Path index: " + str(path_index))    
    curve_frame = path.get_curve_frame(path_index)
    print("Path curve frame: ")
    print("  ID: " + str(curve_frame.id))    
    print("  Position: " + str(curve_frame.position))    
    print("  Normal: " + str(curve_frame.normal))    
    print("  Tangent: " + str(curve_frame.tangent))    

    # Create circle segmentation.
    center = [ -2.30674277962187, -1.88743121940042, 13.575810494091229 ]

    segmentation = sv.segmentation.Polygon(control_points)
    #segmentation = sv.segmentation.Polygon(control_points=control_points)

    return segmentation 

def create_path():
    # Read control points.
    with open('../pathplanning/aorta-control-points.json') as json_file:
        control_points = json.load(json_file)

    # Create Path object.
    path = sv.pathplanning.Path()

    # Add control points.
    for pt in control_points:
        path.add_control_point(pt)

    return path

## Create a path.
path = create_path()

## Create renderer and graphics window.
win_width = 500
win_height = 500
renderer, renderer_window = gr.init_graphics(win_width, win_height)

## Create a segmentation at path index 5.
seg1 = create_segmentation(renderer, path, path_index=0)
#normal = seg1.get_normal()
#print("Normal: " + str(normal))    

## Show segmentation.
gr.create_segmentation_geometry(renderer, seg1, color=[1.0, 0.0, 0.0])

## Change segmentation frame.
#curve_frame = path.get_curve_frame(10)
#print("New segmentation center: {0:s}".format(str(curve_frame.position)))
#seg1.set_frame(frame=curve_frame)
#gr.create_segmentation_geometry(renderer, seg1, color=[0.0, 1.0, 1.0])
#gr.add_sphere(renderer, curve_frame.position, 0.2, color=[1.0, 1.0, 0.0], wire=True)

# Show path.
gr.create_path_geometry(renderer, path)

## Add a sphere at the origin.
gr.add_sphere(renderer, [0.0,0.0,0.0], 0.5, color=[1.0, 1.0, 1.0], wire=True)

# Display window.
gr.display(renderer_window)

