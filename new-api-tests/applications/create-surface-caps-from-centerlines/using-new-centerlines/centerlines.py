#!/usr/bin/env python

from collections import defaultdict
from math import sqrt
from math import pi
from math import acos
from os import path
import vtk

class Branch(object):
    '''Attributes:
    '''
    def __init__(self, cid, geometry, end_point_ids, end_cell_ids):
        self.cid = cid                    
        self.geometry = geometry 
        self.end_point_ids = end_point_ids
        self.end_cell_ids = end_cell_ids
        self.renderer = None
        self.graphics = None
        self.length_scale = None

    def show(self, renderer, graphics, color, line_width, radius):
        graphics.add_geometry(renderer, self.geometry, color=color, line_width=line_width)
        for pid in self.end_point_ids:
            pt = self.geometry.GetPoints().GetPoint(pid)
            graphics.add_sphere(renderer, pt, radius, color=color, wire=True)

    def remove_surface_end(self, centerlines, surface, max_radius_data, normal_data):
        '''Remove the portion of the surface at the end of the centerlines.
        '''
        print("\n========== Branch.remove_surface_end ==========")
        print("[Branch.remove_surface_end] end_point_ids: {0:s}".format(str(self.end_point_ids)))
        print("[Branch.remove_surface_end] end_cell_ids: {0:s}".format(str(self.end_cell_ids)))
        points = self.geometry.GetPoints()
        #end_pt = points.GetPoint(end_pid)
        #pt = self.geometry.GetPoints().GetPoint(pid)
        #radius = max_radius_data.GetValue(pid) 
        clipped_surface = surface
        for end_pid in self.end_point_ids:
            end_pt = points.GetPoint(end_pid)
            start_pid = None
     
            for cell_id in self.end_cell_ids:
                print("[Branch.remove_surface_end] ----- cell_id {0:d} -----".format(cell_id))
                cell = centerlines.GetCell(cell_id)
                cell_pids = cell.GetPointIds()
                pid1 = cell_pids.GetId(0)
                pid2 = cell_pids.GetId(1)
                print("[Branch.remove_surface_end] cell_pids: {0:d}  {1:d}".format(pid1, pid2))
                if pid1 == end_pid:
                    start_pid = pid2
                    break
                elif pid2 == end_pid:
                    start_pid = pid1
                    break
            print("[Branch.remove_surface_end] start_pid: {0:d}".format(start_pid))
            print("[Branch.remove_surface_end] end_pid: {0:d}".format(end_pid))
            start_pt = points.GetPoint(start_pid)

            start_radius = max_radius_data.GetValue(start_pid)
            end_radius = max_radius_data.GetValue(end_pid)
            avg_radius = (start_radius + end_radius) / 2.0
            print("[Branch.remove_surface_end] start_radius: {0:g}".format(start_radius))
            print("[Branch.remove_surface_end] end_radius: {0:g}".format(end_radius))

            if self.renderer:
                radius = self.length_scale 
                self.graphics.add_sphere(self.renderer, start_pt, radius, color=[0.5, 0.5, 0.5], wire=True)

            pt_normal = [(end_pt[i]-start_pt[i]) for i in range(3)]
            length = vtk.vtkMath.Norm(pt_normal)
            vtk.vtkMath.Normalize(pt_normal)

            normal = [normal_data.GetComponent(start_pid,i) for i in range(3)]
            dist_factor = 0.15
            dp = sum([pt_normal[i]*normal[i] for i in range(3)])
            print("[Branch.remove_surface_end] dp: {0:g}".format(dp))
            if dp < 0.0:
                normal = [-x for x in normal]
            plane_pt = [(start_pt[i] + dist_factor*start_radius*normal[i]) for i in range(3)]

            print("[Branch.remove_surface_end] plane_pt: {0:s}".format(str(plane_pt)))
            slice_plane = vtk.vtkPlane()
            slice_plane.SetOrigin(plane_pt[0], plane_pt[1], plane_pt[2])
            slice_plane.SetNormal(normal[0], normal[1], normal[2])
            self.show_plane(plane_pt, normal, color=[1,0,0])

            # Set the dimensions of the clipping box.
            start_radius = max_radius_data.GetValue(start_pid) 
            end_radius = max_radius_data.GetValue(end_pid) 
            sphere = vtk.vtkSphereSource()
            sphere.SetCenter(plane_pt)
            sphere.SetRadius(end_radius)
            sphere.Update()
            bounds = 6*[0.0]
            sphere.GetOutput().GetBounds(bounds)
            slice_planes = vtk.vtkPlanes()
            slice_planes.SetBounds(bounds)

            # Clip the surface.
            box_func = self.compute_box_func(normal, plane_pt, end_radius)
            clipped_surface = self.clip_surface(clipped_surface, box_func)
        #_for end_pid in self.end_point_ids
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
        if not self.renderer:
            return
        plane = vtk.vtkPlaneSource()
        plane.SetCenter(origin)
        plane.SetNormal(normal)
        plane.Update()
        plane_pd = plane.GetOutput()
        self.graphics.add_geometry(self.renderer, plane_pd, color)

