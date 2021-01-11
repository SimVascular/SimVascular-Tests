#!/usr/bin/env python

from collections import defaultdict
from math import sqrt
from os import path
import vtk

class Centerlines(object):
    '''The Centerlines class defines methods for operations based on centerlines geometry.
    '''
    def __init__(self):
        self.graphics = None
        self.renderer = None
        self.geometry = None
        self.surface = None
        self.sections = None
        self.cids_array_name = "CenterlineIds"
        self.max_radius_array_name = "MaximumInscribedSphereRadius"
        self.length_scale = 1.0
        self.section_pids = None 
        self.start_pids = None 
        self.end_pids = None
        #self.end_offset = -0.9
        self.end_offset = 0.0

    def read(self, file_name):
        '''Read a centerlines geometry file created using SV.
        '''
        filename, file_extension = path.splitext(file_name)
        reader = vtk.vtkXMLPolyDataReader()
        reader.SetFileName(file_name)
        reader.Update()
        self.geometry = reader.GetOutput()
        self.compute_length_scale()
        self.extract_data()

    def write_clipped_surface(self, surface, file_name):
        '''Write a clipped surface to a .vtp file.
        '''
        writer = vtk.vtkXMLPolyDataWriter()
        writer.SetFileName(file_name)
        writer.SetInputData(surface)
        writer.Update()
        writer.Write()

    def extract_data(self):
        '''Extract centerline start/end IDs for each branch.
        '''
        print("========== extract_data ==========")
        cids = self.geometry.GetCellData().GetArray(self.cids_array_name)
        if cids == None:
            raise Exception("No '" + self.cids_array_name + "' data array defined in centerlines geometry.")
        vrange = cids.GetRange()
        min_id = int(vrange[0])
        max_id = int(vrange[1])
        print("Max centerline id: " + str(max_id))
        print("Min centerline id: " + str(min_id))
        self.sections = []
        for cid in range(min_id, max_id+1):
            section = self.extract_sections(self.geometry, cids, cid)
            self.sections.append(section)

        max_radius_data = self.geometry.GetPointData().GetArray(self.max_radius_array_name)
        num_lines = self.geometry.GetNumberOfLines()
        points = self.geometry.GetPoints()
        print("Number of centerline lines: {0:d}".format(num_lines))

        start_pids = []
        end_pids = []
        section_pids = defaultdict(list)

        for cid in range(min_id, max_id+1):
            print("----- cid {0:d} -----".format(cid))
            start_pid = None
            for i in range(num_lines):
                line_cid = cids.GetValue(i)
                if line_cid != cid: 
                    continue 
                cell = self.geometry.GetCell(i)
                cell_pids = cell.GetPointIds()
                num_ids = cell_pids.GetNumberOfIds()

                for j in range(num_ids):
                    pid = cell_pids.GetId(j)
                    section_pids[cid].append(pid)
        
                if start_pid == None:
                    start_pid = cell_pids.GetId(0)
                last_pid = cell_pids.GetId(num_ids-1)

            print("  start_pid {0:d}".format(start_pid))
            print("  last_pid {0:d}".format(last_pid))
            start_pt = points.GetPoint(start_pid)
            start_radius = max_radius_data.GetValue(start_pid) 
            start_pids.append(start_pid)
            gr_geom = self.graphics.add_sphere(self.renderer, start_pt, start_radius, color=[0.0, 1.0, 0.0])
            gr_geom.GetProperty().SetRepresentationToWireframe()

            last_pt = points.GetPoint(last_pid)
            last_radius = max_radius_data.GetValue(last_pid) 
            end_pids.append(last_pid)
            gr_geom = self.graphics.add_sphere(self.renderer, last_pt, last_radius, color=[1.0, 0.0, 0.0])
            gr_geom.GetProperty().SetRepresentationToWireframe()
        #_for cid in range(min_id, max_id+1)

        self.section_pids = section_pids
        self.start_pids = start_pids
        self.end_pids = end_pids

    def remove_surface_ends(self): 
        '''Remove the ends of the surface.
        '''
        print("========== remove_surface_ends ==========")
        section_pids = self.section_pids 
        start_pids = self.start_pids
        end_pids = self.end_pids
        self.start_pids = start_pids
        self.end_pids = end_pids
        points = self.geometry.GetPoints()
        max_radius_data = self.geometry.GetPointData().GetArray(self.max_radius_array_name)
        start_cid = min(section_pids.keys())
        start_pids = section_pids[start_cid]
        start_pid = start_pids[0] 
        start_pt = points.GetPoint(start_pid)
        start_radius = max_radius_data.GetValue(start_pid) 
        print("start_cid: {0:d}".format(start_cid))
        print("start_pid: {0:d}".format(start_pid))
        print("start_radius: {0:g}".format(start_radius))

        #for cid in section_pids:
        #    print("### " + str(section_pids[cid]))

        ## Remove the surface at the start of the centerlines.
        surface = self.surface
        clipped_surface = self.remove_surface_start(surface, start_pt, start_radius, start_pids)

        ## Slice off the surface at the ends of the centerlines.
        print("[create_caps] Create end caps ...")
        for cid in section_pids:
            print("Cid: {0:d}".format(cid))
            pids = section_pids[cid]
            print("   Number of pids: {0:d}".format(len(pids)))
            end_pid = pids[-1] 
            end_radius = max_radius_data.GetValue(end_pid) 
            print("   End pid: {0:d}".format(end_pid))
            print("   End radius: {0:g}".format(end_radius))
            clipped_surface = self.remove_surface_end(clipped_surface, end_pid, end_radius, pids)

        gr_geom = self.graphics.add_geometry(self.renderer, clipped_surface, color=[1.0, 1.0, 0.0])
        gr_geom.GetProperty().SetRepresentationToWireframe()
        return clipped_surface 

    def remove_surface_end(self, surface, end_pid, end_radius, pids):
        '''Remove the portion of the surface at the end of the centerlines.
        '''
        print("   ---- remove_surface_end ----")
        points = self.geometry.GetPoints()
        end_pt = points.GetPoint(end_pid) 
        for i in reversed(range(len(pids))):
            pid = pids[i]
            #print("   i: {0:d}".format(i))
            #print("   pid: {0:d}".format(pid))
            pt = points.GetPoint(pid)
            d = sqrt(sum([(pt[j]-end_pt[j])**2 for j in range(3)]))
            #print("  d: {0:g}".format(d), end = '')
            if d >= end_radius + self.end_offset:
                plane_pt = pt
                plane_pid = pid
                plane_pid_index = i
                break

        print("   plane_pid_index: {0:d}".format(plane_pid_index))
        print("   plane_pid: {0:d}".format(plane_pid))
        print("   plane_pt: {0:s}".format(str(plane_pt)))
        gr_geom = self.graphics.add_sphere(self.renderer, plane_pt, 0.1, color=[1.0, 1.0, 0.0])
        gr_geom.GetProperty().SetRepresentationToWireframe()

        pt1 = points.GetPoint(pids[plane_pid_index-1])
        pt2 = points.GetPoint(plane_pid)
        normal = [(pt2[i]-pt1[i]) for i in range(3)]
        vtk.vtkMath.Normalize(normal)
        slice_plane = vtk.vtkPlane()
        slice_plane.SetOrigin(plane_pt[0], plane_pt[1], plane_pt[2])
        slice_plane.SetNormal(normal[0], normal[1], normal[2])
        self.show_plane(plane_pt, normal, color=[1,0,0])

        sphere = vtk.vtkSphereSource()
        sphere.SetCenter(plane_pt)
        sphere.SetRadius(end_radius)
        sphere.Update()
        bounds = 6*[0.0]
        sphere.GetOutput().GetBounds(bounds)
        slice_planes = vtk.vtkPlanes()
        slice_planes.SetBounds(bounds)
        print("   Number of planes: {0:d}".format(slice_planes.GetNumberOfPlanes()))

        ## Clip the surface.
        box_func = self.compute_box_func(normal, plane_pt, end_radius)
        clipped_surface = self.clip_surface(surface, box_func)
        return clipped_surface

    def remove_surface_start(self, surface, start_pt, start_radius, start_pids):
        '''Remove the portion of the surface at the start of the centerlines.
        '''
        ## Find point to place start slice plane.
        points = self.geometry.GetPoints()
        print("Find point to place start slice plane ... ")
        for i,pid in enumerate(start_pids):
            #print("  pid: {0:d}".format(pid), end = '')
            pt = points.GetPoint(pid)
            d = sqrt(sum([(pt[j]-start_pt[j])**2 for j in range(3)]))
            #print("  d: {0:g}".format(d), end = '')
            if d >= start_radius + self.end_offset:
                plane_pt = pt
                plane_pid = pid
                plane_pid_index = i
                break 
        #_for i,pid in enumerate(start_pids)

        print("plane_pid_index: {0:d}".format(plane_pid_index))
        print("plane_pid: {0:d}".format(plane_pid))
        print("plane_pt: {0:s}".format(str(plane_pt)))
        gr_geom = self.graphics.add_sphere(self.renderer, plane_pt, 0.1, color=[1.0, 1.0, 0.0])
        gr_geom.GetProperty().SetRepresentationToWireframe()

        if plane_pid_index == 0:
            plane_pid_index += 1
        pt1 = points.GetPoint(start_pids[plane_pid_index-1])
        pt2 = points.GetPoint(plane_pid)
        normal = [(pt1[i]-pt2[i]) for i in range(3)]
        #normal = [(pt2[i]-pt1[i]) for i in range(3)]
        vtk.vtkMath.Normalize(normal)
        slice_plane = vtk.vtkPlane()
        slice_plane.SetOrigin(plane_pt[0], plane_pt[1], plane_pt[2])
        slice_plane.SetNormal(normal[0], normal[1], normal[2])
        self.show_plane(plane_pt, normal, color=[0,1,0])

        '''
        sphere = vtk.vtkSphereSource()
        sphere.SetCenter(plane_pt)
        sphere.SetRadius(start_radius)
        sphere.Update()
        bounds = 6*[0.0]
        sphere.GetOutput().GetBounds(bounds)
        slice_planes = vtk.vtkPlanes()
        slice_planes_pts = vtk.vtkPoints()
        print("   Number of planes: {0:d}".format(slice_planes.GetNumberOfPlanes()))
        for i in range(slice_planes.GetNumberOfPlanes()):
            plane = slice_planes.GetPlane(i)
            self.show_plane(plane.GetOrigin(), plane.GetNormal(), color=[1,0,1])
        '''

  
        ## Extract slice from the suraface.
        cutter = vtk.vtkCutter()
        cutter.SetCutFunction(slice_plane)
        cutter.SetInputData(surface)
        cutter.Update()
        sliced_surface = cutter.GetOutput()
        self.graphics.add_geometry(self.renderer, sliced_surface, color=[1.0, 1.0, 0.0])

        ## Clip the surface.
        box_func = self.compute_box_func(normal, plane_pt, start_radius)
        clipped_surface = self.clip_surface(surface, box_func)
        return clipped_surface 

    def compute_box_func(self, normal, plane_pt, radius):
        '''Compute a implicit function for a bounding box. 
        '''
        v = 3*[0.0]
        v[0] = vtk.vtkMath.Random(-10,10)
        v[1] = vtk.vtkMath.Random(-10,10)
        v[2] = vtk.vtkMath.Random(-10,10)
        v1 = 3*[0.0]
        vtk.vtkMath.Cross(normal, v, v1);
        vtk.vtkMath.Normalize(v1);
        v2 = 3*[0.0]
        vtk.vtkMath.Cross(normal, v1, v2);

        matrix = vtk.vtkMatrix4x4()
        matrix.Identity()
        for i in range(3):
            matrix.SetElement(i, 0, normal[i])
            matrix.SetElement(i, 1, v1[i])
            matrix.SetElement(i, 2, v2[i])

        sphere = vtk.vtkSphereSource()
        rscale = 2.0
        sphere_center = [plane_pt[i]+rscale*radius*normal[i] for i in range(3)]
        sphere.SetCenter(sphere_center)
        sphere.SetRadius(rscale*radius)
        sphere.Update()
        bounds = 6*[0.0]
        sphere.GetOutput().GetBounds(bounds)

        box_func = vtk.vtkBox()
        box_func.SetBounds(bounds)

        transform = vtk.vtkTransform()
        transform.Translate(sphere_center)
        #transform.Translate(plane_pt[0], plane_pt[1], plane_pt[2])
        transform.Concatenate(matrix)
        transform.Scale(1.0, 1.0, 1.0)
        transform.Translate(-sphere_center[0], -sphere_center[1], -sphere_center[2])
        #transform.Translate(-plane_pt[0], -plane_pt[1], -plane_pt[2])
        transform.Update()
        inverse_transform = transform.GetInverse()

        #ipt = transform.TransformPoint(plane_pt)
        ipt = inverse_transform.TransformPoint(plane_pt)

        box_func.SetBounds(bounds)
        #box.SetTransform(transform)
        box_func.SetTransform(inverse_transform)

        cube = vtk.vtkCubeSource()
        cube.SetBounds(bounds)
        cube.Update()
        cube_pd = cube.GetOutput()
        transform_pd = vtk.vtkTransformPolyDataFilter()
        #transform = vtk.vtkTransform()
        #transform.Translate(plane_pt[0], plane_pt[1], plane_pt[2])
        #transform.Scale(1.0, 1.0, 1.0)
        #transform_pd.SetTransform(inverse_transform);
        transform_pd.SetTransform(transform);
        transform_pd.SetInputData(cube_pd)
        transform_pd.Update()
        gr_geom = self.graphics.add_geometry(self.renderer, transform_pd.GetOutput(), color=[1.0, 0.0, 1.0])
        gr_geom.GetProperty().SetRepresentationToWireframe()
        return box_func

    def clip_surface(self, surface, slice_plane):
        '''Clip a surface.
        '''
        clip_filter = vtk.vtkClipPolyData()
        clip_filter.SetInputData(surface)
        clip_filter.GenerateClippedOutputOn()
        clip_filter.SetClipFunction(slice_plane)
        clip_filter.Update()
        return clip_filter.GetOutput()

    def show_plane(self, origin, normal, color):
        plane = vtk.vtkPlaneSource()
        plane.SetCenter(origin)
        plane.SetNormal(normal)
        plane.Update()
        plane_pd = plane.GetOutput()
        self.graphics.add_geometry(self.renderer, plane_pd, color)

    def extract_sections(self, centerlines, ids, cid):
        '''Extract a section of the centerlines geometry for the given ID.
        '''
        thresh = vtk.vtkThreshold()
        thresh.SetInputData(centerlines)
        thresh.ThresholdBetween(cid, cid)
        thresh.SetInputArrayToProcess(0, 0, 0, "vtkDataObject::FIELD_ASSOCIATION_CELLS", self.cids_array_name)
        thresh.Update()

        surfacefilter = vtk.vtkDataSetSurfaceFilter()
        surfacefilter.SetInputData(thresh.GetOutput())
        surfacefilter.Update()
        return surfacefilter.GetOutput()

    def compute_length_scale(self):
        pt1 = 3*[0.0]
        pt2 = 3*[0.0]
        avg_d = 0.0
        num_pts = self.geometry.GetNumberOfPoints()
        points = self.geometry.GetPoints()
        for i in range(num_pts-1):
            points.GetPoint(i,pt1)
            points.GetPoint(i+1,pt2)
            dx = pt1[0] - pt2[0]
            dy = pt1[1] - pt2[1]
            dz = pt1[2] - pt2[2]
            d = sqrt(dx*dx + dy*dy + dz*dz)
            avg_d += d
        self.length_scale = avg_d / num_pts



