import os
import vtk

class MouseInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    ''' This class provides picking an actor.
    '''
    def __init__(self, visualizer):
        #self.AddObserver("LeftButtonPressEvent", self.leftButtonPressEvent)
        self.AddObserver("KeyPressEvent", self.onKeyPressEvent)
        self.AddObserver("CharEvent", self.onCharEvent)
        self.visualizer = visualizer 
        self.selected_points = []
        self.sphere = None

    def leftButtonPressEvent(self, obj, event):
        ''' Process left mouse button press.
        '''
        print("[MouseInteractorStyle] LeftButtonPressEvent ")
        clickPos = self.GetInteractor().GetEventPosition()

        # vtk.vtkCellPicker() does not select path lines.
        #picker = vtk.vtkCellPicker()
        picker = vtk.vtkPropPicker()
        picker.Pick(clickPos[0], clickPos[1], 0, self.renderer)
        #picker.SetTolerance(0.0001)
        if picker.GetActor() == None:
            return

        actor = picker.GetActor() 
        #print("[MouseInteractorStyle]   Actor: " + str(actor))
        cgeom = self.visualizer.actor_map[actor]
        print("[MouseInteractorStyle]   Name: " + str(cgeom.name))
        print("[MouseInteractorStyle]   Type: " + str(cgeom.source_type))
        position = picker.GetPickPosition()
        print("[MouseInteractorStyle]   Position: " + str(position))
        cgeom.process_select(position)

        if self.sphere == None:
            sphere = vtk.vtkSphereSource()
            sphere.SetCenter(position[0], position[1], position[2])
            sphere.SetRadius(0.1)
            sphere.Update()
            polydata = sphere.GetOutput()
            self.visualizer.add_polydata("pick_sphere", polydata, color=[0.0, 1.0, 0.0])
            self.sphere = sphere

        self.sphere.SetCenter(position[0], position[1], position[2])
        self.sphere.Update()
        '''
        ## Get path data at the selected point.
        for path in self.graphics.paths:
            path_data = path.select(position)
            print("  path data: ")
            print("    id: %s" %  path_data.id)
            print("    index: %d" %  path_data.index)
            print("    point: %s" %  str(path_data.point))
            print("    tangent: %s" %  str(path_data.tangent))
            print("    rotation: %s" %  str(path_data.rotation))

            # Show tangent.
            s = 1.0
            pt1 = path_data.point
            tangent = path_data.tangent
            tangent = np.array(path_data.tangent)
            pt2 = [(pt1[j]+s*tangent[j]) for j in range(0,3)] 
            self.graphics.add_line(pt1, pt2, width=5)

            # Show normal.
            normal = np.array(path_data.rotation)
            pt2 = [(pt1[j]+s*normal[j]) for j in range(0,3)] 
            self.graphics.add_line(pt1, pt2, color=[0.0,1.0,0.0], width=5)

            # Show binormal.
            binormal = np.cross(tangent, normal)
            pt2 = [(pt1[j]+s*binormal[j]) for j in range(0,3)] 
            self.graphics.add_line(pt1, pt2, color=[1.0,1.0,0.0], width=5)

            self.graphics.image.extract_slice(pt1, tangent, normal, binormal)

        '''
        self.visualizer.window.Render()

        return

    def onCharEvent(self, renderer, event):
        """
        Process an on char event.

        This is used to prevent passing the shortcut key 'w' to vtk which we use
        to write selected results and vtk uses to switch to wireframe display. 
        """
        key = self.GetInteractor().GetKeySym()
        if (key != 'w'):
            self.OnChar()
  
    def onKeyPressEvent(self, renderer, event):
        """
        Process a key press event.
        """
        key = self.GetInteractor().GetKeySym()

        if (key == 's'):
            self.leftButtonPressEvent(None, event)
        elif (key == 'f'):
            self.fix()

    #__def onKeyPressEvent

#__class MouseInteractorStyle

class VisualizationGeometry(object):
    def __init__(self, name, source, callback=None):
        self.name = name
        self.source = source
        self.source_type = str(type(source))
        self.callback = callback 

    def process_select(self, position):
        if self.callback == None:
            return
        self.callback(self.source, position)

