Please check back for updates regularly, if you have an issue that isn't mentioned here/fixed in a recent version please open an issue.

# Changelog
## VERSION 2.5.4
* Fixed errors with 1 frame animations.
* Fixed bone-only model exporting.
* Merged XANIM/XCAM functions.
* Added button to clear cosmetic parent.

## VERSION 2.5.3
* Added auto-updater (Seperate EXE to handle it so user isn't stuck waiting for it and doesn't crash some ver. of Maya, can be disabled)
* Fully removed Bo3 Mode (its checkbox wasn't removed)
* Added an option to print XMODEL_EXPORT info while exporting.

## VERSION 2.5.2
* Grab notes not working.

## VERSION 2.5.1
* Fixed 0 bone models not writing TAG_ORIGIN

## VERSION 2.5
* Fixed progression bars on xanim and xmodel exports.
* Fixed auto-rename to only rename under certain conditions (i.e. rename only tag_weapon to tag_weapon_right if it's a child of tag_torso)
+ Added support for cosmetic bones.
+ Added clear notes button to remove all notes in xanim window.
+ Added support for ExportX, Export2Bin still works. (ExportX is required for cosmetic bones).
+ Armature Only models are now allowed for animation models.
- Removed Ignore Useless notes, it's hard to determine a "useless note", if you don't want notes like "reload_large" then remove them manually.
- Removed Bo3 Mode, if you have models with greater than 65k verts, use ExportX.

## VERSION 2.4
* Added basic XCAM_EXPORT support
* Added support for CoD1 (untested)
* Added support for BO3 xmodel_export keywords
* Added an option to automatically rename tag_weapon and j_gun joints

## VERSION 2.3
* Fixed Reg error/s.
* (Hopyfully) Fixed Export2Bin and should now work and convert in same dir.

## VERSION 2.2
+ Export2Bin support is fully finished

## VERSION 2.1
+ Minor fix in RCAT which caused an error in Maya 2016

## VERSION 2.0
+ Added an option for exporting anims with better quality and reduced jitter (only applies to custom made anims)
+ Support for Export2Bin
+ Supports reading notetracks from old CoD Exporter for Maya 8.5 and from Wraith exports
+ Merged with Ray's camera animation toolkit

## VERSION 1.5.1
+ Added CoD4 XModel importing
+ Automatically exports black vertices as white (can disable this in the customization section at the top of the script file)
* Bug fixes

## VERSION 1.5
* Organized code a bit
* Renamed project to "CoDMayaTools" (from "CoDExportTools"), as it now does both importing and exporting
* Fixed material/object names exporting with : in them (namespace markers)
+ Added CoD5 XModel importing
+ Auto updating
+ IWI to DDS converter

## VERSION 1.4
* Changed new version message to open website forum topic instead of message box
* Fixed models without skins exporting in Object space instead of World space

## VERSION 1.3
* Fixed excessive TRI_VERT_RATIO error (this can still happen if something is wrong with your model, but this update should help)

## VERSION 1.2
+ Added button to export multiple models/animations at once
* Moved some of the user-changeable variables in the script to the top of the file in the CUSTOMIZATION section

## VERSION 1.1
+ Added feature to switch the gun in a weapon rig file
* Fixed trying to write to the export file before it was created
* Changed the "No joints selected; exporting with a default TAG_ORIGIN." warning to not create a warning dialog after export
* Other small random fixes

## VERSION 1
* Original - XModel Exporter, XAnim Exporter, and ViewModel tools


















