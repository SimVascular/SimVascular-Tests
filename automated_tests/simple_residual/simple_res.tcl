set thisFile [dict get [ info frame [ info frame ] ] file ]
set thisDir [file dirname $thisFile]
puts $thisFile
puts $thisDir

set data "0.1\n"
set filename "$thisDir/simple_res.output"
if { [file exists $filename] } {
    file delete $filename
}
set fileId [open $filename "w"]
puts -nonewline $fileId $data
close $fileId
after 1000
mainGUIexit