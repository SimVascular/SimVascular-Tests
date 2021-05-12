#!/usr/bin/env python

from os import path
import sv
import vtk

class Surface(object):
    """The surface class is used to store surface data.
    """
    def __init__(self, graphics=None, window=None, renderer=None):
        self.file_name = None
        self.file_prefix = None
        self.graphics = graphics
        self.window = window 
        self.renderer = renderer
        self.geometry = None
        self.centerlines_source_nodes = []
        self.centerlines_target_nodes = []
        self.centerlines = None

    def read(self, file_name):
        """Read in a surface from a .vtp or .vtk file.
        """
        file_prefix, file_extension = path.splitext(file_name)
        self.file_name = file_name
        self.file_prefix = file_prefix 

        if file_extension == '.vtk':
            reader = vtk.vtkPolyDataReader()
        elif file_extension == '.vtp':
            reader = vtk.vtkXMLPolyDataReader()
        else:
            raise Exception("Unsupported file format '{0:s}'".format(file_extension))

        reader.SetFileName(file_name)
        reader.Update()
        geometry = reader.GetOutput()

        kernel = sv.modeling.Kernel.POLYDATA
        modeler = sv.modeling.Modeler(kernel)
        model = modeler.read(file_name)
        try:
            face_ids = model.get_face_ids()
        except:
            face_ids = model.compute_boundary_faces(angle=60.0)
        print("Face IDs: {0:s}".format(str(face_ids)))
        self.geometry = model.get_polydata()

        '''
        self.geometry = geometry 

        cleaner = vtk.vtkCleanPolyData()
        cleaner.SetInputData(geometry);
        cleaner.PieceInvariantOn();
        cleaner.Update();
        self.geometry = cleaner.GetOutput()
        self.geometry.BuildLinks()
        '''

    def add_centerlines_source_node(self, **kwargs):
        '''Add a source node ID used for exctracting centerlines.
        '''
        node_id = int(kwargs['node_ids'][0])
        self.centerlines_source_nodes.append(node_id)

    def add_centerlines_target_node(self, **kwargs):
        '''Add a target node ID used for exctracting centerlines.
        '''
        node_id = int(kwargs['node_ids'][0])
        self.centerlines_target_nodes.append(node_id)

    def compute_centerlines(self, **kwargs):
        '''Compute the centerlines for the given list of node IDs.
        '''
        print('[surface] ========== compute_centerlines ==========')
        if len(self.centerlines_source_nodes) == 0:
            raise Exception("No source nodes have been selected for centerlines extraction.")

        if len(self.centerlines_target_nodes) == 0:
            raise Exception("No target nodes have been selected for centerlines extraction.")
       
        print('[surface] Source nodes: {0:s}'.format(str(self.centerlines_source_nodes)))
        print('[surface] Target nodes: {0:s}'.format(str(self.centerlines_target_nodes)))

        # Extract centerlines.
        surface = kwargs['surface']
        inlet_ids = self.centerlines_source_nodes 
        outlet_ids = self.centerlines_target_nodes 
        centerlines_polydata = sv.vmtk.centerlines(surface, inlet_ids, outlet_ids)
        #centerlines_polydata = sv.vmtk.centerlines(self.geometry, inlet_ids, outlet_ids)
        self.centerlines = centerlines_polydata
        if self.graphics != None and self.renderer != None:
            self.graphics.add_geometry(self.renderer, centerlines_polydata, color=[0.0, 0.8, 0.0], line_width=3)
            self.window.Render()

        # Write centerlines.
        file_prefix = self.file_prefix
        file_name = file_prefix+"-centerlines.vtp"
        writer = vtk.vtkXMLPolyDataWriter()
        writer.SetFileName(file_name)
        writer.SetInputData(centerlines_polydata)
        writer.Update()
        writer.Write()
        print("[surface] Centerlines geometry has been written to '{0:s}'".format(file_name))



