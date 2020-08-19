#!/usr/bin/env python

from os import path
import vtk

class Image(object):

    def __init__(self):
        self.file_name = None
        self.volume = None
        self.visualization = None
        self.paths = None
        self.greyscale_lut = None
        self.hue_lut = None 
        self.sat_lut = None
        self.colors = vtk.vtkNamedColors()

    def create_greyscale_lut(self, scalar_range):
        imin = scalar_range[0]
        imax = scalar_range[1]
        table = vtk.vtkLookupTable()
        table.SetRange(imin, imax) # image intensity range
        table.SetValueRange(0.0, 1.0) # from black to white
        table.SetSaturationRange(0.0, 0.0) # no color saturation
        table.SetRampToLinear()
        table.Build()
        self.greyscale_lut = table

    def create_hue_lut(self, scalar_range):
        ''' Create a lookup table that consists of the full hue circle (from HSV).
        '''
        imin = scalar_range[0]
        imax = scalar_range[1]
        table = vtk.vtkLookupTable()
        table.SetTableRange(imin, imax)
        table.SetHueRange(0, 1)
        table.SetSaturationRange(1, 1)
        table.SetValueRange(1, 1)
        table.Build()
        self.hue_lut = table

    def create_sat_lut(self, scalar_range):
        imin = scalar_range[0]
        imax = scalar_range[1]
        table = vtk.vtkLookupTable()
        table.SetTableRange(imin, imax)
        table.SetHueRange(.6, .6)
        table.SetSaturationRange(0, 1)
        table.SetValueRange(1, 1)
        table.Build()
        self.sat_lut = table

    def read_volume(self, file_name):
        ''' Read in a 3D image volume.
        '''
        filename, file_extension = path.splitext(file_name)
        reader = None
        if file_extension == ".vti":
            reader = vtk.vtkXMLImageDataReader()
        reader.SetFileName(file_name)
        reader.Update()
        self.volume = reader.GetOutput()

        self.extent = self.volume.GetExtent()
        self.width = self.extent[1] - self.extent[0]
        self.height = self.extent[3] - self.extent[2]
        self.depth = self.extent[5] - self.extent[4]
        self.scalar_range = self.volume.GetScalarRange()
        self.dimensions = self.volume.GetDimensions()
        self.spacing = self.volume.GetSpacing()
        self.origin = self.volume.GetOrigin()
        self.bounds = self.volume.GetBounds()
        self.scalars = self.volume.GetPointData().GetScalars()

        self.create_greyscale_lut((0,200))
        #self.create_greyscale_lut(self.scalar_range)
        self.create_hue_lut(self.scalar_range)
        self.create_sat_lut(self.scalar_range)

        '''
        image_point_data = imageDataVTK.GetPointData()
        image_data = vtkNumPy.vtk_to_numpy(image_point_data.GetArray(0))
        '''

        print("Volume: ")
        print("  dimensions: %s" % str(self.dimensions))
        print("  extent: %s" % str(self.extent))
        print("  spacing: %s" % str(self.spacing))
        print("  origin: %s" % str(self.origin))
        print("  bounds: %s" % str(self.bounds))
        print("  width: %d" % self.width)
        print("  height: %d" % self.height)
        print("  depth: %d" % self.depth)
        print("  scalar_range: %s" % str(self.scalar_range))

        #self.graphics.add_sphere(self.origin, radius=0.2)

        x0, y0, z0 = self.origin
        xSpacing, ySpacing, zSpacing = self.spacing
        xMin, xMax, yMin, yMax, zMin, zMax = self.extent
        center = [x0 + 0.5*xSpacing * (xMax-1), y0 + 0.5*ySpacing * (yMax-1), z0 + 0.5*zSpacing * (zMax-1)]
        #self.graphics.add_sphere(center, radius=0.1, color=[1.0,0.0,0.0])

    def display_edges(self):
        outline = vtk.vtkOutlineFilter()
        outline.SetInputData(self.volume)
        outline.Update()

        mapper = vtk.vtkDataSetMapper()
        mapper.SetInputData(outline.GetOutput())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetRepresentationToWireframe()
        actor.GetProperty().SetColor(self.colors.GetColor3d("Black"))
        self.visualization.add_actor(actor)

    def display_axis_slice(self, axis, index):
        slice_colors = vtk.vtkImageMapToColors()
        slice_colors.SetInputData(self.volume)
        slice_colors.SetLookupTable(self.greyscale_lut)
        #slice_colors.SetLookupTable(self.hue_lut)
        #slice_colors.SetLookupTable(self.sat_lut)
        slice_colors.Update()

        slice = vtk.vtkImageActor()
        slice.GetMapper().SetInputData(slice_colors.GetOutput())

        if axis == 'i':
            imin = index 
            imax = index
            jmin = 0
            jmax = self.height
            kmin = 0
            kmax = self.depth

        elif axis == 'j':
            imin = 0
            imax = self.width
            jmin = index
            jmax = index 
            kmin = 0
            kmax = self.depth

        elif axis == 'k':
            imin = 0
            imax = self.width
            jmin = 0
            jmax = self.height
            kmin = index
            kmax = index 

        slice.SetDisplayExtent(imin, imax, jmin,jmax, kmin,kmax);
        slice.ForceOpaqueOn()
        slice.PickableOff()
        self.visualization.add_actor(slice)

    def extract_slice_gut(self, origin, tangent, normal, binormal):
        '''
        This works but can't clip slice.
        '''
        print(" ")
        print("---------- Image Extract Slice ----------") 
        print("origin: " + str(origin))
        print("tangent: " + str(tangent))
        print("normal: " + str(normal))
        print("binormal: " + str(binormal))

        # Define the slice plane.
        slice_plane = vtk.vtkPlane()
        slice_plane.SetOrigin(origin[0], origin[1], origin[2])
        slice_plane.SetNormal(tangent[0], tangent[1], tangent[2])

        ## Create a mapper that slice a 3D image with an abitrary slice plane 
        #  and draw the results on the screen. 
        #
        reslice_mapper = vtk.vtkImageResliceMapper() 
        reslice_mapper.SetInputData(self.volume) 
        reslice_mapper.SliceFacesCameraOff()
        reslice_mapper.SliceAtFocalPointOff()
        reslice_mapper.SetSlicePlane(slice_plane)
        reslice_mapper.Update()

        ## vtkImageSlice is used to represent an image in a 3D scene. 
        #
        image_slice = vtk.vtkImageSlice() 
        image_slice.SetMapper(reslice_mapper) 
        image_slice.Update()
        self.visualization.add_actor(image_slice)
        print("Image slice: ")
        bounds = 6*[0]
        image_slice.GetBounds(bounds)
        print("  Bounds: " + str(bounds))
        #print(str(image_slice))

        ## Show slice bounds.
        #
        imageBoundsCube = vtk.vtkCubeSource()
        imageBoundsCube.SetBounds(self.bounds)
        imageBoundsCube.Update()
        #
        cutter = vtk.vtkCutter()
        cutter.SetCutFunction(slice_plane);
        cutter.SetInputData(imageBoundsCube.GetOutput());
        cutter.Update()
        cutterMapper = vtk.vtkPolyDataMapper()
        cutterMapper.SetInputData(cutter.GetOutput())
        #
        planeBorder = vtk.vtkActor()
        planeBorder.GetProperty().SetColor(1.0, 1.0, 0)
        planeBorder.GetProperty().SetOpacity(1.0)
        planeBorder.GetProperty().SetLighting(0)
        planeBorder.GetProperty().SetLineWidth(4)
        planeBorder.SetMapper(cutterMapper)
        self.visualization.add_actor(planeBorder)

    def extract_slice(self, origin, tangent, normal, binormal):
        print(" ")
        print("---------- Image Extract Slice ----------") 
        print("origin: " + str(origin))
        print("tangent: " + str(tangent))
        print("normal: " + str(normal))
        print("binormal: " + str(binormal))

        # Define the slice plane.
        slice_plane = vtk.vtkPlane()
        slice_plane.SetOrigin(origin[0], origin[1], origin[2])
        slice_plane.SetNormal(tangent[0], tangent[1], tangent[2])

        ## Show slice bounds.
        #
        imageBoundsCube = vtk.vtkCubeSource()
        imageBoundsCube.SetBounds(self.bounds)
        imageBoundsCube.Update()
        #
        cutter = vtk.vtkCutter()
        cutter.SetCutFunction(slice_plane);
        cutter.SetInputData(imageBoundsCube.GetOutput());
        cutter.Update()
        cutterMapper = vtk.vtkPolyDataMapper()
        cutterMapper.SetInputData(cutter.GetOutput())
        #
        planeBorder = vtk.vtkActor()
        planeBorder.GetProperty().SetColor(1.0, 1.0, 0)
        planeBorder.GetProperty().SetOpacity(1.0)
        planeBorder.GetProperty().SetLighting(0)
        planeBorder.GetProperty().SetLineWidth(4)
        planeBorder.SetMapper(cutterMapper)
        #self.graphics.add_actor(planeBorder)

        ## Interpolate slice plane points.
        #
        xSpacing, ySpacing, zSpacing = self.spacing
        w = 40.0 * xSpacing
        num_u = 200
        num_v = 200
        u = normal
        v = binormal
        pt0 = origin - w*(u + v)
        print("pt0: " + str(pt0))
        du = 2*w / num_u
        dv = 2*w / num_v
        
        points = vtk.vtkPoints()
        for j in range(num_v):
            for i in range(num_u):
                pt = pt0 + i*du*u + j*dv*v
                #print("{0:d}  {1:d}  pt {2:s}".format(i, j, str(pt)))
                points.InsertNextPoint(pt[0], pt[1], pt[2])
        #_for j in range(num_v)

        ## Outline slice.
        pt1 = pt0 + 0*du*u + 0*dv*v
        pt2 = pt0 + 0*du*u + (num_v-1)*dv*v
        self.visualization.add_line(pt1, pt2, color=[1.0,1.0,0.0], width=5)
        pt1 = pt2 
        pt2 = pt0 + (num_u-1)*du*u + (num_v-1)*dv*v
        self.visualization.add_line(pt1, pt2, color=[1.0,1.0,0.0], width=5)
        pt1 = pt2 
        pt2 = pt0 + (num_u-1)*du*u + 0*dv*v
        self.visualization.add_line(pt1, pt2, color=[1.0,1.0,0.0], width=5)
        pt1 = pt2 
        pt2 = pt0 + 0*du*u + 0*dv*v
        self.visualization.add_line(pt1, pt2, color=[1.0,1.0,0.0], width=5)

        pts_polydata = vtk.vtkPolyData()
        pts_polydata.SetPoints(points)

        probe = vtk.vtkProbeFilter()
        probe.SetSourceData(self.volume)
        probe.SetInputData(pts_polydata)
        probe.Update()

        data = probe.GetOutput().GetPointData().GetScalars()
        num_values = data.GetNumberOfTuples()
        values = vtk.vtkDoubleArray()
        values.SetNumberOfValues(num_values);
  
        print("Interpolated data:")
        for i in range(data.GetNumberOfTuples()):
            val = data.GetValue(i)
            values.SetValue(i, val);
            #print(val)

        ## Show interpolation points.
        vertexFilter = vtk.vtkVertexGlyphFilter()
        vertexFilter.SetInputData(pts_polydata)
        vertexFilter.Update()

        polydata = vtk.vtkPolyData()
        polydata.ShallowCopy(vertexFilter.GetOutput())
        polydata.GetPointData().SetScalars(values)
        print("Scalar range: " + str(polydata.GetScalarRange()))

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(polydata)
        mapper.SetLookupTable(self.greyscale_lut)
        mapper.SetScalarRange(polydata.GetScalarRange())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetPointSize(2)
        #actor.GetProperty().SetColor(1.0, 1.0, 0.0)
        self.visualization.add_actor(actor)



