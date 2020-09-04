'''
This script tests opening an SV project.
'''
from pathlib import Path
import project 
from visualization import Visualization,VisualizationGeometry
import numpy as np

class TestProject(object):
    def __init__(self, visualization):
        self.visualization = visualization
        self.image = None 

    def select_contour(self, contour, position):
        print("[select_contour] ")
        print("[select_contour] Position: {0:s} ".format(str(position)))
        #cid = contour.get_id()
        #print("[select_contour] Contour ID: {0:d} ".format(cid))

    def select_path(self, path, position):
        print("[select_path] ")
        print("[select_path] Select position: {0:s} ".format(str(position)))
        points = path.get_curve_points()
        num_pts = len(points)
        min_d = 1e6	
        min_i = None
        for i,point in enumerate(points):
           dx = position[0] - point[0]
           dy = position[1] - point[1]
           dz = position[2] - point[2]
           d = dx*dx + dy*dy + dz*dz
           if d < min_d:
               min_d = d
               min_i = i
        #_for i,point in enumerate(points)
        print("[select_path] Path number of curve points: {0:d} ".format(num_pts))
        print("[select_path] Path curve point index: {0:d} ".format(min_i))
        point = path.get_curve_point(min_i)
        tangent = path.get_curve_tangent(min_i)
        normal = path.get_curve_normal(min_i)
        print("[select_path] Point: {0:s} ".format(str(point)))
        print("[select_path] Tangent: {0:s} ".format(str(tangent)))
        print("[select_path] Normal: {0:s} ".format(str(normal)))

        if True:
            # Show tangent.
            s = 1.0
            pt1 = point
            tangent = np.array(tangent)
            pt2 = [(pt1[j]+s*tangent[j]) for j in range(0,3)]
            self.visualization.add_line(pt1, pt2, color=[1.0,0.0,0.0], width=5)
            # Show normal.
            normal = np.array(normal)
            pt2 = [(pt1[j]+s*normal[j]) for j in range(0,3)]
            self.visualization.add_line(pt1, pt2, color=[1.0,0.0,0.0], width=5)
            # Show binormal.
            binormal = np.cross(tangent, normal)
            pt2 = [(pt1[j]+s*binormal[j]) for j in range(0,3)]
            self.visualization.add_line(pt1, pt2, color=[1.0,0.0,0.0], width=5)

            self.image.extract_slice(pt1, tangent, normal, binormal)

    def show_image(self, project, image_name):
        print(" ")
        print("Get {0:s} image ... ".format(image_name))
        image = project.get_image(image_name)
        image.visualization = self.visualization 
        image.display_edges()
        #image.display_axis_slice('j', 30)
        #image.display_axis_slice('i', 255)
        image.display_axis_slice('k', 255)
        self.image = image 

    def show_mesh(self, project, mesh_name):
        print(" ")
        print("Get {0:s} mesh ... ".format(mesh_name))
        #model_group = project.get_model(model_name)

    def show_model(self, project, model_name):
        print(" ")
        print("Get {0:s} model ... ".format(model_name))
        model_group = project.get_model(model_name)
        num_models = model_group.number_of_models()
        print("  Number of models: {0:d}".format(num_models))
        model = model_group.get_model(0)
        print("  Model type: " + str(type(model)))
        face_ids = model.get_face_ids()
        print("  Model Face IDs: {0:s}".format(str(face_ids)))
        model_polydata = model.get_polydata()
        print("  Model polydata: num nodes: {0:d}".format(model_polydata.GetNumberOfPoints()))
        print("  Model polydata: num polygons: {0:d}".format(model_polydata.GetNumberOfCells()))
        mgeom = VisualizationGeometry(model_name, model, None)
        self.visualization.add_polydata(mgeom, model_polydata, color=[0.0, 1.0, 1.0], opacity=0.5, pickable=False)

    def show_path(self, project, path_name):
        print(" ")
        print("Get path group {0:s}: ".format(path_name))
        path_group = project.get_path(path_name)
        print("  Number of paths: {0:d}".format(path_group.get_num_times()))
        print("  Method: {0:s}".format(path_group.get_method()))
        print(" ")
        path = path_group.get_path(0)
        control_points = path.get_control_points()
        print("  Number of control points: {0:d}".format(len(control_points)))
        curve_points = path.get_curve_points()
        print("  Number of curve points: {0:d}".format(len(curve_points)))
        path_lines, path_control_points = self.visualization.get_path_geometry(path)
        pgeom = VisualizationGeometry(path_name, path, self.select_path)
        self.visualization.add_polydata(pgeom, path_lines, color=[0.8, 0.0, 0.0], line_width=2.0)

    def show_segmentation(self, project, seg_name):
        print(" ")
        print("Get {0:s} segmentation ... ".format(seg_name))
        segmentation = project.get_segmentation(seg_name)
        num_conts = segmentation.get_num_times()
        print("  Number of contours: {0:d}".format(num_conts))
        for i in range(num_conts):
            contour = segmentation.get_segmentation(i)
            contour_geom, center_point, control_points = self.visualization.get_contour_geometry(contour)
            name = seg_name+":contour:" + str(i)
            cgeom = VisualizationGeometry(name, contour, self.select_contour)
            self.visualization.add_polydata(cgeom, contour_geom, color=[0.0, 0.8, 0.0], line_width=2.0)

## Open a project.
print("  ")
print("==================== Test Opening a Project ====================")
project_path = "../data/DemoProject"
project_path = "/Users/parkerda/SimVascular/DemoProject/"
project = project.Project()
project.open(project_path)

win_width = 500
win_height = 500
vis = Visualization("Demo Project", win_width, win_height)
test_project = TestProject(vis)

## Print the plugins defined for the project.
print(" ") 
print("Plugins: ") 
plugin_instances = project.get_plugin_instances()
for name, inst in plugin_instances.items(): 
    print("  {0:s} : {1:s}".format(name, ', '.join([name for name in inst])))

## Get an SV path object.
#
# show_path(project, vis, "right_iliac")
path_plugin_instances = project.get_plugin_instances(project.plugin_names.PATHS)
print("Number of path plugins: {0:d}".format(len(path_plugin_instances))) 
for name in path_plugin_instances:
    test_project.show_path(project, name)

## Get an SV segmentation object.
#
#show_segmentation(project, vis, "right_iliac")
seg_plugin_instances = project.get_plugin_instances(project.plugin_names.SEGMENTATIONS)
print("Number of segmentation plugin instances: {0:d}".format(len(seg_plugin_instances))) 
for name in seg_plugin_instances:
    test_project.show_segmentation(project, name)

## Get an SV model object.
#
# test_project.show_model(project, "demo")

## Get an image object.
#
# test_project.show_image(project, "sample_data-cm")

## Get a mesh object.
#
test_project.show_mesh(project, "demo")

## Display geometry.
#
if True:
    vis.display()

