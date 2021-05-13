#!/usr/bin/env python

from math import sqrt
import vtk

class Region(object):
    '''The Region class is used to store a flat region of a surface.
    '''
    def __init__(self, surface, cell_ids):
        self.surface = surface 
        self.cell_ids = cell_ids
        self.node_id = None 
        self.cell_id = None 
        self.area = 0.0
        self.max_radius = 0.0

        self.compute_properties()

    def compute_properties(self):
        points = self.surface.geometry.GetPoints()
        center = 3*[0.0]
        cell_ids = self.cell_ids 

        ## Compute the total area of the regions cells.
        #
        total_area = 0.0

        for cell_id in cell_ids:
            cell = self.surface.geometry.GetCell(cell_id)
            cell_pids = cell.GetPointIds()
            pid1 = cell_pids.GetId(0)
            pt1 = points.GetPoint(pid1)
            pid2 = cell_pids.GetId(1)
            pt2 = points.GetPoint(pid2)
            pid3 = cell_pids.GetId(2)
            pt3 = points.GetPoint(pid3)
            cell_center = [(pt1[i] + pt2[i] + pt3[i]) / 3.0 for i in range(3)]
            center[0] += cell_center[0]
            center[1] += cell_center[1]
            center[2] += cell_center[2]
            area = vtk.vtkTriangle.TriangleArea(pt1, pt2, pt3)
            total_area += area

        self.center = [center[i] / len(cell_ids) for i in range(3)]
        self.area = total_area 

        ## Compute the maximum radius and rind the node and 
        #  cell IDs for the end point. 
        #
        max_r = 0.0
        center = self.center 
        min_dist = 1e6
        node_id = 0
        cell_id = 0

        for cell_id in cell_ids:
            cell = self.surface.geometry.GetCell(cell_id)
            cell_pids = cell.GetPointIds()
            pid1 = cell_pids.GetId(0)
            pt1 = points.GetPoint(pid1)
            pid2 = cell_pids.GetId(1)
            pt2 = points.GetPoint(pid2)
            pid3 = cell_pids.GetId(2)
            pt3 = points.GetPoint(pid3)

            r1 = sqrt(sum([(pt1[i]-center[i])*(pt1[i]-center[i])  for i in range(3)]))
            r2 = sqrt(sum([(pt2[i]-center[i])*(pt2[i]-center[i])  for i in range(3)]))
            r3 = sqrt(sum([(pt3[i]-center[i])*(pt3[i]-center[i])  for i in range(3)]))
            if r1 > max_r:
                max_r = r1
            if r2 > max_r:
                max_r = r2
            if r3 > max_r:
                max_r = r3

            if r1 < min_dist:
                min_dist = r1
                node_id = pid1
                cell_id = cell_id
            if r2 < min_dist:
                min_dist = r2
                node_id = pid2
                cell_id = cell_id
            if r3 < min_dist:
                min_dist = r3
                node_id = pid3
                cell_id = cell_id

        self.max_radius = max_r
        self.node_id = node_id
        self.cell_id = cell_id

    def show(self, color):
        '''Show the set of cells found for a flat regions.
        '''
        points = self.surface.geometry.GetPoints()
        cell_ids = self.cell_ids 
        radius = self.surface.length_scale
        num_pts = len(cell_ids)
        cell_points = vtk.vtkPoints()
        cell_points.SetNumberOfPoints(num_pts)

        for i,cell_id in enumerate(cell_ids):
            cell = self.surface.geometry.GetCell(cell_id)
            cell_pids = cell.GetPointIds()
            pid1 = cell_pids.GetId(0)
            pt1 = points.GetPoint(pid1)
            pid2 = cell_pids.GetId(1)
            pt2 = points.GetPoint(pid2)
            pid3 = cell_pids.GetId(2)
            pt3 = points.GetPoint(pid3)
            center = [(pt1[i] + pt2[i] + pt3[i]) / 3.0 for i in range(3)]
            #self.graphics.add_sphere(self.renderer, center, radius, color=color, wire=True)
            cell_points.SetPoint(i, center[0], center[1], center[2])

        self.surface.graphics.add_glyph_points(self.surface.renderer, cell_points, color=color)
        self.surface.graphics.add_sphere(self.surface.renderer, self.center, radius, color=color, wire=True)
