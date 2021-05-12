#!/usr/bin/env python

from collections import defaultdict
from math import sqrt
from math import pi
from math import acos
from os import path
import vtk

class Branch(object):
    """The Branch class stores data for a centerline branch.
    """
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
