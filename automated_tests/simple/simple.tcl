set thisFile [dict get [ info frame [ info frame ] ] file ]
set thisDir [file dirname $thisFile]
puts $thisFile
puts $thisDir

set data "This is some test data.\n"
set filename "$thisDir/output/simple_test.txt"
set fileId [open $filename "w"]
puts -nonewline $fileId $data
close $fileId
after 1000
mainGUIexit