#!/usr/bin/env python

from branch import Branch
from collections import defaultdict
from math import sqrt
from math import pi
from math import acos
from os import path
import sv
import vtk

class Centerlines(object):
    '''The Centerlines class defines methods for operations based on centerlines geometry.

       Attributes:
         surface: The Surface object from which the centerlines where computed.
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
        self.clip_distance = 0.0
        self.clip_width_scale = 1.0
        self.clipped_surface = None

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

        print("[centerlines] Number of centerline ends: {0:d}".format(len(end_ids)))
        self.ends_node_ids = end_ids

    def write_clipped_surface(self):
        '''Write a clipped surface to a .vtp file.
        '''
        file_name = self.surface.file_prefix + "-clipped.vtp"
        writer = vtk.vtkXMLPolyDataWriter()
        writer.SetFileName(file_name)
        writer.SetInputData(self.clipped_surface)
        writer.Update()
        writer.Write()
        print("[centerlines] Clipped geometry has been written to '{0:s}'".format(file_name))

    def extract_branches(self):
        '''Extract branches from the centerlines based on CenterlinesIds.
        '''
        print("[centerlines] ========== extract_branches ==========")
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
        print("[centerlines] Number of centerline lines: {0:d}".format(num_lines))
        print("[centerlines] Number of centerline points: {0:d}".format(num_points))

        # Find the longest branch.
        max_num_lines = 0
        longest_cid = None
        for cid in range(min_id,max_id+1):
            branch_geom = self.extract_branch_geom(cid)
            if branch_geom.GetNumberOfLines() > max_num_lines:
                max_num_lines = branch_geom.GetNumberOfLines()
                longest_cid = cid
        print("\n[centerlines] Longest branch cid: {0:d}  Number of lines: {1:d}".format(longest_cid, max_num_lines))
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

        branch_end_normals = []
        for pid in branch_end_point_ids:
            pt = points.GetPoint(pid)
            normal = self.surface.get_point_normal(pt)
            branch_end_normals.append(normal)

        #print("[centerlines] branch cid: {0:d}".format(cid))
        #print("[centerlines]   branch_end_point_ids: {0:s}".format(str(branch_end_point_ids)))
        #print("[centerlines]   branch_end_cell_ids: {0:s}".format(str(branch_end_cell_ids)))
        return Branch(cid, branch_geom, branch_end_point_ids, branch_end_cell_ids, branch_end_normals, 
                      self.clip_distance, self.clip_width_scale)

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

    def create_model(self, **kwargs): 
        '''Create a model by clipping the ends of a surface using centerlines data.

           A Surface object is passed in 'data'. This should have centerlines computed for it.
        '''
        print("[centerlines] ========== create_model ==========")
        surface_obj = kwargs['data']
        if surface_obj.centerlines == None:
            raise Exception("Centerlines have not been computed.")
        
        self.geometry = surface_obj.centerlines 
        self.file_prefix = surface_obj.file_prefix 

        # Compute the average polygons size for the surface.
        self.compute_length_scale()

        # Compute the centerines end points.
        self.get_end_points()

        # Extract branches from the centerlines.
        self.extract_branches()

        # Clip the ends of the surface.
        self.clipped_surface = self.remove_surface_ends() 
        self.write_clipped_surface()

        # Create a model from the clipped surface.
        self.create_capped_surface()

        #surface_obj.vtk_actor.GetProperty().SetOpacity(0.5)
        #surface_obj.vtk_actor.GetProperty().BackfaceCullingOff()
        #surface_obj.vtk_actor.GetProperty().SetRepresentationToPoints()
        surface_obj.vtk_actor.GetProperty().SetRepresentationToWireframe()


    def create_capped_surface(self):
        '''Create a capped surface from the clipped surface.
        '''
        print("[centerlines] ========== create_capped_surface ==========")
        clipped_surface = self.clipped_surface
        capped_surface = sv.vmtk.cap(surface=clipped_surface, use_center=True)
        self.graphics.add_geometry(self.renderer, capped_surface, color=[0.0, 1.0, 1.0])

        file_name = self.surface.file_prefix + "-capped.vtp"
        writer = vtk.vtkXMLPolyDataWriter()
        writer.SetFileName(file_name)
        writer.SetInputData(capped_surface)
        writer.Update()
        writer.Write()
        print("[centerlines] Capped geometry has been written to '{0:s}'".format(file_name))

    def remove_surface_ends(self): 
        '''Remove the ends of the surface.
        '''
        print("[centerlines] ========== remove_surface_ends ==========")
        points = self.geometry.GetPoints()
        max_radius_data = self.geometry.GetPointData().GetArray(self.max_radius_array_name)
        normal_data = self.geometry.GetPointData().GetArray(self.normal_array_name)
        clipped_surface = self.surface.geometry

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

