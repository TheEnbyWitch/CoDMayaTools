# CoDMayaTools
Original made by Aidan. Maintained by Ray1235 and Scobalula

New features:
- Animation quality - export more frames for higher quality and less jitter at the cost of a bigger file size!
- Export2Bin support - automatically converts xmodel_exports and xanim_exports to bin!
- Supports reading notetracks from old CoD Exporter for Maya 8.5 and from Wraith exports
- Automatic camera animation generation

## Cosmetic Bones:
For most models coming from Bo3 it's usually obvious what the cosmetic bone is, it usually has quite a number of bones without children under it (for character models, it's usually "head").

All cosmetic bones share the same parent, and thus it was easier to mark 1 joint, to do this:

1) Select the parent of the cosmetic bones.

2) In the export window select "Set selected as Cosmetic Parent", CoD Maya Tools will tell you it's been marked.

3) Export as normal.

#### The model MUST be converted using DTZxPorter's ExportX, NOT Export2Bin, to download ExportX click here and go to the Utilities tab

[exportx](http://aviacreations.com/wraith/)
