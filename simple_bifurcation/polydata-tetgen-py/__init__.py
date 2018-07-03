#import os
#import math
import ctypes
import sys
import vtk
if sys.version_info < (3,0):
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
    myDll=ctypes.PyDLL('lib_simvascular_segmentation.dylib')
    myDll.initpyContour()
    myDll.initpyThresholdContour()
    myDll.initpylevelSetContour()
    myDll.initpyPolygonContour()
    myDll.initpyCircleContour()
    myDll.initpySplinePolygonContour()
    import pyContour
    import pyThresholdContour
    import pylevelSetContour
    import pyCircleContour
    import pyPolygonContour
    import pySplinePolygonContour
    myDll=ctypes.PyDLL('lib_simvascular_vmtk_utils.dylib')
    myDll.initpyVMTKUtils()
    import pyVMTKUtils
    myDll=ctypes.PyDLL('lib_simvascular_opencascade_solid.dylib')
    myDll.initpySolidOCCT()
    import pySolidOCCT
    myDll=ctypes.PyDLL('lib_simvascular_mmg_mesh.dylib')
    myDll.initpyMeshUtil()
    import pyMeshUtil
    myDll=ctypes.PyDLL('lib_simvascular_itk_lset.dylib')
    myDll.initpyItkls()
    import pyItkls
    myDll=ctypes.PyDLL('lib_simvascular_adaptor.dylib')
    myDll.initpyMeshAdapt()
    import pyMeshAdapt
    myDll=ctypes.PyDLL('lib_simvascular_tetgen_adaptor.dylib')
    myDll.initpyTetGenAdapt()
    import pyTetGenAdapt
    myDll=ctypes.PyDLL('lib_simvascular_geom.dylib')
    myDll.initpyGeom()
    import pyGeom
    myDll=ctypes.PyDLL('lib_simvascular_image.dylib')
    myDll.initpyImage()
    import pyImage
    myDll=ctypes.PyDLL('lib_simvascular_path.dylib')
    myDll.initpyPath()
    import pyPath
    myDll=ctypes.PyDLL('liborg_sv_pythondatanodes.dylib')
    myDll.initpyGUI()
    import pyGUI
else:
    myDll=ctypes.PyDLL('lib_simvascular_solid.dylib')
    func=myDll.PyInit_pySolid2
    func.restype = ctypes.py_object
    pySolid2 = func()
    myDll=ctypes.PyDLL('lib_simvascular_polydata_solid.dylib')
    func=myDll.PyInit_pySolidPolydata
    func.restype = ctypes.py_object
    pySolidPolydata=func()
    myDll=ctypes.PyDLL('lib_simvascular_repository.dylib')
    func=myDll.PyInit_pyRepository
    func.restype = ctypes.py_object
    pyRepository=func()
    myDll=ctypes.PyDLL('lib_simvascular_mesh.dylib')
    func=myDll.PyInit_pyMeshObject
    func.restype = ctypes.py_object
    pyMeshObject=func()
    myDll=ctypes.PyDLL('lib_simvascular_tetgen_mesh.dylib')
    func=myDll.PyInit_pyMeshTetgen
    func.restype = ctypes.py_object
    pyMeshTetgen=func()
    myDLL=ctypes.PyDLL('lib_simvascular_utils.dylib')
    func=myDLL.PyInit_pyMath
    func.restype = ctypes.py_object
    pyMath=func()
    myDll=ctypes.PyDLL('lib_simvascular_segmentation.dylib')
    func=myDll.PyInit_pyContour
    func.restype = ctypes.py_object
    pyContour=func()
    func=myDll.PyInit_pyThresholdContour
    func.restype = ctypes.py_object
    pyThresholdContour=func()
    func=myDll.PyInit_pylevelSetContour
    func.restype = ctypes.py_object
    pylevelSetContour=func()
    func=myDll.PyInit_pyPolygonContour
    func.restype = ctypes.py_object
    pyPolygonContour=func()
    func=myDll.PyInit_pyCircleContour
    func.restype = ctypes.py_object
    pyCircleContour=func()
    func=myDll.PyInit_pySplinePolygonContour
    func.restype = ctypes.py_object
    pySplinePolygonContour=func()
    myDll=ctypes.PyDLL('lib_simvascular_vmtk_utils.dylib')
    func=myDll.PyInit_pyVMTKUtils
    func.restype = ctypes.py_object
    pyVMTKUtils=func()
    myDll=ctypes.PyDLL('lib_simvascular_opencascade_solid.dylib')
    func=myDll.PyInit_pySolidOCCT
    func.restype = ctypes.py_object
    pySolidOCCT=func()
    myDll=ctypes.PyDLL('lib_simvascular_mmg_mesh.dylib')
    func=myDll.PyInit_pyMeshUtil
    func.restype = ctypes.py_object
    pyMeshUtil=func()
    myDll=ctypes.PyDLL('lib_simvascular_itk_lset.dylib')
    func=myDll.PyInit_pyItkls
    func.restype = ctypes.py_object
    pyItkls=func()
    myDll=ctypes.PyDLL('lib_simvascular_adaptor.dylib')
    func=myDll.PyInit_pyMeshAdapt
    func.restype = ctypes.py_object
    pyMeshAdapt=func()
    myDll=ctypes.PyDLL('lib_simvascular_tetgen_adaptor.dylib')
    func=myDll.PyInit_pyTetGenAdapt
    func.restype = ctypes.py_object
    pyTetGenAdapt=func()
    myDll=ctypes.PyDLL('lib_simvascular_geom.dylib')
    func=myDll.PyInit_pyGeom
    func.restype = ctypes.py_object
    pyGeom=func()
    myDll=ctypes.PyDLL('lib_simvascular_image.dylib')
    func=myDll.PyInit_pyImage
    func.restype = ctypes.py_object
    pyImage=func()
    myDll=ctypes.PyDLL('lib_simvascular_path.dylib')
    func=myDll.PyInit_pyPath
    func.restype = ctypes.py_object
    pyPath=func()
    myDll=ctypes.PyDLL('liborg_sv_pythondatanodes.dylib')
    func=myDll.PyInit_pyGUI
    pyGUI=func()

    

