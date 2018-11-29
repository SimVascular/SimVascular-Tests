import os
import math
import ctypes
import sys
if sys.version_info<(3,0):
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
    import vtk
    myDLL=ctypes.PyDLL('lib_simvascular_geom.dylib')
    myDLL.initpyGeom()
    import pyGeom
    myDll=ctypes.PyDLL('lib_simvascular_segmentation.dylib')
    myDll.initpyContour()
    myDll.initpyCircleContour()
    import pyContour
    import pyCircleContour
    myDll=ctypes.PyDLL('lib_simvascular_path.dylib')
    myDll.initpyPath()
    import pyPath
    mydll=ctypes.PyDLL('lib_simvascular_vmtk_utils.dylib')
    mydll.initpyVMTKUtils()
    import pyVMTKUtils
else:
    myDll=ctypes.PyDLL('lib_simvascular_solid.dylib')
    initfunc=myDll.PyInit_pySolid2
    initfunc.restype = ctypes.py_object
    pySolid2 = initfunc()
    myDll=ctypes.PyDLL('lib_simvascular_polydata_solid.dylib')
    initfunc=myDll.PyInit_pySolidPolydata
    initfunc.restype = ctypes.py_object
    pySolidPolydata=initfunc()
    myDll=ctypes.PyDLL('lib_simvascular_repository.dylib')
    initfunc=myDll.PyInit_pyRepository
    initfunc.restype = ctypes.py_object
    pyRepository=initfunc()
    myDll=ctypes.PyDLL('lib_simvascular_mesh.dylib')
    initfunc=myDll.PyInit_pyMeshObject
    initfunc.restype = ctypes.py_object
    pyMeshObject=initfunc()
    myDll=ctypes.PyDLL('lib_simvascular_tetgen_mesh.dylib')
    initfunc=myDll.PyInit_pyMeshTetgen
    initfunc.restype = ctypes.py_object
    pyMeshTetgen=initfunc()
    myDLL=ctypes.PyDLL('lib_simvascular_utils.dylib')
    initfunc=myDLL.PyInit_pyMath
    initfunc.restype = ctypes.py_object
    pyMath=initfunc()
    myDLL=ctypes.PyDLL('lib_simvascular_geom.dylib')
    initfunc=myDLL.PyInit_pyGeom
    initfunc.restype = ctypes.py_object
    pyGeom=initfunc()
    myDll=ctypes.PyDLL('lib_simvascular_segmentation.dylib')
    initfunc=myDll.PyInit_pyContour
    initfunc.restype = ctypes.py_object
    pyContour=initfunc()
    initfunc=myDll.PyInit_pyCircleContour
    initfunc.restype = ctypes.py_object
    pyCircleContour=initfunc()
    myDll=ctypes.PyDLL('lib_simvascular_path.dylib')
    initfunc=myDll.PyInit_pyPath
    initfunc.restype = ctypes.py_object
    pyPath=initfunc()
    mydll=ctypes.PyDLL('lib_simvascular_vmtk_utils.dylib')
    initfunc=mydll.PyInit_pyVMTKUtils
    initfunc.restype = ctypes.py_object
    pyVMTKUtils=initfunc()
    import vtk