class Centerlines(object):
    '''The Centerlines class defines methods for operations based on centerlines geometry.
    '''
    def __init__(self):
        self.cids_array_name = "CenterlineId"
        self.max_radius_array_name = "MaximumInscribedSphereRadius"
        self.normal_array_name = "CenterlineSectionNormal"
        self.graphics = None
        self.renderer = None
        self.geometry = None
        self.surface = None
        self.ends_node_ids = None    # The centerlines ends node IDs.
        self.branches = None         # The branches extracted from the centerlines.
        self.cid_list = None 
        self.longest_cid = None
        self.lut = None       
        self.length_scale = 1.0
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
        self.get_end_points()
        self.extract_branches()

    def get_end_points(self):
        '''Get the node IDs for the ends of the centerlines.
        '''
        num_lines = self.geometry.GetNumberOfLines()
        id_hash = defaultdict(int)
        for i in range(num_lines):
            cell = self.geometry.GetCell(i)
            cell_pids = cell.GetPointIds()
            num_ids = cell_pids.GetNumberOfIds()
            pid1 = cell_pids.GetId(0)
            pid2 = cell_pids.GetId(1)
            id_hash[pid1] += 1
            id_hash[pid2] += 1

        points = self.geometry.GetPoints()
        end_ids = []

        for pid in id_hash:
            if id_hash[pid] == 1:
                #print("get_end_points] End point: {0:d}".format(pid))
                end_ids.append(pid)
                #pt = points.GetPoint(pid)
                #gr.add_sphere(renderer, pt, 0.5, color=[1,1,1], wire=True)

        print("[get_end_points] Number of centerline ends: {0:d}".format(len(end_ids)))
        self.ends_node_ids = end_ids

    def write_clipped_surface(self, surface, file_name):
        '''Write a clipped surface to a .vtp file.
        '''
        writer = vtk.vtkXMLPolyDataWriter()
        writer.SetFileName(file_name)
        writer.SetInputData(surface)
        writer.Update()
        writer.Write()

    def extract_branches(self):
        '''Extract branches from the centerlines based on CenterlinesIds.
        '''
        print("========== extract_branches ==========")
        data_array = self.geometry.GetPointData().GetArray(self.cids_array_name)
        num_centerlines = self.get_centerline_info()
        min_id = 0
        max_id = num_centerlines-1
        cid_list = list(range(min_id,max_id+1))
        print("[extract_branches] Centerline IDs: {0:s}".format(str(cid_list)))
        self.cid_list = cid_list 

        # Create a color lookup table for branch geometry.
        self.lut = vtk.vtkLookupTable()
        self.lut.SetTableRange(min_id, max_id+1)
        self.lut.SetHueRange(0, 1)
        self.lut.SetSaturationRange(1, 1)
        self.lut.SetValueRange(1, 1)
        self.lut.Build()

        max_radius_data = self.geometry.GetPointData().GetArray(self.max_radius_array_name)
        num_lines = self.geometry.GetNumberOfLines()
        num_points = self.geometry.GetNumberOfPoints()
        points = self.geometry.GetPoints()
        print("Number of centerline lines: {0:d}".format(num_lines))
        print("Number of centerline points: {0:d}".format(num_points))

        # Find the longest branch.
        max_num_lines = 0
        longest_cid = None
        for cid in range(min_id,max_id+1):
            branch_geom = self.extract_branch_geom(cid)
            if branch_geom.GetNumberOfLines() > max_num_lines:
                max_num_lines = branch_geom.GetNumberOfLines()
                longest_cid = cid
        print("\nLongest branch cid: {0:d}  Number of lines: {1:d}".format(longest_cid, max_num_lines))
        self.longest_cid = longest_cid 

        # Create cell_id -> centerline id map.
        cell_cids = defaultdict(list)
        for cid in cid_list:
            #print("\n---------- cid {0:d} ----------".format(cid))
            for i in range(num_lines):
                cell = self.geometry.GetCell(i)
                cell_pids = cell.GetPointIds()
                num_ids = cell_pids.GetNumberOfIds()
                pid1 = cell_pids.GetId(0)
                pid2 = cell_pids.GetId(1)
                value1 = int(data_array.GetComponent(pid1, cid))
                value2 = int(data_array.GetComponent(pid2, cid))
                if (value1 == 1) or (value2 == 1):
                    cell_cids[i].append(cid)
                #_for j in range(num_ids)
            #_for i in range(num_lines)
        #_for cid in range(min_id,max_id+1)

        # Determine branch cells.
        branch_cells = defaultdict(list)
        for cid in cid_list:
            for i in range(num_lines):
                cids = cell_cids[i]
                if longest_cid in cids:
                    if i not in branch_cells[longest_cid]:
                        branch_cells[longest_cid].append(i)
                else:
                    if (len(cids) == 1) and (cids[0] == cid):
                        branch_cells[cid].append(i)
                    if cid in cell_cids[i]:
                        cell_cids[i].remove(cid)
                #_for j in range(num_ids)
        #_for cid in cid_list

        # Create branch geomerty.
        self.branches = []
        end_point_ids = self.ends_node_ids
        for cid in cid_list:
            self.branches.append( self.create_branch(cid, branch_cells, end_point_ids) )

    def show_branches(self):
        radius = self.length_scale
        for branch in self.branches:
            color = [0.0, 0.0, 0.0]
            if branch.cid == self.longest_cid:
                color = [1.0, 1.0, 1.0]
                line_width = 4
            else:
                self.lut.GetColor(branch.cid, color)
                line_width = 2
            branch.show(self.renderer, self.graphics, color, line_width, radius)

    def create_branch(self, cid, branch_cells, end_point_ids):
        '''Create a branch from the centerlines.
        '''
        points = self.geometry.GetPoints()
        num_lines = self.geometry.GetNumberOfLines()

        ## Find ends of line.
        #
        branch_end_point_ids = []
        branch_end_cell_ids = []

        for cell_id in branch_cells[cid]:
            cell = self.geometry.GetCell(cell_id)
            cell_pids = cell.GetPointIds()
            num_ids = cell_pids.GetNumberOfIds()
            pid1 = cell_pids.GetId(0)
            pid2 = cell_pids.GetId(1)
            if pid1 in end_point_ids:
                start_cell = cell_id
                branch_end_point_ids.append(pid1)
                branch_end_cell_ids.append(cell_id)
            elif pid2 in end_point_ids:
                branch_end_point_ids.append(pid2)
                branch_end_cell_ids.append(cell_id)

        ## Create branch geometry.
        #
        branch_geom = vtk.vtkPolyData()
        branch_geom.SetPoints(points)
        branch_lines = vtk.vtkCellArray()
        #
        for cell_id in branch_cells[cid]:
            cell = self.geometry.GetCell(cell_id)
            cell_pids = cell.GetPointIds()
            num_ids = cell_pids.GetNumberOfIds()
            pid1 = cell_pids.GetId(0)
            pid2 = cell_pids.GetId(1)
            line = vtk.vtkLine()
            line.GetPointIds().SetId(0, pid1)
            line.GetPointIds().SetId(1, pid2)
            branch_lines.InsertNextCell(line)
        #
        branch_geom.SetLines(branch_lines)

        return Branch(cid, branch_geom, branch_end_point_ids, branch_end_cell_ids)

    def extract_branch_geom(self, cid):
        data_array = self.geometry.GetPointData().GetArray(self.cids_array_name)
        thresh = vtk.vtkThreshold()
        thresh.SetInputData(self.geometry)
        thresh.ThresholdBetween(1.0, 1.0)
        thresh.SetComponentModeToUseSelected()
        thresh.SetSelectedComponent(cid)
        #thresh.SetPassThroughCellIds(cell_ids)
        thresh.SetInputArrayToProcess(0, 0, 0, "vtkDataObject::FIELD_ASSOCIATION_POINTS", self.cids_array_name)
        thresh.Update()

        surfacefilter = vtk.vtkDataSetSurfaceFilter()
        surfacefilter.SetInputData(thresh.GetOutput())
        surfacefilter.Update()
        return surfacefilter.GetOutput()

    def get_centerline_info(self):
        data_array = self.geometry.GetPointData().GetArray(self.cids_array_name)
        num_comp = data_array.GetNumberOfComponents()
        return num_comp

    def remove_surface_ends(self): 
        '''Remove the ends of the surface.
        '''
        print("========== remove_surface_ends ==========")
        points = self.geometry.GetPoints()
        max_radius_data = self.geometry.GetPointData().GetArray(self.max_radius_array_name)
        normal_data = self.geometry.GetPointData().GetArray(self.normal_array_name)
        clipped_surface = self.surface

        for branch in self.branches:
            branch.renderer = self.renderer 
            branch.graphics = self.graphics 
            branch.length_scale = self.length_scale 
            clipped_surface = branch.remove_surface_end(self.geometry, clipped_surface, max_radius_data, normal_data)

        gr_geom = self.graphics.add_geometry(self.renderer, clipped_surface, color=[1.0, 1.0, 0.0])
        gr_geom.GetProperty().SetRepresentationToWireframe()
        return clipped_surface

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

