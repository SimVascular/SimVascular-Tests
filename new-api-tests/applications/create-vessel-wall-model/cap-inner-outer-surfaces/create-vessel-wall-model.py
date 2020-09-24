'''This script is used to create a model of a vessel wall by performing a Boolean 
   subtract operation between models of the inner and outer vessel contours.
'''
import os, pwd
import sys
import sv
import vtk
from math import sqrt
sys.path.insert(1, '../../../graphics/')
import graphics as gr

class VesselModel(object):
    def __init__(self, renderer, kernel):
        self.renderer = renderer
        self.modeler = sv.modeling.Modeler(kernel)
        self.num_profile_points = 60
        self.segmentations = None 
        self.outer_aligned_contours = None 
        self.inner_aligned_contours = None 
        self.translate_scale = 0.1
        self.loft_with_nurbs = True 
        self.num_sections = 12 
        self.wall_thickness = 0.25
        self.edge_size = 0.2

        self.inner_surface = None
        self.inner_surface_edges = None
        self.inner_surface_edges_comp = None

        self.outer_surface = None
        self.outer_surface_edges = None
        self.outer_surface_edges_comp = None
        self.inlet_cap = None
        self.outlet_cap = None
        self.closed_lofted_surface = None
        self.solide_model = None

    def create_solid_model(self, model_name, seg_file_name):
        ## Read in segmentations.
        print("[VesselModel] Read SV ctgr file: {0:s}".format(seg_file_name))
        series = sv.segmentation.Series(seg_file_name)

        ## Get segmentations.
        time = 0
        num_segs = series.get_num_segmentations(time)
        self.segmentations = [ series.get_segmentation(sid, time) for sid in range(num_segs) ]
        print("[VesselModel] Number of segmentations: {0:d}".format(num_segs))

        ## Create inner lofted surface.
        print("Create inner loft surface ...")
        self.inner_surface = self.create_lofted_surface(self.segmentations, scale_contours=False)
        self.inner_surface_edges, self.inner_surface_edges_comp = self.extract_surface_edges(self.inner_surface)
        #self.write_polydata(self.inner_surface_edges_comp[0], "inner_surface_edges_comp0.vtp")
        #self.write_polydata(self.inner_surface_edges_comp[1], "inner_surface_edges_comp1.vtp")
        #self.write_polydata(self.inner_surface_edges, "inner_surface_edges.vtp")
        print("[VesselModel] Inner surface edges: ")
        print("[VesselModel]   Number of points: {0:d}".format(self.inner_surface_edges.GetNumberOfPoints()))

        ## Create outer lofted surface.
        thickness = self.wall_thickness 
        print("[VesselModel] Create outer loft surface ...")
        print("[VesselModel]   wall_thickness: {0:g}".format(thickness))
        self.outer_surface = self.create_lofted_surface(self.segmentations, scale_contours=True, wall_thickness=thickness)
        self.outer_surface_edges, self.outer_surface_edges_comp = self.extract_surface_edges(self.outer_surface)
        print("[VesselModel] Inner surface: ")
        print("[VesselModel]   Number of points: {0:d}".format(self.inner_surface.GetNumberOfPoints()))
        print("[VesselModel]   Number of cells: {0:d}".format(self.inner_surface.GetNumberOfCells()))

        print("[VesselModel] Outer surface: ")
        print("[VesselModel]   Number of points: {0:d}".format(self.outer_surface.GetNumberOfPoints()))
        print("[VesselModel]   Number of cells: {0:d}".format(self.outer_surface.GetNumberOfCells()))

        ## Cap the ends of the lofter surfaes.
        self.inlet_cap = self.add_cap(inlet=True)
        self.outlet_cap = self.add_cap(inlet=False)
        #print(str(self.inlet_cap))
        print("[VesselModel] Inlet cap: ")
        print("[VesselModel]   Number of points: {0:d}".format(self.inlet_cap.GetNumberOfPoints()))
        print("[VesselModel]   Number of cells: {0:d}".format(self.inlet_cap.GetNumberOfCells()))
        self.write_polydata(self.inlet_cap, "inlet_cap.vtp")
        self.write_polydata(self.outlet_cap, "outlet_cap.vtp")

        ## Merge lofted surfaces and caps.
        append_filter = vtk.vtkAppendPolyData()
        append_filter.AddInputData(self.inner_surface)
        append_filter.AddInputData(self.outer_surface)
        append_filter.AddInputData(self.inlet_cap)
        append_filter.AddInputData(self.outlet_cap)
        append_filter.Update()

        ## Remove any duplicate points.
        tol = 1e-5
        clean_filter = vtk.vtkCleanPolyData()
        clean_filter.SetInputData(append_filter.GetOutput())
        clean_filter.SetTolerance(tol)
        clean_filter.Update()
        print("[VesselModel] Clean polydata: ")
        print("[VesselModel]   Tolerance: {0:g}".format(clean_filter.GetTolerance()))
        self.closed_lofted_surface = clean_filter.GetOutput() 
        print("[VesselModel] Closed lofted surface: ")
        print("[VesselModel]   Number of points: {0:d}".format(self.closed_lofted_surface.GetNumberOfPoints()))
        print("[VesselModel]   Number of cells: {0:d}".format(self.closed_lofted_surface.GetNumberOfCells()))

        writer = vtk.vtkXMLPolyDataWriter()
        writer.SetFileName("closed_lofted_surface.vtp");
        writer.SetInputData(self.closed_lofted_surface)
        writer.Write()

        ## Create a solid model for the closed surface.
        print("[VesselModel] Create solid model ...")
        model = sv.modeling.PolyData()
        model.set_surface(surface=self.closed_lofted_surface)
        face_ids = model.compute_boundary_faces(angle=60.0)
        print("Model Face IDs: {0:s}".format(str(face_ids)))

        ## Remesh the model.
        if False:
            edge_size = self.edge_size = 1.0
            print("[VesselModel]   edge_size: {0:g}".format(edge_size))
            remesh_model = sv.mesh_utils.remesh(model.get_polydata(), hmin=edge_size, hmax=edge_size)
            model.set_surface(surface=remesh_model)
            model.compute_boundary_faces(angle=60.0)

        self.solid_model = model

    def write_polydata(self, polydata, file_name): 
        writer = vtk.vtkXMLPolyDataWriter()
        writer.SetFileName(file_name)
        writer.SetInputData(polydata)
        writer.Write()

    def create_lofted_surface(self, segmentations, scale_contours=False, wall_thickness=0.0):
        '''Create a lofted surface from a list of segmentations.
        '''
        aligned_contours = self.align_contours(segmentations, scale_contours, wall_thickness)  
        if scale_contours:
            self.outer_aligned_contours = aligned_contours 
        else:
            self.inner_aligned_contours = aligned_contours 
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

        return loft_surf

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
                    #cont_ipd = self.translate_polydata(cont_ipd, normal, scale=-tscale)
                elif i == len(segmentations) - 1:
                    normal = seg.get_normal()
                    #cont_ipd = self.translate_polydata(cont_ipd, normal, scale=tscale)

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

    def get_points_center(self, points):
        num_points = points.GetNumberOfPoints()
        center = 3*[0.0]
        for i in range(num_points):
            pt = points.GetPoint(i)
            center[0] += pt[0] 
            center[1] += pt[1] 
            center[2] += pt[2] 
        return [x / num_points for x in center ] 

    def get_edge_component(self, inlet):
        #print("========== get_edge_component ==========")
        #print("[get_edge_component] inlet: " + str(inlet))

        if inlet:
            inner_contour = self.inner_aligned_contours[0]
            outer_contour = self.outer_aligned_contours[0]
        else:
            inner_contour = self.inner_aligned_contours[-1]
            outer_contour = self.outer_aligned_contours[-1]

        inner_points = inner_contour.GetPoints()
        num_inner_points = inner_points.GetNumberOfPoints()
        outer_points = outer_contour.GetPoints()
        num_outer_points = outer_points.GetNumberOfPoints()

        #print("[get_edge_component] Inner edge ...")
        pt = 3*[0.0]
        cpt = 3*[0.0]
        inner_closest_comp = None
        inner_closest_comp_id = None
        min_comp_d = 1e6
        inner_center = self.get_points_center(inner_points)
        #print("[get_edge_component]   inner_center: "+str(inner_center))
        for cid,comp in enumerate(self.inner_surface_edges_comp): 
            #self.write_polydata(comp, "inner_surface_edges_comp_" + str(cid) + ".vtp")
            #print("[get_edge_component]   ---- comp {0:d} ---- ".format(cid))
            comp_points = comp.GetPoints()
            cp_center = self.get_points_center(comp_points)
            #print("[get_edge_component]   cp_center: "+str(cp_center))
            dist = sum([(inner_center[j]-cp_center[j])*(inner_center[j]-cp_center[j]) for j in range(3)])
            #print("[get_edge_component]   dist: "+str(dist))
            if dist < min_comp_d:
                inner_closest_comp = comp 
                inner_closest_comp_id = cid
                min_comp_d = dist
        #_for comp in self.inner_surface_edges_comp
        #print("[get_edge_component]   min_comp_d: {0:g}".format(min_comp_d))
        #print("[get_edge_component]   inner_closest_comp_id: {0:d}".format(inner_closest_comp_id))

        #print("[get_edge_component] Outer edge ...")
        outer_closest_comp = None
        outer_closest_comp_id = None
        outer_center = self.get_points_center(inner_points)
        min_comp_d = 1e6
        for cid,comp in enumerate(self.outer_surface_edges_comp):
            #print("[get_edge_component] ---- comp {0:d} ---- ".format(cid))
            comp_points = comp.GetPoints()
            cp_center = self.get_points_center(comp_points)
            dist = sum([(outer_center[j]-cp_center[j])*(outer_center[j]-cp_center[j]) for j in range(3)])
            #print("[get_edge_component]   dist: "+str(dist))
            if dist < min_comp_d:
                outer_closest_comp = comp
                outer_closest_comp_id = cid
                min_comp_d = dist
        #_for comp in self.outer_surface_edges_comp
        #print("[get_edge_component]   min_comp_d: {0:g}".format(min_comp_d))
        #print("[get_edge_component]   outer_closest_comp_id: {0:d}".format(outer_closest_comp_id))

        return inner_closest_comp, outer_closest_comp

    def add_cap(self, inlet=True):
        print("========== add caps ==========")
        print("[add_caps] Inlet: {0:d}".format(inlet))
        print("[add_caps] Number of inner edge components: {0:d}".format(len(self.inner_surface_edges_comp)))
        print("[add_caps] Number of outer edge components: {0:d}".format(len(self.outer_surface_edges_comp)))

        inner_contour, outer_contour = self.get_edge_component(inlet)
        inner_points = inner_contour.GetPoints()
        num_inner_points = inner_points.GetNumberOfPoints()
        #print("[add_caps] Number of inner points: {0:d}".format(num_inner_points))
        outer_points = outer_contour.GetPoints()
        num_outer_points = outer_points.GetNumberOfPoints()
        #print("[add_caps] Number of outer points: {0:d}".format(num_outer_points))

        gr.add_geometry(self.renderer, inner_contour, [0.0,1.0,0.0], wire=False)
        gr.add_geometry(self.renderer, outer_contour, [1.0,0.0,0.0], wire=False)

        cap_polydata = vtk.vtkPolyData()
        cap_points = vtk.vtkPoints()
        cap_cells = vtk.vtkCellArray()
        tri = vtk.vtkTriangle()

        ## Add points.
        #
        pt = 3*[0.0]
        for i in range(num_inner_points):
            pt = inner_points.GetPoint(i)
            cap_points.InsertNextPoint(pt[0], pt[1], pt[2])  
        for i in range(num_inner_points):
            pt = outer_points.GetPoint(i)
            cap_points.InsertNextPoint(pt[0], pt[1], pt[2])  
 
        r = 0.02
        gr.add_sphere(renderer, inner_points.GetPoint(0), r, color=[1.0, 0.0, 0.0], wire=False)
        gr.add_sphere(renderer, inner_points.GetPoint(1), r, color=[0.0, 1.0, 0.0], wire=False)
        gr.add_sphere(renderer, inner_points.GetPoint(2), r, color=[0.0, 0.0, 1.0], wire=False)
        gr.add_sphere(renderer, inner_points.GetPoint(3), r, color=[1.0, 1.0, 0.0], wire=False)
        gr.add_sphere(renderer, inner_points.GetPoint(4), r, color=[1.0, 0.0, 1.0], wire=False)

        gr.add_sphere(renderer, outer_points.GetPoint(0), r, color=[1.0, 0.0, 0.0], wire=False)
        gr.add_sphere(renderer, outer_points.GetPoint(1), r, color=[0.0, 1.0, 0.0], wire=False)
        gr.add_sphere(renderer, outer_points.GetPoint(2), r, color=[0.0, 0.0, 1.0], wire=False)
        gr.add_sphere(renderer, outer_points.GetPoint(3), r, color=[1.0, 1.0, 0.0], wire=False)
        gr.add_sphere(renderer, outer_points.GetPoint(4), r, color=[1.0, 0.0, 1.0], wire=False)

        ## Add triangles.
        #
        n = num_inner_points
        #for i in range(0,2):
        for i in range(num_inner_points):
            j = (i+1) % num_inner_points
            #print("i {0:d}  j {1:d}".format(i,j))
            tri = vtk.vtkTriangle()
            tri.GetPointIds().SetId(0, i)
            tri.GetPointIds().SetId(1, i+n)
            tri.GetPointIds().SetId(2, j+n)
            cap_cells.InsertNextCell(tri)

            tri = vtk.vtkTriangle()
            tri.GetPointIds().SetId(0, i)
            tri.GetPointIds().SetId(1, j+n)
            tri.GetPointIds().SetId(2, j)
            cap_cells.InsertNextCell(tri)

        cap_polydata.SetPoints(cap_points)
        cap_polydata.SetPolys(cap_cells)
        gr.add_geometry(self.renderer, cap_polydata, [1.0,1.0,1.0], wire=False)
        return cap_polydata

    def extract_surface_edges(self, polydata):
        feature_edges = vtk.vtkFeatureEdges()
        feature_edges.SetInputData(polydata)
        feature_edges.BoundaryEdgesOn()
        feature_edges.ManifoldEdgesOff()
        feature_edges.NonManifoldEdgesOff()
        feature_edges.FeatureEdgesOff()
        feature_edges.Update()

        boundary_edges = feature_edges.GetOutput()
        clean_filter = vtk.vtkCleanPolyData()
        boundary_edges_clean = clean_filter.SetInputData(boundary_edges)
        clean_filter.Update();
        cleaned_edges = clean_filter.GetOutput()

        edge_components = []
        conn_filter = vtk.vtkPolyDataConnectivityFilter()
        conn_filter.SetInputData(cleaned_edges)
        conn_filter.SetExtractionModeToSpecifiedRegions()
        self.boundary_edge_components = list()
        rid = 0

        while True:
            conn_filter.AddSpecifiedRegion(rid)
            conn_filter.Update()
            component = vtk.vtkPolyData()
            component.DeepCopy(conn_filter.GetOutput())
            if component.GetNumberOfCells() <= 0:
                break
            # [TODO:DaveP] the edge points don't seem to be oriented, this 
            # seems to fix that (maybe).
            stripper = vtk.vtkStripper()
            stripper.SetInputData(component)
            stripper.JoinContiguousSegmentsOn();
            stripper.Update()
            clean = vtk.vtkCleanPolyData()
            clean.SetInputData(stripper.GetOutput())
            clean.Update();
            edge_components.append(clean.GetOutput())
            conn_filter.DeleteSpecifiedRegion(rid)
            rid += 1

        cleaned_edges.BuildLinks()
        return cleaned_edges, edge_components

    def show_inner_surface(self, color, wire=False, edges=False):
        gr.add_geometry(self.renderer, self.inner_surface, color, edges, wire)

    def show_outer_surface(self, color, wire=False, edges=False):
        gr.add_geometry(self.renderer, self.outer_surface, color, edges, wire)

    def show_segmentations(self, color):
        for seg in self.segmentations:
            gr.create_segmentation_geometry(renderer, seg, color)

    def show_inner_aligned_contours(self, color):
        for contour in self.inner_aligned_contours:
             gr.add_geometry(renderer, contour, color)

    def show_outer_aligned_contours(self, color):
        for contour in self.outer_aligned_contours:
             gr.add_geometry(renderer, contour, color)

    def show_edges(self, color):
        gr.add_geometry(renderer, self.inner_surface_edges, color)
        gr.add_geometry(renderer, self.outer_surface_edges, color)

