'''Test creating a path frame object.
'''
import sv 

## Create Path object.
path_frame = sv.pathplanning.PathFrame()
print("Path frame:")
print("  Position: " + str(path_frame.position))
print("  Normal: " + str(path_frame.normal))
print("  Tangent: " + str(path_frame.tangent))

## Create Path object.
path_frame = sv.pathplanning.PathFrame(position=[1,2,3], normal=[0,0,1], tangent=[0,1,0])
print("Path frame:")
print("  Position: " + str(path_frame.position))
print("  Normal: " + str(path_frame.normal))
print("  Tangent: " + str(path_frame.tangent))

