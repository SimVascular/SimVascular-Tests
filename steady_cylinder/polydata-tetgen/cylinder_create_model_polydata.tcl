
proc cylinder_create_model_PolyData {dstdir} {

  # just copy the model for now

  catch {repos_delete -obj cyl}
  solid_readNative -file cylinder.vtp -obj cyl

  file copy cylinder.vtp $dstdir
  file copy cylinder.vtp.facenames $dstdir
  
  return [file join $dstdir cylinder.vtp]

}
