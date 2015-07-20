
proc bifurcation_create_model_PolyData {dstdir} {

   file copy bifurcation.vtp $dstdir
   file copy bifurcation.vtp.facenames $dstdir

   catch {repos_delete -obj bifurcation}
   solid_readNative -file [file join $dstdir bifurcation.vtp] -obj bifurcation
   
   return [file join $dstdir bifurcation.vtp]

}
