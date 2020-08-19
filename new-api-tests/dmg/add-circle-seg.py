'''Test adding a circle segmentation to the SV Data Manager.

   This is tested using the Demo Project.
'''
from pathlib import Path
import sv

## Create a circle.
#
radius = 1.0
center = [0.0, 0.0, 0.0]
normal = [0.0, 1.0, 0.0]
segmentations = [ sv.segmentation.Circle(radius=radius, center=center, normal=normal) ]

sv.dmg.add_segmentation(name="circle", path="aorta", segmentations=segmentations)

