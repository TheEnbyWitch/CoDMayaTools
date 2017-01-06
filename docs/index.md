## New features in comparison to Aidan's original version:
* Full support for BO3 and Export2Bin
* Backwards compatibility with CoD1 (untested & xmodels only)
* Read notetracks from SEAnims, Wraith, tanims and old files
* Ray's Camera Animation Toolkit included for your weapon camera animation needs!
* Export XCams for BO3

## Installation:
1) Download the [repository](https://github.com/Ray1235/CoDMayaTools/archive/master.zip) or just the [CoDMayaTools.py](https://raw.githubusercontent.com/Ray1235/CoDMayaTools/master/CoDMayaTools.py) file (right click & save). You'll only need that single file.

2) Copy CoDMayaTools.py to:

```
<USER>\Documents\maya\<Your maya version>\scripts
```

![scripts dir](http://i.imgur.com/UZdXYN1.png)

3) Open usersetup.mel (create one if it doesn't exist) and paste this

```
python("import CoDMayaTools")
```

4) Save and close the file and launch Maya

5) First-time config will occur. The plugin will ask you for your game's root directory and if you'll be using Export2Bin.

6) You're all set! Be sure to visit this repo often for updates!
