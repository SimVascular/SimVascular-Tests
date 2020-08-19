'''Test creating a ellipsoid.

    **** The cvModelingModel MakeEllipsoid method is not implemented. **** 

'''
import sv
import sys
import vtk
sys.path.insert(1, '../graphics/')
import graphics as gr

# Create a modeler.
oc_modeler = sv.modeling.Modeler(sv.modeling.Kernel.OPENCASCADE)
modeler = sv.modeling.Modeler(sv.modeling.Kernel.POLYDATA)

## Create a ellipsoid.
print("Create a ellipsoid ...")
center = [0.0, 0.0, 0.0]
radii = [1, 2, 3] 
ellipsoid = modeler.ellipsoid(center=center, radii=radii)
print("  Ellipsoid type: " + str(type(ellipsoid)))
ellipsoid_pd = ellipsoid.get_polydata()
print("  Ellipsoid: num nodes: {0:d}".format(ellipsoid_pd.GetNumberOfPoints()))
#
oc_ellipsoid = oc_modeler.ellipsoid(center=center, radii=radii)
print("  OC Ellipsoid type: " + str(type(oc_ellipsoid)))
oc_ellipsoid_pd = oc_ellipsoid.get_polydata()
print("  OC Ellipsoid: num nodes: {0:d}".format(oc_ellipsoid_pd.GetNumberOfPoints()))

## Create renderer and graphics window.
win_width = 500
win_height = 500
renderer, renderer_window = gr.init_graphics(win_width, win_height)

## Add model polydata.
gr.add_geometry(renderer, ellipsoid_pd, color=[0.0, 1.0, 0.0], wire=True, edges=False)
#gr.add_geometry(renderer, oc_ellipsoid_pd, color=[1.0, 0.0, 0.0], wire=True, edges=False)

## Add a sphere.
gr.add_sphere(renderer, center=center, radius=0.1, color=[1.0, 1.0, 1.0], wire=True)

pt1 = center
pt2 = [ center[i] + length/2.0 * axis[i] for i in range(3) ]
gr.add_line(renderer, pt1, pt2, color=[0.5, 0.0, 0.0], width=4)

# Display window.
gr.display(renderer_window)



