
proc bifurcation_create_model_Discrete {dstdir} {

  # just copy the model for now

  set fn bifurcation.dsm

  catch {repos_delete -obj bifurcation}
  solid_readNative -file $fn -obj bifurcation

  file copy $fn $dstdir
  file copy $fn.facenames $dstdir

  global gDiscreteModelFaceNames
  global gDiscreteModelFaceNamesInfo
  catch {unset gDiscreteModelFaceNames}
  catch {unset gDiscreteModelFaceNamesInfo}
  if [file exists $fn.facenames] {
    puts "sourcing $fn.facenames"
    source $fn.facenames
    package require md5
    set mymd5 [::md5::md5 -hex -file $fn]
    if {$mymd5 != $gDiscreteModelFaceNamesInfo(model_file_md5)} {
      return -code error "ERROR: dsm model ($fn) file doesn't match one used to generate facenames ($fn.facenames)!"
    }
  }

  return [file join $dstdir $fn]

}
