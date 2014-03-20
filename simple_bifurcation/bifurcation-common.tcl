
proc demo_cleanup_old_files_misc {} {
}

proc demo_cleanup_old_files_simvascular {} {
  file delete bifurcation.mss
  file delete bifurcation.sms
  file delete bifurcation.sts
  file delete geom.sms
  file delete bct.dat.inflow
  file delete usrNBC1.var.inflow
  file delete usrNBC2.var.inflow
  file delete usrNBC3.var.inflow
  file delete inflow_mesh_face.vtk
  file delete bifurcation.logfile
  file delete bifurcation.coordinates.gz
  file delete bifurcation.connectivity.gz
  file delete bifurcation.coordinates
  file delete bifurcation.connectivity
  file delete bifurcation.xadj.gz
  file delete bifurcation.xadj
  file delete bifurcation.presolver
  file delete all.ebc
  file delete all.nbc
  file delete all.ebc.gz
  file delete all.nbc.gz
  file delete walls.ebc
  file delete walls.nbc
  file delete walls.ebc.gz
  file delete walls.nbc.gz
  foreach i [file_find mesh-surfaces *] {
    file delete $i
  }
  file delete mesh-surfaces
  # spectrum result files
  file delete bifurcation_mesh.vis.gz
  file delete bifurcation_mesh.vis
#  foreach i [file_find . bifurcation_res*.vis*] {
#    file delete $i
#  }
#  foreach i [file_find . frame-*.vtu] {
#    file delete $i
#  }
#  foreach i [file_find . profiles_for_*] {
#    file delete $i
#  }
}

proc demo_cleanup_old_files_solver {rootdir} {
  cd $rootdir
  file delete geombc.dat.1
  file delete dumpnew.dat
  file delete echo.dat
  file delete fort.76
  file delete histor.dat
  file delete spmass.dat
  foreach i [file_find . restart.*] {
    file delete $i
  }
  foreach i [file_find . flux.*] {
    file delete $i
  }
  foreach i [file_find . "error.*"] {
    file delete $i
  }
  foreach i [file_find . "forces*"] {
    file delete $i
  }
  file delete bct.dat
  file delete numstart.dat
  file delete solver.log
  file delete solver.done
  file delete license.dat
  file delete solver.inp

  cd ..
}

proc demo_cleanup_old_files_acusolve {rootdir} {
  cd $rootdir
  # delete acusolve files
  file delete inflow.1.bcu
  file delete inflow.1.time
  file delete inflow.2.bcu
  file delete inflow.2.time
  file delete inflow.3.bcu
  file delete inflow.3.time
  # mesh related files
  foreach i [file_find ACUSIM.DIR *] {
    file delete $i
  }
  file delete ACUSIM.DIR
  file delete bifurcation.1.Log
  file delete bifurcation.1.echo
  file delete acusolve.done
  file delete acusolve.log
  file delete license.dat
  file delete Acusim.cnf
  cd ..
}

proc demo_cleanup_old_files {} {
  demo_cleanup_old_files_misc
  demo_cleanup_old_files_simvascular
}

