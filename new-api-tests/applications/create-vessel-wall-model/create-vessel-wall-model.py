'''This script is used to create a model of a vessel wall by performing a Boolean 
   subtract operation between models of the inner and outer vessel contours.
'''
import os, pwd
import sys
import sv
import vtk
from math import sqrt
sys.path.insert(1, '../../graphics/')
import graphics as gr

class VesselModel(object):
    def __init__(self, renderer, kernel):
        self.renderer = renderer
        self.modeler = sv.modeling.Modeler(kernel)
        self.num_profile_points = 60
        self.segmentations = None 
        self.translate_scale = 0.1
        self.loft_with_nurbs = True 
        self.num_sections = 12 
        self.wall_thickness = 0.25
        self.edge_size = 0.2
        self.inner_surface = None
        self.inner_model = None
        self.outer_model = None

    def create_solid_models(self, model_name, seg_file_name):
        ## Read in segmentations.
        print("[VesselModel] Read SV ctgr file: {0:s}".format(seg_file_name))
        series = sv.segmentation.Series(seg_file_name)

        ## Get segmentations.
        time = 0
        num_segs = series.get_num_segmentations(time)
        self.segmentations = [ series.get_segmentation(sid, time) for sid in range(num_segs) ]
        print("[VesselModel] Number of segmentations: {0:d}".format(num_segs))

        ## Create inner lofted solid.
        print("Create inner loft surface ...")
        self.inner_surface = self.create_lofted_solid(self.segmentations, scale_contours=False)
        self.inner_model = self.create_solid_model(self.inner_surface)

        ## Create outer lofted solid.
        thickness = self.wall_thickness 
        print("[VesselModel] Create outer loft surface ...")
        print("[VesselModel]   wall_thickness: {0:g}".format(thickness))
        self.outer_surface = self.create_lofted_solid(self.segmentations, scale_contours=True, wall_thickness=thickness)
        self.outer_model = self.create_solid_model(self.outer_surface)

    def create_solid_model(self, loft_surface):
        '''Create a solid model from the lofted surfaces. 
        '''
        ## Create a solid model for the closed lofter surface.
        print("[VesselModel] Create solid model ...")
        model = sv.modeling.PolyData()
        model.set_surface(surface=loft_surface)
        model.compute_boundary_faces(angle=60.0)

        ## Remesh the model.
        edge_size = self.edge_size = 1.0
        print("[VesselModel]   edge_size: {0:g}".format(edge_size))
        remesh_model = sv.mesh_utils.remesh(model.get_polydata(), hmin=edge_size, hmax=edge_size)
        model.set_surface(surface=remesh_model)
        model.compute_boundary_faces(angle=60.0)
        return model

    def create_lofted_solid(self, segmentations, scale_contours=False, wall_thickness=0.0):
        '''Create a lofted solid from a list of segmentations.
        '''
        aligned_contours = self.align_contours(segmentations, scale_contours, wall_thickness)  
        loft_with_nurbs = False
        loft_with_nurbs = True

        if loft_with_nurbs:
            print("Creating a lofted surface using NURBS.")
            num_sect = self.num_sections 
            options = sv.geometry.LoftNurbsOptions()
            loft_surf = sv.geometry.loft_nurbs(polydata_list=aligned_contours, loft_options=options, num_sections=num_sect)

        else:
            options = sv.geometry.LoftOptions()
            options.interpolate_spline_points = True
            options.num_spline_points = 50
            options.num_long_points = 100
            loft_surf = sv.geometry.loft(polydata_list=aligned_contours, loft_options=options)

        loft_capped = sv.vmtk.cap(surface=loft_surf, use_center=False)
        return loft_capped 

    def align_contours(self, segmentations, scale_contours=False, wall_thickness=0.0):  
        num_contours = len(segmentations)
        num_profile_points = self.num_profile_points
        use_distance = True
        contour_list = []
        tscale = self.translate_scale

        for i,seg in enumerate(segmentations):
            cont_pd = seg.get_polydata()
            cont_ipd = sv.geometry.interpolate_closed_curve(polydata=cont_pd, number_of_points=num_profile_points)

            if scale_contours:
                center = seg.get_center()
                cont_ipd = self.expand_polydata(cont_ipd, center, wall_thickness)
            else:
                if i == 0:
                    normal = seg.get_normal()
                    cont_ipd = self.translate_polydata(cont_ipd, normal, scale=-tscale)
                elif i == len(segmentations) - 1:
                    normal = seg.get_normal()
                    cont_ipd = self.translate_polydata(cont_ipd, normal, scale=tscale)

            if i == 0:
                cont_align = cont_ipd
            else:
                cont_align = sv.geometry.align_profile(last_cont_align, cont_ipd, use_distance)
            contour_list.append(cont_align)
            last_cont_align = cont_align
    
        return contour_list

    def translate_polydata(self, polydata, normal, scale=1.0):
        '''Translate polydata in a direction given by 'normal'.
        '''
        transform = vtk.vtkTransform()
        tx = scale * normal[0]
        ty = scale * normal[1]
        tz = scale * normal[2]
        transform.Translate(tx, ty, tz)
        transformFilter = vtk.vtkTransformFilter()
        transformFilter.SetInputData(polydata)
        transformFilter.SetTransform(transform)
        transformFilter.Update()
        return transformFilter.GetOutput()

    def expand_polydata(self, polydata, center, dist=1.0):
        '''Create a polydata object such that its points are 'dist' distance from the 
           points of the given 'polydata'. 
        '''
        num_pts = polydata.GetNumberOfPoints()
        num_cells = polydata.GetNumberOfCells()
        polydata_pts = polydata.GetPoints()
        polydata_cells = polydata.GetLines()

        points = vtk.vtkPoints()
        points.SetNumberOfPoints(num_pts)
        lines = vtk.vtkCellArray()
        n = 0
        pt = 3*[0.0]
        spt = 3*[0.0]
        v = 3*[0.0]
        for i in range(num_pts):
            polydata_pts.GetPoint(i, pt)
            v = [ pt[j] - center[j] for j in range(3) ]
            mag = sqrt(sum([v[j]*v[j] for j in range(3)]))
            s = dist / mag
            spt = [ pt[j] + s*v[j] for j in range(3) ]
            points.SetPoint(n, spt[0], spt[1], spt[2])
            n += 1

        scaled_polydata = vtk.vtkPolyData()
        scaled_polydata.SetPoints(points)
        scaled_polydata.SetLines(polydata_cells)
        scaled_polydata.BuildLinks()

        return scaled_polydata

    def show_inner_model(self, color, wire=False, edges=False):
        polydata = self.inner_model.get_polydata()
        gr.add_geometry(self.renderer, polydata, color, edges, wire)

    def show_outer_model(self, color, wire=False, edges=False):
        polydata = self.outer_model.get_polydata()
        gr.add_geometry(self.renderer, polydata, color, edges, wire)

    def show_segmentations(self, color):
        for seg in self.segmentations:
            gr.create_segmentation_geometry(renderer, seg, color)


