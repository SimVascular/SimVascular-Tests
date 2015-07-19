
proc cylinder_create_model_parasolid {dstdir} {
  #
  #  Create a solid model of a cylinder:  radius 0.2 cm
  #                                       length 6.0 cm
  #                                       length 3.0 cm
  #
  puts "Creating solid model."
  catch {repos_delete -obj cyl}
  #solid_cylinder -result cyl -radius 0.2 -length 6.0 \
  #	       -ctr {0 0 3.0} -axis {0 0 1}
  solid_cylinder -result cyl -radius 2 -length 30 \
	         -ctr {0 0 15} -axis {0 0 1}

  #
  #  Set Face Names of Solid Model
  #
  #  NOTE:  This can be done interactively using:
  #         Solid Modeling->Simple Model Viewer
  #                                            -> View
  #                                            -> Save

  puts "Tagging faces."
  set faceids [cyl GetFaceIds]
  cyl SetFaceAttr -attr gdscName -faceId [lindex $faceids 0] -value inflow
  cyl SetFaceAttr -attr gdscId   -faceId [lindex $faceids 1] -value 1
  cyl SetFaceAttr -attr gdscName -faceId [lindex $faceids 1] -value outlet
  cyl SetFaceAttr -attr gdscName -faceId [lindex $faceids 2] -value wall

  #
  #  Save the solid model with the face tags to a file
  #
  puts "Save SolidModel."
  cyl WriteNative -file [file join $dstdir cylinder]

  return [file join $dstdir cylinder.xmt_txt]
  
}
