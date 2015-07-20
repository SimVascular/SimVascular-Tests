
proc bifurcation_create_model_Parasolid {dstdir} {
   catch {repos_delete -obj bifurcation}
   file copy bifurcation.xmt_txt [file join $dstdir bifurcation.xmt_txt]
   solid_readNative -file [file join $dstdir bifurcation.xmt_txt] -obj bifurcation
   return [file join $dstdir bifurcation.xmt_txt] 
}

