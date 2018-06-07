import os
import math
import ctypes
myDll=ctypes.PyDLL('lib_simvascular_solid.dylib')
myDll.initpySolid2()
import pySolid2
myDll=ctypes.PyDLL('lib_simvascular_polydata_solid.dylib')
myDll.initpySolidPolydata()
import pySolidPolydata
myDll=ctypes.PyDLL('lib_simvascular_repository.dylib')
myDll.initpyRepository()
import pyRepository
myDll=ctypes.PyDLL('lib_simvascular_mesh.dylib')
myDll.initpyMeshObject()
import pyMeshObject
myDll=ctypes.PyDLL('lib_simvascular_tetgen_mesh.dylib')
myDll.initpyMeshTetgen()
import pyMeshTetgen
myDLL=ctypes.PyDLL('lib_simvascular_utils.dylib')
myDLL.initpyMath()
import pyMath
