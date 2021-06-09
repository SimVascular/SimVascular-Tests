# geodesic_groups_file 2.1

#
# Group Stuff
#

proc group_autoload {} {
  global gFilenames
  set grpdir $gFilenames(groups_dir)
  group_readProfiles {left_iliac_branch1} [file join $grpdir {left_iliac_branch1}]
  group_readProfiles {celiac_trunk_branch1} [file join $grpdir {celiac_trunk_branch1}]
  group_readProfiles {right_inf_renal} [file join $grpdir {right_inf_renal}]
  group_readProfiles {left_iliac_branch2} [file join $grpdir {left_iliac_branch2}]
  group_readProfiles {left_renal} [file join $grpdir {left_renal}]
  group_readProfiles {splenic_branch1} [file join $grpdir {splenic_branch1}]
  group_readProfiles {superior_mesenteric_branch1} [file join $grpdir {superior_mesenteric_branch1}]
  group_readProfiles {right_iliac} [file join $grpdir {right_iliac}]
  group_readProfiles {left_iliac_internal} [file join $grpdir {left_iliac_internal}]
  group_readProfiles {inferior_mesenteric_artery} [file join $grpdir {inferior_mesenteric_artery}]
  group_readProfiles {left_sup_renal} [file join $grpdir {left_sup_renal}]
  group_readProfiles {right_iliac_internal} [file join $grpdir {right_iliac_internal}]
  group_readProfiles {celiac_trunk} [file join $grpdir {celiac_trunk}]
  group_readProfiles {right_iliac_branch1} [file join $grpdir {right_iliac_branch1}]
  group_readProfiles {splenic} [file join $grpdir {splenic}]
  group_readProfiles {right_iliac_branch2} [file join $grpdir {right_iliac_branch2}]
  group_readProfiles {aorta} [file join $grpdir {aorta}]
  group_readProfiles {superior_mesenteric} [file join $grpdir {superior_mesenteric}]
  group_readProfiles {right_renal} [file join $grpdir {right_renal}]
}
