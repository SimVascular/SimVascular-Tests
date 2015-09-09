set thisFile [dict get [ info frame [ info frame ] ] file ]
set thisDir [file dirname $thisFile]
puts $thisFile
puts $thisDir

after 1000
mainGUIexit 1