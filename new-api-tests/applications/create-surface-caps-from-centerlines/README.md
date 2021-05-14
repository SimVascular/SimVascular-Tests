This directory contains the Python create_surface_caps.py scripts used to remove the ends of a surface based 
on the centerlines geometry computed for it. The surface ends can then be capped to form a closed surface model.

The surface is typically obtained from a 3D segmenatation of medical imaging data.

The create_surface_caps.py script uses interactive graphics to disaplay geometry for surfaces, centerlines, etc. 
All operations (e.g. extracting centerlines) are initiated using keyboard keys 

    a - Compute model automatically.
    c - Compute centerlines.
    m - Create a model from the surface and centerlines, remesh the surface and generate an FE volume mesh.
    q - Quit
    s - Select a centerline source point.
    t - Select a centerline target point.
    u - Undo the selection of a centerline source or target point.

The order of operations is

   1) Select a centerline source points (usually a single point)

   2) Select a centerline target points

   3) Compute centerlines

   4) Create a model from the surface and centerlines

   5) Remesh the model surface (needed to regularize the capped surface mesh)

   6) Generate an FE volume mesh 

Selecting the 'a' key performs all of these operations automatically without the need for selecting source 
and target points for the centerlines computation. It assumes a surface that has just three flat regions 
defining a vessel with an inlet and two outlets. The source and target points are determined as the centers of 
the three flat regions. This may not work for all surfaces!

Geometry from all operations are written to a .vtp or .vtu files with the NAME of the input surface file prefixed

   NAME-centerlines.vtp - Centerlines 

   NAME-clipped.vtp - The clipped surface

   NAME-capped.vtp - The capped clipped surface

   NAME-mesh.vtu - The FE volume mesh 


The create_surface_caps.py script accepts several argumnents 

   --surface-file (required) 

     The name of the input surface (.vtp or .vtk) file.

   --clip-distance (optional, default=0.0) 

     The distance from the end of a centerline branch to clip a surface. If not given then the maximum 
     inscribed sphere radius at the end is used. 
                     
   --clip-width-scale (optiona, default=1.0)

     The width multiplied by the centerline branch end maximum inscribed sphere radius to define the width
     of the box used to clip a surface.

   --mesh-scale (optional, default=1.0)

     The factor used to scale the fe volume meshing edge size. A larger scale creates a coarser mesh. 
     The initial edge size is determined from the largest surface triangle.

   --remesh-scale (optional, default=1.0)

     The factor used to scale the surface remeshing edge size. A larger scale creates a coarser suface mesh. 
     The initial edge size is determined from the largest surface triangle.


Example:

    simvascluar --python -- create_surface_caps.py --surface-file=demo-surface.vtp  


