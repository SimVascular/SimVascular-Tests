'''Test imaging.Image extract_slice method. 
'''
import os
import sv
import vtk
import sys
sys.path.insert(1, '../graphics/')
import graphics as gr

def display_edges(renderer, image):
    outline = vtk.vtkOutlineFilter()
    outline.SetInputData(image)
    outline.Update()

    mapper = vtk.vtkDataSetMapper()
    mapper.SetInputData(outline.GetOutput())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetRepresentationToWireframe()
    #actor.GetProperty().SetColor(self.colors.GetColor3d("Black"))
    renderer.AddActor(actor)

def create_greyscale_lut(scalar_range):
    imin = scalar_range[0]
    imax = scalar_range[1]
    table = vtk.vtkLookupTable()
    table.SetRange(imin, imax) # image intensity range
    table.SetValueRange(0.0, 1.0) # from black to white
    table.SetSaturationRange(0.0, 0.0) # no color saturation
    table.SetRampToLinear()
    table.Build()
    return table

# The location of some imaging data.
sv_data_dir = os.environ['SIMVASCULAR_DATA']

## Read an image.
#
print("Read image file ...")
file_name = sv_data_dir + "/DemoProject/Images/sample_data-cm.vti"
file_name = sv_data_dir + "/data/OSMSC0110-aorta/image_data/volume/I.002.dcm"
image = sv.imaging.Image(file_name)

dimensions = image.get_dimensions()
print("Image dimensions: {0:g} {1:g} {2:g}".format(dimensions[0], dimensions[1], dimensions[2]))

spacing = image.get_spacing()
print("Image spacing: {0:g} {1:g} {2:g}".format(spacing[0], spacing[1], spacing[2]))

use_slice_points = True

if use_slice_points:
    slice_points = image.extract_slice()
else:
    image_slice = image.extract_slice()
    image_size = 3*[0]
    image_slice.GetDimensions(image_size)
    print("Image slice dimentions: {0:s}".format(str(image_size)))

## Create renderer and graphics window.
win_width = 500
win_height = 500
renderer, renderer_window = gr.init_graphics(win_width, win_height)

if use_slice_points:
    geom_filter = vtk.vtkGeometryFilter()
    geom_filter.SetInputData(slice_points)
    geom_filter.Update()

    color_lut = create_greyscale_lut((0,255))

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(geom_filter.GetOutput())
    #mapper.SetScalarVisibility(False)
    mapper.SetLookupTable(color_lut)
    #mapper.SetScalarRange(0,255)
    mapper.SetScalarRange(0,183)
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    renderer.AddActor(actor)

else:
    display_edges(renderer, image_slice)

    color_lut = create_greyscale_lut((0,200))
    slice_colors = vtk.vtkImageMapToColors()
    slice_colors.SetInputData(image_slice)
    slice_colors.SetLookupTable(color_lut)
    slice_colors.Update()

    slice_actor = vtk.vtkImageActor()
    slice_actor.GetMapper().SetInputData(slice_colors.GetOutput())
    imin = 0
    imax = image_size[0]-1
    jmin = 0
    jmax = image_size[1]-1
    kmin = 0
    kmax = image_size[2]-1
    slice_actor.SetDisplayExtent(imin, imax, jmin,jmax, kmin,kmax);
    slice_actor.ForceOpaqueOn()
    renderer.AddActor(slice_actor)

# Display window.
gr.display(renderer_window)