class Visualization(object):
    ''' The Visualization class is used to visualize SV objects (paths, contours, etc.) in a graphics window.
    '''
    def __init__(self, name, win_width, win_height):
        self.renderer = vtk.vtkRenderer()
        self.window = vtk.vtkRenderWindow()
        self.window.AddRenderer(self.renderer)
        self.renderer.SetBackground(0.8, 0.8, 0.8)
        self.window.SetSize(win_width, win_height)
        self.window.Render()
        self.window.SetWindowName(name)
        self.interactor = None 
        self.extent_min = [1e6, 1e6, 1e6]
        self.extent_max = [-1e6, -1e6, -1e6]
        self.actor_map = {}

    def update_extent(self, x, y, z):
        if x > self.extent_max[0]:
            self.extent_max[0] = x
        elif x < self.extent_min[0]:
            self.extent_min[0] = x

        if y > self.extent_max[1]:
            self.extent_max[1] = y
        elif y < self.extent_min[1]:
            self.extent_min[1] = y

        if z > self.extent_max[2]:
            self.extent_max[2] = z
        elif z < self.extent_min[2]:
            self.extent_min[2] = z

    def convert_ugrid_to_polydata(self, mesh):
        ''' Convert an mesh to polydata.
        '''
        geometry_filter = vtk.vtkGeometryFilter()
        geometry_filter.SetInputData(mesh)
        geometry_filter.Update()
        mesh_polydata = geometry_filter.GetOutput()

        triangle_filter = vtk.vtkTriangleFilter()
        triangle_filter.SetInputData(mesh_polydata)
        triangle_filter.Update()
        polydata = triangle_filter.GetOutput()
        return polydata 


    def get_contour_geometry(self, contour):
        ''' Create geometry for the contour points and control points.
        '''
        coords = contour.get_contour_points()
        num_pts = len(coords)

        ## Create contour geometry points and line connectivity.
        #
        points = vtk.vtkPoints()
        points.SetNumberOfPoints(num_pts)
        lines = vtk.vtkCellArray()
        lines.InsertNextCell(num_pts+1)
        n = 0
        for pt in coords:
            points.SetPoint(n, pt[0], pt[1], pt[2])
            lines.InsertCellPoint(n)
            n += 1
            self.update_extent(pt[0], pt[1], pt[2])
        #_for pt in coords
        lines.InsertCellPoint(0)

        contour_geom = vtk.vtkPolyData()
        contour_geom.SetPoints(points)
        contour_geom.SetLines(lines)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(geom)
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetLineWidth(2.0)
        actor.GetProperty().SetColor(0.0, 0.6, 0.0)
        renderer.AddActor(actor)

        ## Add center point.
        #
        center = contour.get_center()
        num_pts = 1
        points = vtk.vtkPoints()
        vertices = vtk.vtkCellArray()
        pid = points.InsertNextPoint(center)
        vertices.InsertNextCell(1)
        vertices.InsertCellPoint(pid)
        center_point = vtk.vtkPolyData()
        center_point.SetPoints(points)
        center_point.SetVerts(vertices)

        ## Add control points.
        #
        coords = contour.get_control_points()
        num_pts = len(coords)
        points = vtk.vtkPoints()
        vertices = vtk.vtkCellArray()
        for pt in coords:
            pid = points.InsertNextPoint(pt)
            vertices.InsertNextCell(1)
            vertices.InsertCellPoint(pid)
        #_for pt in coords
        control_points = vtk.vtkPolyData()
        control_points.SetPoints(points)
        control_points.SetVerts(vertices)

        return contour_geom, center_point, control_points

    def get_path_geometry(self, path):
        ''' Create geometry for the path curve and control points.
        '''
        coords = path.get_curve_points()
        num_pts = len(coords)

        ## Create path geometry points and line connectivity.
        points = vtk.vtkPoints()
        points.SetNumberOfPoints(num_pts)
        lines = vtk.vtkCellArray()
        lines.InsertNextCell(num_pts)
        n = 0
        for pt in coords:
            points.SetPoint(n, pt[0], pt[1], pt[2])
            lines.InsertCellPoint(n)
            n += 1
            self.update_extent(pt[0], pt[1], pt[2])
        #_for pt in coords
        lines_geom = vtk.vtkPolyData()
        lines_geom.SetPoints(points)
        lines_geom.SetLines(lines)

        ## Add control points.
        coords = path.get_control_points()
        num_pts = len(coords)
        points = vtk.vtkPoints()
        vertices = vtk.vtkCellArray()
        for pt in coords:
            pid = points.InsertNextPoint(pt)
            vertices.InsertNextCell(1)
            vertices.InsertCellPoint(pid)
        #_for pt in coords
        control_points = vtk.vtkPolyData()
        control_points.SetPoints(points)
        control_points.SetVerts(vertices)

        return lines_geom, control_points

    def get_contour_geometry(self, contour):
        ''' Create geometry for the contour points and control points.
        '''
        coords = contour.get_points()
        num_pts = len(coords)

        ## Create contour geometry points and line connectivity.
        #
        points = vtk.vtkPoints()
        points.SetNumberOfPoints(num_pts)
        lines = vtk.vtkCellArray()
        lines.InsertNextCell(num_pts+1)
        n = 0
        for pt in coords:
            points.SetPoint(n, pt[0], pt[1], pt[2])
            lines.InsertCellPoint(n)
            n += 1
            self.update_extent(pt[0], pt[1], pt[2])
        #_for pt in coords
        lines.InsertCellPoint(0)

        contour_pd = vtk.vtkPolyData()
        contour_pd.SetPoints(points)
        contour_pd.SetLines(lines)

        ## Add center point.
        #
        center = contour.get_center()
        num_pts = 1
        center_point = vtk.vtkPoints()
        vertices = vtk.vtkCellArray()
        pid = center_point.InsertNextPoint(center)
        vertices.InsertNextCell(1)
        vertices.InsertCellPoint(pid)
        center_point_pd = vtk.vtkPolyData()
        center_point_pd.SetPoints(center_point)
        center_point_pd.SetVerts(vertices)

        ## Add control points.
        #
        try:
            coords = contour.get_control_points()
            num_pts = len(coords)
            control_points = vtk.vtkPoints()
            vertices = vtk.vtkCellArray()
            for pt in coords:
                pid = control_points.InsertNextPoint(pt)
                vertices.InsertNextCell(1)
                vertices.InsertCellPoint(pid)
            #_for pt in coords
            control_points_pd = vtk.vtkPolyData()
            control_points_pd.SetPoints(control_points)
            control_points_pd.SetVerts(vertices)
        except:
            control_points_pd = None

        return contour_pd, center_point, control_points_pd

    def add_polydata(self, vgeom, polydata, color=[1.0, 1.0, 1.0], opacity=1.0, line_width=1.0, wire=False, edges=False, pickable=True):
        ''' Add a polydata object to the renderer.
        '''
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(polydata)
        mapper.SetScalarVisibility(False)

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(color[0], color[1], color[2])
        actor.GetProperty().SetOpacity(opacity)
        actor.GetProperty().SetPointSize(5)
        actor.GetProperty().SetLineWidth(line_width)
        if not pickable: 
            actor.PickableOff()

        if wire:
            actor.GetProperty().SetRepresentationToWireframe()
            actor.GetProperty().SetLineWidth(1.0)

        if edges:
            actor.GetProperty().EdgeVisibilityOn();

        self.actor_map[actor] = vgeom
        self.renderer.AddActor(actor)

    def add_actor(self, actor): 
        self.renderer.AddActor(actor)

    def add_line(self, pt1, pt2, color=[1.0, 1.0, 1.0], width=2):
        line = vtk.vtkLineSource()
        line.SetPoint1(pt1);
        line.SetPoint2(pt2)
        line.Update()
        polydata = line.GetOutput()
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(polydata)
        mapper.ScalarVisibilityOff()
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(color[0], color[1], color[2])
        self.renderer.AddActor(actor)

    def add_sphere(self, name, center, radius, color=[1.0, 1.0, 1.0], wire=False):
        ''' Add a polydata object to the renderer.
        '''
        sphere = vtk.vtkSphereSource()
        sphere.SetCenter(center[0], center[1], center[2])
        sphere.SetRadius(radius) 
        sphere.SetPhiResolution(16)
        sphere.SetThetaResolution(16)
        sphere.Update()
        sphere_pd = sphere.GetOutput() 
        self.add_polydata(name, sphere_pd, color, wire)

    def display(self):
        center = 3*[0.0]
        widths = 3*[0.0]
        for i in range(3):
            center[i] = (self.extent_max[i] +  self.extent_min[i])/ 2.0;
            widths[i] = self.extent_max[i] -  self.extent_min[i]
        self.add_sphere("center", center, 0.1, color=[0.5, 0.5, 0.5])

        camera = self.renderer.GetActiveCamera();
        offset_z = 2.0*widths[2]
        camera.SetPosition(0.0, 0.0, offset_z)
        camera.SetFocalPoint(center[0], center[1], center[2])

        # Create a trackball interacter to transform the geometry using the mouse.
        self.interactor = vtk.vtkRenderWindowInteractor()
        self.interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
        self.interactor.SetRenderWindow(self.window)

        # Add the custom picking style.
        style = MouseInteractorStyle(self)
        style.renderer = self.renderer
        style.visualizer = self
        self.interactor.SetInteractorStyle(style)
        style.SetCurrentRenderer(self.renderer)

        self.interactor.Start()
