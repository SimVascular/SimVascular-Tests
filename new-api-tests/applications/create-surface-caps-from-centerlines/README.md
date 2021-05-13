This directory contains the Python create_surface_caps.py scripts used to remove the ends of a surface based 
on the centerlines geometry computed for it. The surface ends can then be capped to form a closed surface model.

The surface is typically ontained from a 3D segmenatation of medical imaging data.

The create_surface_caps.py uses interactive graphics to disaplay geometry for surfaces, centerlines, etc. 
All operations (e.g. extracting centerlines) are initiated using keyboard keys defined as

    a - Compute model automatically.
    c - Compute centerlines.
    m - Create a model from the surface and centerlines.
    q - Quit
    s - Select a centerline source point.
    t - Select a centerline target point.

The order of operations is

   1) Select a centerline source points (usually a single point)
   2) Select a centerline target points
   3) Compute centerlines
   4) Create a model from the surface and centerlines

Selecting the 'a' key performs all of these operations automatically without the need for selecting source 
and target points for the centerlines computation. It assumes a surface that has just three flat regions 
defining an inlet and two outlet vessles. The source and target points are determined as the centers of 
the three flat regions. This may not work for all surfaces!

Example:

    simvascluar --python -- create_surface_caps.py --surface-file=demo-surface.vtp  


