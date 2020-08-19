'''Test the sv.geometry.LoftNurbsOptions() class. 
'''
import sv

options = sv.geometry.LoftNurbsOptions()
print(dir(options)) 
print(dir(options.knot_span_types)) 

print("\n\nKnot span types: ")
print("  AVERAGE: {0:s}".format(options.knot_span_types.AVERAGE))
#print("  AVERAGE: {0:s}".format(options.knot_span_types.AVERAGE))

print("\n\nOption attributes: ")
print("  u_degree: " + str(options.u_degree))

## Print all options
#
print("\n\nOptions values: ")
[ print("  {0:s}:{1:s}".format(key,str(value))) for (key, value) in sorted(options.get_values().items()) ]
print("\n\n")

#print("  AVERAGE: {0:s}".format(options.KnotSpanType.AVERAGE))
#print("  DERIVATIVE: {0:s}".format(options.KnotSpanType.DERIVATIVE))
#print("  EQUAL: {0:s}".format(options.KnotSpanType.EQUAL))

#options.KnotSpanType_AVERAGE
#options.KnotSpanType_DERIVATIVE