#_class VesselModel


if __name__ == '__main__':

    ## Create renderer and graphics window.
    win_width = 500
    win_height = 500
    renderer, renderer_window = gr.init_graphics(win_width, win_height)

    ## Build models for the aorta.
    model_name = 'aorta'
    seg_file_name = "../../../data/DemoProject/Segmentations/" + model_name + ".ctgr"
    aorta_vessel_model = VesselModel(renderer, sv.modeling.Kernel.POLYDATA)
    aorta_vessel_model.create_solid_model(model_name, seg_file_name)
    aorta_vessel_model.show_inner_surface(color=[1.0,0.0,0.0], wire=True, edges=False)
    aorta_vessel_model.show_outer_surface(color=[0.0,1.0,0.0], wire=False, edges=False)
    #aorta_vessel_model.show_segmentations(color=[1.0,1.0,1.0])
    #aorta_vessel_model.show_edges(color=[1.0,1.0,1.0])
    #aorta_vessel_model.show_inner_aligned_contours(color=[0.0,0.5,0.0])
    #aorta_vessel_model.show_outer_aligned_contours(color=[0.5,0.0,0.0])
    file_name = "vessel-wall-solid-model"
    file_format = "vtp"
    aorta_vessel_model.solid_model.write(file_name=file_name, format=file_format)

    '''
    ## Build models for the right iliac.
    model_name = 'right_iliac'
    seg_file_name = "../../../data/DemoProject/Segmentations/" + model_name + ".ctgr"
    iliac_vessel_model = VesselModel(renderer, sv.modeling.Kernel.POLYDATA)
    iliac_vessel_model.create_solid_models(model_name, seg_file_name)
    #iliac_vessel_model.show_inner_model(color=[1.0,0.0,0.0], wire=False, edges=False)
    #iliac_vessel_model.show_outer_model(color=[0.0,1.0,0.0], wire=False, edges=False)
    iliac_vessel_model.show_segmentations(color=[1.0,1.0,1.0])
    '''
    ## Display window.
    gr.display(renderer_window)