#_class VesselModel


if __name__ == '__main__':

    ## Create renderer and graphics window.
    win_width = 500
    win_height = 500
    renderer, renderer_window = gr.init_graphics(win_width, win_height)

    ## Build models for the aorta.
    model_name = 'aorta'
    seg_file_name = "../../data/DemoProject/Segmentations/" + model_name + ".ctgr"
    aorta_vessel_model = VesselModel(renderer, sv.modeling.Kernel.POLYDATA)
    aorta_vessel_model.create_solid_models(model_name, seg_file_name)
    #aorta_vessel_model.show_inner_model(color=[1.0,0.0,0.0], wire=True, edges=False)
    #aorta_vessel_model.show_outer_model(color=[0.0,1.0,0.0], wire=False, edges=False)
    aorta_vessel_model.show_segmentations(color=[1.0,1.0,1.0])

    ## Build models for the right iliac.
    model_name = 'right_iliac'
    seg_file_name = "../../data/DemoProject/Segmentations/" + model_name + ".ctgr"
    iliac_vessel_model = VesselModel(renderer, sv.modeling.Kernel.POLYDATA)
    iliac_vessel_model.create_solid_models(model_name, seg_file_name)
    #iliac_vessel_model.show_inner_model(color=[1.0,0.0,0.0], wire=False, edges=False)
    #iliac_vessel_model.show_outer_model(color=[0.0,1.0,0.0], wire=False, edges=False)
    iliac_vessel_model.show_segmentations(color=[1.0,1.0,1.0])

    ## Union vessels.
    modeler = sv.modeling.Modeler(sv.modeling.Kernel.POLYDATA)
    inner_union = modeler.union(aorta_vessel_model.inner_model, iliac_vessel_model.inner_model)
    #gr.add_geometry(renderer, inner_union.get_polydata(), color=[1.0,0.0,1.0])
    outer_union = modeler.union(aorta_vessel_model.outer_model, iliac_vessel_model.outer_model)
    #gr.add_geometry(renderer, outer_union.get_polydata(), color=[1.0,0.0,1.0])

    ## Subtract union vessels to get vessel wall.
    vessel_wall = modeler.subtract(main=outer_union, subtract=inner_union)
    #face_ids = vessel_wall.compute_boundary_faces(angle=50.0)
    face_ids = vessel_wall.get_face_ids()
    print("Vessel wall model face IDs: " + str(face_ids))
    gr.add_geometry(renderer, vessel_wall.get_polydata(), color=[1.0,0.0,1.0])
    vessel_wall.write(file_name="vessel-wall", format="vtp")

    ## Display window.
    gr.display(renderer_window)

