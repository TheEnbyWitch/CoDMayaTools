# Copyright 2016, Ray1235

# CoDMayaTools is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# -----------------------------------------------------------------------------------------
#
#	Change log now available on Github!
#

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------- Customization (You can change these values!) ----------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
MAX_WARNINGS_SHOWN = 100 # Maximum number of warnings to show per export
EXPORT_WINDOW_NUMSLOTS = 100 # Number of slots in the export windows
CONVERT_BLACK_VERTS_TO_WHITE = True # To automatically export any black vertices as white, set to 'True'. Otherwise, set to 'False'.

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------- Global ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
import os
import maya.cmds as cmds
import maya.mel as mel
import math
import sys
import datetime
import os.path
import traceback
import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim
import urllib2
import socket
import subprocess
import webbrowser
import Queue
import _winreg as reg
import time
import struct
import shutil
import zipfile
import re
from subprocess import Popen, PIPE, STDOUT


WarningsDuringExport = 0 # Number of warnings shown during current export
CM_TO_INCH = 0.3937007874015748031496062992126 # 1cm = 50/127in
FILE_VERSION = 2.54
VERSION_CHECK_URL = "https://raw.githubusercontent.com/Ray1235/CoDMayaTools/master/version"
GLOBAL_STORAGE_REG_KEY = (reg.HKEY_CURRENT_USER, "Software\\CoDMayaTools") # Registry path for global data storage
#				name	 : 		control code name,				control friendly name,	data storage node name,	refresh function,		export function
OBJECT_NAMES = 	{'menu'  : 		["CoDMayaToolsMenu",    		"Call of Duty Tools", 	None,					None,					None],
				 'progress' :	["CoDMayaToolsProgressbar",	 	"Progress", 			None,					None,					None],
				 'xmodel':		["CoDMayaXModelExportWindow", 	"Export XModel",		"XModelExporterInfo",	"RefreshXModelWindow",	"ExportXModel"],
				 'xanim' :		["CoDMayaXAnimExportWindow",  	"Export XAnim",			"XAnimExporterInfo",	"RefreshXAnimWindow",	"ExportXAnim"],
				 'xcam' :		["CoDMayaXCamExportWindow",  	"Export XCam",			"XCamExporterInfo",		"RefreshXCamWindow",	"ExportXCam"]}

WORKING_DIR = os.path.dirname(os.path.realpath(__file__))

currentGame = "none"
# Format (JOINT, PARENTNAME) : NEWNAME
# Leave parent to None to rename regardless.
RENAME_DICTONARY = {("tag_weapon", "tag_torso") : "tag_weapon_right",
					("tag_weapon1", "tag_torso") : "tag_weapon_left",
					("j_gun", None) : "tag_weapon",
					("j_gun1", None) : "tag_weapon_le",
					("tag_flash1", "j_gun1") : "tag_flash_le",
					("tag_brass1", None) : "tag_brass_le",
}

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------ Init ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
def CreateMenu():
	cmds.setParent(mel.eval("$temp1=$gMainWindow"))
	
	if cmds.control(OBJECT_NAMES['menu'][0], exists=True):
		cmds.deleteUI(OBJECT_NAMES['menu'][0], menu=True)
	
	menu = cmds.menu(OBJECT_NAMES['menu'][0], label=OBJECT_NAMES["menu"][1], tearOff=True)
	
	# Export tools
	cmds.menuItem(label=OBJECT_NAMES['xmodel'][1]+"...", command="CoDMayaTools.ShowWindow('xmodel')")
	cmds.menuItem(label=OBJECT_NAMES['xanim'][1]+"...", command="CoDMayaTools.ShowWindow('xanim')")
	cmds.menuItem(label=OBJECT_NAMES['xcam'][1]+"...", command="CoDMayaTools.ShowWindow('xcam')")
	
	# Viewmodel controls submenu
	cmds.menuItem(label="ViewModel Tools", subMenu=True)
	cmds.menuItem(label="Create New Gunsleeve Maya File", command=CreateNewGunsleeveMayaFile)
	cmds.menuItem(label="Create New ViewModel Rig File", command=CreateNewViewmodelRigFile)
	cmds.menuItem(label="Switch Gun in Current Rig File", command=SwitchGunInCurrentRigFile)
	cmds.setParent(menu, menu=True)
	
	# Import tools
	cmds.menuItem(divider=True)
	cmds.menuItem(label="Import XModel...", subMenu=True)
	cmds.menuItem(label="...from CoD5", command="CoDMayaTools.ImportXModel('CoD5')")
	cmds.menuItem(label="...from CoD4", command="CoDMayaTools.ImportXModel('CoD4')")
	cmds.setParent(menu, menu=True)
	
	# Ray's Animation Toolkit
	cmds.menuItem(divider=True)
	cmds.menuItem(label="Ray's Camera Animation Toolkit", subMenu=True)
	cmds.menuItem(label="Mark as camera", command="CoDMayaTools.setObjectAlias('camera')")
	cmds.menuItem(label="Mark as weapon", command="CoDMayaTools.setObjectAlias('weapon')")
	cmds.menuItem(divider=True)
	cmds.menuItem(label="Generate camera animation", command="CoDMayaTools.GenerateCamAnim()")
	cmds.menuItem(divider=True)
	cmds.menuItem(label="Remove camera animation in current range", command=RemoveCameraKeys)
	cmds.menuItem(label="Reset camera", command=RemoveCameraAnimData)
	cmds.setParent(menu, menu=True)
	
	# IWIxDDS
	cmds.menuItem(divider=True)
	cmds.menuItem(label="Convert IWI to DDS", command="CoDMayaTools.IWIToDDSUser()")
	
	# Root folder
	cmds.menuItem(divider=True)
	cmds.menuItem(label="Set Root Folder",  command="CoDMayaTools.SetRootFolder(None, 'CoD5')")

	# Settings
	cmds.menuItem(divider=True)
	cmds.menuItem(label="Settings", subMenu=True)
	cmds.menuItem(label="Set Root Folder",  command="CoDMayaTools.SetRootFolder(None, 'CoD5')")
	cmds.menuItem(divider=True)
	cmds.menuItem("E2B", label='Use ExportX', checkBox=QueryToggableOption('E2B'), command="CoDMayaTools.SetToggableOption('E2B')" )
	cmds.menuItem(label="Set Path to ExportX", command="CoDMayaTools.SetExport2Bin()")
	cmds.menuItem(divider=True)
	cmds.menuItem("AutomaticRename", label='Automatically rename joints (J_GUN, etc.)', checkBox=QueryToggableOption('AutomaticRename'), command="CoDMayaTools.SetToggableOption('AutomaticRename')" )
	cmds.menuItem(divider=True)
	cmds.menuItem("CoD1Mode", label='CoD1 Mode', checkBox=QueryToggableOption('CoD1Mode'), command="CoDMayaTools.SetToggableOption('CoD1Mode')" )
	cmds.menuItem("AutoUpdate", label='Auto Updates', checkBox=QueryToggableOption('AutoUpdate'), command="CoDMayaTools.SetToggableOption('AutoUpdate')" )
	cmds.menuItem("PrintExport", label='Print xmodel_export information.', checkBox=QueryToggableOption('PrintExport'), command="CoDMayaTools.SetToggableOption('PrintExport')" )
	cmds.setParent(menu, menu=True)
	cmds.menuItem(divider=True)
	# For easy script updating
	cmds.menuItem(label="Reload Script", command="reload(CoDMayaTools)")
	
	# Tools Info
	cmds.menuItem(label="About", command="CoDMayaTools.AboutWindow()")

				 
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------- Import Common --------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
def ImportFileSelectDialog(codRootPath, type):
	importFrom = None
	if cmds.about(version=True)[:4] == "2012": # There is a bug in later versions of Maya with the file browser dialog and files with no extension
		importFrom = cmds.fileDialog2(fileMode=1, fileFilter="%s Files (*)" % type, caption="Import %s" % type, startingDirectory=os.path.join(codRootPath, "raw/%s/" % type.lower()))
	else:
		importFrom = cmds.fileDialog2(fileMode=1, dialogStyle=1, fileFilter="%s Files (*)" % type, caption="Import %s" % type, startingDirectory=os.path.join(codRootPath, "raw/%s/" % type.lower()))

	if importFrom == None or len(importFrom) == 0 or importFrom[0].strip() == "":
		return None
	path = importFrom[0].strip()
	
	pathSplit = os.path.splitext(path) # Fix bug with Maya 2013
	if pathSplit[1] == ".*":
		path = pathSplit
	
	return path
	
def UnitQuaternionToDegrees(x, y, z):
	w = math.sqrt(1 - x*x - y*y - z*z) # The 4th component of a quaternion can be found from the other 3 components in unit quaternions
	euler = OpenMaya.MQuaternion(x, y, z, w).asEulerRotation()
	return (math.degrees(euler.x), math.degrees(euler.y), math.degrees(euler.z))
	
def ReadJointRotation(f):
	rot = struct.unpack('<hhh', f.read(6))
	# Rotation is stored as a unit quaternion, but only the X, Y, and Z components are given, as integers scaled to -32768 to 32767
	rot = UnitQuaternionToDegrees(rot[0] / 32768.0, rot[1] / 32768.0, rot[2] / 32768.0)
	return rot

def ReadNullTerminatedString(f):
	byte = f.read(1)
	string = ""
	while struct.unpack('B', byte)[0] != 0:
		string += byte
		byte = f.read(1)
		
	return string
	
def AutoCapsJointName(name):
	if name.startswith("tag"):
		return name.upper()
		
	name = name.capitalize()
	
	name = name.replace("_le_", "_LE_")
	name = name.replace("_ri_", "_RI_")
	
	if name[-3:] == "_le":
		name = name[:-3] + "_LE"
	if name[-3:] == "_ri":
		name = name[:-3] + "_RI"
	
	# Capitalize the letter after each underscore
	indices = set([m.start() for m in re.finditer("_", name)])
	return "".join(c.upper() if (i-1) in indices else c for i, c in enumerate(name))

	
	
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------- Import XAnim --------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
def ImportXAnim(game):
	codRootPath = GetRootFolder(True, game) # Only call this once, because it might create a dialog box
	xanimPath = ImportFileSelectDialog(codRootPath, "XAnim")
	if not xanimPath:
		return
		
	print("Importing XAnim '%s'" % os.path.basename(xanimPath))
	with open(xanimPath, "rb") as f:
		# Check file version
		version = f.read(2)
		if len(version) == 0 or struct.unpack('H', version)[0] != 17:
			MessageBox("ERROR: Not a valid XAnim file")
			return
		
		# Header
		numFrames = struct.unpack('<H', f.read(2))[0]
		numJoints = struct.unpack('<H', f.read(2))[0]
		fileInfoBitfield = struct.unpack('<H', f.read(2))[0]
		framerate = struct.unpack('<H', f.read(2))[0]
		
		# Get anim type as string
		animType = "absolute"
		if fileInfoBitfield & 2:
			animType = "delta"
		elif fileInfoBitfield & 256:
			animType = "relative"
		elif fileInfoBitfield & 1024:
			animType = "additive"
		
		# ???
		if animType == "absolute":
			f.read(2) # ???
		else:
			print("Cannot read anim type '%s'" % animType)
			return
			
		# Read joint names
		joints = []
		for i in range(numJoints):
			joints.append(ReadNullTerminatedString(f))
		print joints
		
		# Read joint frame data
		for i in range(numJoints):
			numRotations = struct.unpack('<H', f.read(2))[0]
			for j in range(numRotations):
				rot = ReadJointRotation(f)
				
			numPositions = struct.unpack('<H', f.read(2))[0]
			for j in range(numPositions):
				pos = struct.unpack('<fff', f.read(12))
				print pos
		
		
		
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------- Import XModel -------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
def ImportXModel(game):
	codRootPath = GetRootFolder() # Only call this once, because it might create a dialog box
	xmodelPath = ImportFileSelectDialog(codRootPath, "XModel")
	if not xmodelPath:
		return
	
	# Show progress bar
	if cmds.control("w"+OBJECT_NAMES['progress'][0], exists=True):
		cmds.deleteUI("w"+OBJECT_NAMES['progress'][0])
	progressWindow = cmds.window("w"+OBJECT_NAMES['progress'][0], title=OBJECT_NAMES['progress'][1], width=302, height=22)
	cmds.columnLayout()
	progressControl = cmds.progressBar(OBJECT_NAMES['progress'][0], width=300, progress=0)
	cmds.showWindow(progressWindow)
	cmds.refresh() # Force the progress bar to be drawn
	
	try:
		print("Importing XModel '%s'" % os.path.basename(xmodelPath))
		with open(xmodelPath, "rb") as f:
			version = f.read(2)
			if len(version) == 0 or struct.unpack('H', version)[0] != 25:
				MessageBox("ERROR: Not a valid XModel file")
				return
			
			if game == "CoD4":
				f.read(25) # ???
			elif game == "CoD5":
				f.read(26) # ???
			
			ReadNullTerminatedString(f) # ???
			
			lods = []
			for i in range(4): # 4 is possible number of lods
				someInt = struct.unpack('<I', f.read(4))
				lodFileName = ReadNullTerminatedString(f)
				
				if lodFileName != "":
					lods.append({"name":lodFileName})
					
			if len(lods) == 0:
				MessageBox("ERROR: This XModel has no data (no LOD files)!")
				return
				
			f.read(4) # Spacer if next int isn't 0, otherwise ???
			count = struct.unpack('<I', f.read(4))[0]
			print (lods, count)
			for i in range(count):
				subcount = struct.unpack('<I', f.read(4))[0]
				f.read((subcount * 48) + 36) # ???
			
			for lod in lods:
				materials = []
				numMaterials = struct.unpack('<H', f.read(2))[0]
				for i in range(numMaterials):
					materials.append(ReadNullTerminatedString(f))
				lod["materials"] = materials
				
			# Load joint data (24 bytes per joint) ???
			
			lodToLoad = lods[0]
			
			if len(lods) > 1:
				buttons = []
				lodDict = {}
				for lod in lods:
					buttons.append(lod["name"])
					lodDict[lod["name"]] = lod
				buttons.sort()
				
				result = cmds.confirmDialog(title="Select LOD level", message="This model has more than one LOD level. Select which one to import:", button=buttons, defaultButton=buttons[0], dismissString="EXIT")
				if result in lodDict:
					lodToLoad = lodDict[result]
			
			lodToLoad["transformGroup"] = cmds.group(empty=True, name=lodToLoad["name"])
			
			lodToLoad["materialMaps"] = LoadMaterials(lodToLoad, codRootPath)
			lodToLoad["joints"] = LoadJoints(lodToLoad, codRootPath)
			LoadSurfaces(lodToLoad, codRootPath)
			AutoIKHandles(lodToLoad)
			cmds.select(lodToLoad["transformGroup"], replace=True)
	finally:
		# Delete progress bar
		cmds.deleteUI(progressWindow, window=True)
	
def LoadSurfaces(lod, codRootPath):
	print("Loading XModel surface '%s'" % lod["name"])
	
	with open(os.path.join(codRootPath, "raw/xmodelsurfs/%s" % lod["name"]), "rb") as f:
		version = f.read(2)
		if len(version) == 0 or struct.unpack('H', version)[0] != 25:
			MessageBox("ERROR: Not a valid XModel surface file")
			return
		
		numMeshes = struct.unpack('<H', f.read(2))[0]
		
		if numMeshes != len(lod["materials"]):
			MessageBox("ERROR: Different number of meshes and materials on LOD '%s'" % lod["name"])
			return
		
		meshesCreated = []
		
		cmds.progressBar(OBJECT_NAMES['progress'][0], edit=True, maxValue=numMeshes*5+1, progress=0)
		
		for i in range(numMeshes):
			cmds.window("w"+OBJECT_NAMES['progress'][0], edit=True, title="Loading mesh %i..." % i)
			
			# Read mesh header
			a = struct.unpack('<B', f.read(1))[0] # ???
			b = struct.unpack('<H', f.read(2))[0] # ???
			
			numVerts = struct.unpack('<H', f.read(2))[0]
			numTris = struct.unpack('<H', f.read(2))[0]
			numVerts2 = struct.unpack('<H', f.read(2))[0]
			
			physiqued = numVerts != numVerts2
			if physiqued:
				f.read(2) # ???
				print("\tMesh %i is physiqued... this may not load correctly" % i)
				if numVerts2 != 0:
					while struct.unpack('H', f.read(2))[0] != 0: # Search for next 0 short ???
						pass
					f.read(2) # ???
			else:
				f.read(4) # ???
			
			vertexArray = OpenMaya.MFloatPointArray()
			uArray = OpenMaya.MFloatArray()
			vArray = OpenMaya.MFloatArray()
			polygonCounts = OpenMaya.MIntArray(numTris, 3)
			polygonConnects = OpenMaya.MIntArray()
			vertsWeights = []
			
			ProgressBarStep()
			
			# Read vertices
			for j in range(numVerts):
				f.read(12) # ???
				
				color = struct.unpack('<BBBB', f.read(4))
				uv = struct.unpack('<ff', f.read(8))
				
				f.read(24) # ???
				
				numWeights = 0
				finalBoneNumber = 0
				
				if physiqued:
					numWeights = struct.unpack('<B', f.read(1))[0]
					finalBoneNumber = struct.unpack('<H', f.read(2))[0]
					
				pos = struct.unpack('<fff', f.read(12))
				
				totalWeight = 0
				weights = []
				
				for k in range(numWeights):
					weight = struct.unpack('<HH', f.read(4)) # [0] = bone number, [1] = weight mapped to integer (range 0-(2^16))
					totalWeight += weight[1] / 65536.0
					weights.append((lod["joints"][weight[0]]["name"], weight[1] / 65536.0))
				
				weights.append((lod["joints"][finalBoneNumber]["name"], 1 - totalWeight)) # Final bone gets remaining weight
				vertsWeights.append(weights)
				
				vertexArray.append(pos[0]/CM_TO_INCH, pos[1]/CM_TO_INCH, pos[2]/CM_TO_INCH)
				uArray.append(uv[0])
				vArray.append(1-uv[1])
			
			# Read face indices
			for j in range(numTris):
				face = struct.unpack('<HHH', f.read(6))
				polygonConnects.append(face[0])
				polygonConnects.append(face[1])
				polygonConnects.append(face[2])
			
			ProgressBarStep()
			
			# Create mesh
			mesh = OpenMaya.MFnMesh()
			transform = mesh.create(numVerts, numTris, vertexArray, polygonCounts, polygonConnects)
			
			# UV map
			mesh.setUVs(uArray, vArray)
			mesh.assignUVs(polygonCounts, polygonConnects)
			
			# Rename mesh
			transformDagPath = OpenMaya.MDagPath()
			OpenMaya.MDagPath.getAPathTo(transform, transformDagPath)
			
			newPath = cmds.parent(transformDagPath.fullPathName(), lod["transformGroup"])
			newPath = cmds.rename(newPath, "mesh%i" % i)
			
			meshesCreated.append(newPath)
			
			ProgressBarStep()
			
			# Joint weights
			# TODO: Make this faster!!! Soooo sloowwwwwww
			skin = cmds.skinCluster(lod["joints"][0]["name"], newPath)[0] # Bind the mesh to the root joint for now
			for j, vertWeights in enumerate(vertsWeights): 
				cmds.skinPercent(skin, "%s.vtx[%i]" % (newPath, j), zeroRemainingInfluences=True, transformValue=vertWeights)
			
			ProgressBarStep()	
				
			# Apply textures
			shader = cmds.shadingNode("lambert", name=lod["materials"][i], asShader=True)
			cmds.select(newPath)
			cmds.hyperShade(assign=shader)

			colorMap = cmds.shadingNode("file", name=lod["materials"][i] + "_colorMap", asTexture=True)
			cmds.connectAttr("%s.outColor" % colorMap, "%s.color" % shader)
			
			if "colorMap" in lod["materialMaps"][lod["materials"][i]]:
				cmds.setAttr("%s.fileTextureName" % colorMap, os.path.join(codRootPath, "raw/images/%s/%s.dds" % (lod["name"], lod["materialMaps"][lod["materials"][i]]["colorMap"])), type="string")
			
			# Merge duplicates
			mel.eval("polyMergeVertex  -d 0.01 -am 1 -ch 0 %s;" % newPath) # Merge duplicate verts
			mel.eval("polyMergeUV -d 0.01 -ch 0 %s;" % newPath) # Merge duplicate UVs
			ProgressBarStep()
			
		if len(f.read(1)) != 0: # Check if it's at the end of the file
			MessageBox("The export completed, however it's quite likely that at least one of the meshes did not import correctly. See the Script Editor output for more information.")
	ProgressBarStep()
			
def LoadJoints(lod, codRootPath):
	print("Loading XModel joints '%s'" % lod["name"])
	cmds.window("w"+OBJECT_NAMES['progress'][0], edit=True, title="Loading joints...")
	
	joints = []
	with open(os.path.join(codRootPath, "raw/xmodelparts/%s" % lod["name"]), "rb") as f:
		version = f.read(2)
		if len(version) == 0 or struct.unpack('H', version)[0] != 25:
			MessageBox("ERROR: Not a valid XModel parts file")
			return

		# Number of bones
		numJoints = struct.unpack('<H', f.read(2))[0]

		cmds.progressBar(OBJECT_NAMES['progress'][0], edit=True, maxValue=numJoints*2+1, progress=0)
		
		if numJoints == 0: # Special case
			joints.append({"parent": -1, "pos": (0.0,0.0,0.0), "rot": (0.0,0.0,0.0), "name": "TAG_ORIGIN"})
			cmds.select(clear=True)
			cmds.joint(name=joints[0]["name"], orientation=(0.0,0.0,0.0), position=(0.0,0.0,0.0), relative=True)
			ProgressBarStep()
			return joints
			
		
		f.read(2) # ???

		# Joint data
		joints.append({"parent": -1, "pos": (0.0,0.0,0.0), "rot": (0.0,0.0,0.0)}) # parent joint
		for i in range(numJoints):
			parentJoint = struct.unpack('<B', f.read(1))[0]
			pos = struct.unpack('<fff', f.read(12))
			rot = ReadJointRotation(f)
			
			joints.append({"parent": parentJoint, "pos": pos, "rot": rot})
			ProgressBarStep()

		for i in range(numJoints+1):
			joints[i]["name"] = AutoCapsJointName(ReadNullTerminatedString(f))

		for joint in joints:
			if joint["parent"] >= 0: # Select parent
				cmds.select(joints[joint["parent"]]["name"], replace=True)
			else:
				cmds.select(clear=True)
			
			cmds.joint(name=joint["name"], orientation=joint["rot"], position=(joint["pos"][0]/CM_TO_INCH, joint["pos"][1]/CM_TO_INCH, joint["pos"][2]/CM_TO_INCH), relative=True)
			ProgressBarStep()
	
	ProgressBarStep()
	return joints
			
def LoadMaterials(lod, codRootPath):
	noDupMaterials = list(set(lod["materials"]))
	
	cmds.window("w"+OBJECT_NAMES['progress'][0], edit=True, title="Loading materials...")
	cmds.progressBar(OBJECT_NAMES['progress'][0], edit=True, maxValue=len(noDupMaterials)*2+1, progress=0)
	
	iwdImages = LoadMainIWDImages(codRootPath)
	ProgressBarStep()
	
	# Create output folder
	if not os.path.exists(os.path.join(codRootPath, "raw/images/%s/" % lod["name"])):
		os.mkdir(os.path.join(codRootPath, "raw/images/%s/" % lod["name"]))
	
	# Create material info file
	infofile = open(os.path.join(codRootPath, "raw/images/%s/%s" % (lod["name"], "%s Material Info.txt" % lod["name"])), "w")
	
	# Load materials
	outMaterialList = {}
	for material in noDupMaterials:
		materialMaps = {}
		# http://www.diegologic.net/diegologic/Programming/CoD4%20Material.html
		print("Loading material '%s'" % material)
		with open(os.path.join(codRootPath, "raw/materials/%s" % material), "rb") as f:
			f.read(48) # Skip start of header
			numMaps = struct.unpack('<H', f.read(2))[0]
			f.read(14) # Skip the rest of header
			
			for i in range(numMaps):
				mapTypeOffset = struct.unpack('<I', f.read(4))[0]
				f.read(4) # Skip
				mapNameOffset = struct.unpack('<I', f.read(4))[0]
				current = f.tell()
				
				f.seek(mapTypeOffset)
				mapType = ReadNullTerminatedString(f)
				f.seek(mapNameOffset)
				mapName = ReadNullTerminatedString(f)
				f.seek(current)
				materialMaps[mapType] = mapName
		
		infofile.write("Material: %s\n" % material)
		for type, mapName in materialMaps.items():
			infofile.write("\t%s: %s\n" % (type, mapName))
		infofile.write("\n")
		
		outMaterialList[material] = materialMaps
		ProgressBarStep()
		
		# Gather .iwis
		rawImages = os.listdir(os.path.join(codRootPath, "raw/images/"))
		for type, mapName in materialMaps.items():
			outPath = os.path.join(codRootPath, "raw/images/%s/%s%s" % (lod["name"], mapName, ".iwi"))
			if os.path.exists(outPath):
				continue
			
			if (mapName + ".iwi") in rawImages:
				shutil.copy(os.path.join(codRootPath, "raw/images/%s%s" % (mapName, ".iwi")), os.path.join(codRootPath, "raw/images/%s/" % lod["name"]))
			elif (mapName + ".iwi") in iwdImages:
				iwdName = iwdImages[mapName + ".iwi"]
				zip = zipfile.ZipFile(os.path.join(codRootPath, "main/%s" % iwdName), "r")	
				
				# Extract from zip
				source = zip.open("images/%s%s" % (mapName, ".iwi"))
				target = file(outPath, "wb")
				shutil.copyfileobj(source, target)
				source.close()
				target.close()		
			
			if type == "colorMap":
				IWIToDDS(outPath)
				
		ProgressBarStep()
			
	infofile.close()
	return outMaterialList

def AutoIKHandles(lod):
	if len(lod["joints"]) < 2:
		return
		
	result = cmds.confirmDialog(title="Auto IK Handles", message="Is this a character (player or AI) model?", button=["Yes", "No"], defaultButton="No", dismissString="No")
	if result == "Yes":
		# Arms
		SafeIKHandle("IK_Arm_LE", "J_Shoulder_LE", "J_Wrist_LE")
		SafeIKHandle("IK_Arm_RI", "J_Shoulder_RI", "J_Wrist_RI")
		
		# Left hand
		SafeIKHandle("IK_Index_LE", "J_Index_LE_1", "J_Index_LE_3")
		SafeIKHandle("IK_Mid_LE", "J_Mid_LE_1", "J_Mid_LE_3")
		SafeIKHandle("IK_Ring_LE", "J_Ring_LE_1", "J_Ring_LE_3")
		SafeIKHandle("IK_Pinky_LE", "J_Pinky_LE_1", "J_Pinky_LE_3")
		SafeIKHandle("IK_Thumb_LE", "J_Thumb_LE_1", "J_Thumb_LE_3")
		
		# Right hand
		SafeIKHandle("IK_Index_RI", "J_Index_RI_1", "J_Index_RI_3")
		SafeIKHandle("IK_Mid_RI", "J_Mid_RI_1", "J_Mid_RI_3")
		SafeIKHandle("IK_Ring_RI", "J_Ring_RI_1", "J_Ring_RI_3")
		SafeIKHandle("IK_Pinky_RI", "J_Pinky_RI_1", "J_Pinky_RI_3")
		SafeIKHandle("IK_Thumb_RI", "J_Thumb_RI_1", "J_Thumb_RI_3")
		
		# Legs
		SafeIKHandle("IK_Leg_LE", "J_Hip_LE", "J_Ankle_LE")
		SafeIKHandle("IK_Leg_RI", "J_Hip_RI", "J_Ankle_RI")

def SafeIKHandle(name, joint1, joint2):
	# Only apply the IK Handle if both joints exist
	if cmds.objExists(joint1) and cmds.nodeType(joint1) == 'joint' and cmds.objExists(joint2) and cmds.nodeType(joint2) == 'joint':
		cmds.ikHandle(name=name, startJoint=joint1, endEffector=joint2)	
	
def LoadMainIWDImages(codRootPath):
	iwdImages = {}
	
	if not os.path.exists(os.path.join(codRootPath, "main/")):
		return iwdImages
		
	iwds = os.listdir(os.path.join(codRootPath, "main/"))
	for iwd in iwds:
		if not iwd.endswith(".iwd"):
			continue
			
		zip = zipfile.ZipFile(os.path.join(codRootPath, "main/") + iwd, "r")
		images = zip.namelist()
		images = [x for x in images if x.startswith("images/")]
		for i in range(len(images)):
			imageName = images[i][7:]
			if len(imageName) > 0:
				iwdImages[imageName] = iwd
	
	return iwdImages
	
	
	
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------- IWI to DDS ---------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------	
def IWIToDDS(inIWIPath):
	splitPath = os.path.splitext(inIWIPath)
	outDDSPath = splitPath[0] + ".dds"
	
	print("Converting %s to DDS" % os.path.basename(inIWIPath))
	
	if not os.path.exists(inIWIPath):
		return False
		
	with open(inIWIPath, 'rb') as inf:
		# http://www.matejtomcik.com/Public/Projects/IWIExtractor/
		if inf.read(3) != "IWi": # Read file identifier
			print("\tERROR: Not a valid IWI file")
			return False
			
		header = struct.unpack('<BBBHHBBIIII', inf.read(25))
		
		if header[0] != 6: # Make sure the IWI version is 6
			print("\tERROR: Unsupported IWI version")
			return False
		
		imageType = None
		
		if header[1] == 0xB: # DXT1
			imageType = "DXT1"
		elif header[1] == 0xC: # DXT3
			imageType = "DXT3"
		elif header[1] == 0xD: # DXT5
			imageType = "DXT5"
		else:
			print("\tERROR: Unknown image format")
			return False
		
		with open(outDDSPath, 'wb') as outf:
			# http://msdn.microsoft.com/en-us/library/windows/desktop/bb943991(v=vs.85).aspx
			outf.write("DDS ") # File indentifier
			
			# DDS_HEADER				  size, flags, height,	  width,	 pitch, depth, mipmap count
			outf.write(struct.pack('<7I', 124, 659463, header[4], header[3], 0, 	0, 	   1))
			outf.write(struct.pack('<11I', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)) # Reserved
			# DDS_PIXELFORMAT		  	     size,  flags, type,  masks
			outf.write(struct.pack('II4s5I', 32, 	4, imageType, 0, 0, 0, 0, 0))
			# DDS_HEADER			    caps1
			outf.write(struct.pack('5I', 4198408, 0, 0, 0, 0))
			
			# Copy main image data to outfile
			inf.seek(header[8])
			outf.write(inf.read(header[7] - header[8]))
			
			# For now, don't bother copying the other mipmaps
			
			# Copy mipmap 1
			#inf.seek(header[9])
			#outf.write(inf.read(header[8] - header[9]))
			
			# Copy mipmap 2
			#inf.seek(header[10])
			#outf.write(inf.read(header[9] - header[10]))
			
			# Copy the rest of the data ???
			#inf.seek(28)
			
	return True

def IWIToDDSUser():
	codRootPath = GetRootFolder() # Only call this once, because it might create a dialog box
	files = cmds.fileDialog2(fileMode=4, fileFilter="IWI Images (*.iwi)", caption="Select IWI file", startingDirectory=os.path.join(codRootPath, "raw/images/"))
	if files == None or len(files) == 0 or files[0].strip() == "":
		return
	success = True
	for file in files:
		if not IWIToDDS(file):
			success = False
			
	if not success:
		MessageBox("One or more of the IWIs failed to convert. See the Script Editor output for more information.")

		
			
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------				
# ---------------------------------------------------------------- Export Joints (XModel and XAnim) ----------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
def GetJointList():
	# Joints list.
	joints = []
	# Try get the cosmetic bone.
	try:
		# Get it.
		cosmeticBone = cmds.getAttr(OBJECT_NAMES["xmodel"][2]+ ".Cosmeticbone").split("|")[-1].split(":")[-1]
		# Does it exist in scene?
		if not cmds.objExists(cosmeticBone):
			# If it doesn't, don't assign a cosmetic bone.
			cosmeticBone = None
		else:
			cosmeticBone = cosmeticBone.split("|")[-1].split(":")[-1]
	except:
		# No cosmetic set.
		cosmeticBone = None
	# Cosmetic Bones List
	cosmetic_list = []
	# Cosmetic Bone ID (for xmodel_export)
	cosmetic_id = 0
	
	# Get selected objects
	selectedObjects = OpenMaya.MSelectionList()
	OpenMaya.MGlobal.getActiveSelectionList(selectedObjects)
	
	for i in range(selectedObjects.length()):
		# Get object path and node
		dagPath = OpenMaya.MDagPath()
		selectedObjects.getDagPath(i, dagPath)
		dagNode = OpenMaya.MFnDagNode(dagPath)
		
		# Ignore nodes that aren't joints or arn't top-level
		if not dagPath.hasFn(OpenMaya.MFn.kJoint) or not RecursiveCheckIsTopNode(selectedObjects, dagNode):
			continue
		
		# Breadth first search of joint tree
		searchQueue = Queue.Queue(0)
		searchQueue.put((-1, dagNode, True)) # (index = child node's parent index, child node)
		while not searchQueue.empty():
			node = searchQueue.get()
			index = len(joints)
			
			if node[2]:
				# Don't use main root bone.
				if node[0] > -1:
					# Name of the bones parent, none for Root bone. Split it to remove dagpath seperator and namespace.
					bone_parentname = joints[node[0]][1].split("|")[-1].split(":")[-1]
				else:
					# Skip.
					bone_parentname = None
				# Name of the bone. Split it to remove dagpath seperator and namespace.
				bone_name = node[1].partialPathName().split("|")[-1].split(":")[-1]
				# Check for automatic rename.
				if QueryToggableOption("AutomaticRename"):
					# Run over dictonary for possible joints to rename.
					for potjoints, new_name in RENAME_DICTONARY.iteritems():
						# Found one
						if bone_name == potjoints[0]:
							# Check if it's a child bone of what we want, None to rename regardless.
							if potjoints[1] is None or potjoints[1] == bone_parentname: 
								bone_name = new_name

				# Check if we have cosmetic bone.
				if cosmeticBone is not None and bone_parentname == cosmeticBone:
					# Append it.
					cosmetic_list.append((node[0], bone_name, node[1]))
				else:
					# Not a cosmetic, add it to normal joints.
					joints.append((node[0], bone_name, node[1]))
				
				# Our cosmetic parent.
				if bone_name == cosmeticBone:
					cosmetic_id = index


			else:
				index = node[0]
			
			for i in range(node[1].childCount()):
				dagPath = OpenMaya.MDagPath()
				childNode = OpenMaya.MFnDagNode(node[1].child(i))
				childNode.getPath(dagPath)
				searchQueue.put((index, childNode, selectedObjects.hasItem(dagPath) and dagPath.hasFn(OpenMaya.MFn.kJoint)))

	# Cosmetic bones must be at the end, so append them AFTER we've added other bones.
	joints = joints + cosmetic_list

	LogExport("Exporting %i joints\n" % len(joints))
	LogExport("Exporting %i cosmetics." % len(cosmetic_list))

	return joints, cosmetic_list, cosmetic_id

def GetCameraList():
	cameras = []
	
	# Get selected objects
	selectedObjects = OpenMaya.MSelectionList()
	OpenMaya.MGlobal.getActiveSelectionList(selectedObjects)
	
	for i in range(selectedObjects.length()):
		# Get object path and node
		dagPath = OpenMaya.MDagPath()
		selectedObjects.getDagPath(i, dagPath)
		dagNode = OpenMaya.MFnDagNode(dagPath)
		
		# Ignore nodes that aren't cameras or arn't top-level
		if not dagPath.hasFn(OpenMaya.MFn.kCamera):
			ProgressBarStep()
			continue
		
		# Breadth first search of camera tree
		searchQueue = Queue.Queue(0)
		searchQueue.put((-1, dagNode, True)) # (index = child node's parent index, child node)
		while not searchQueue.empty():
			node = searchQueue.get()
			index = len(cameras)
			
			if node[2]:
				cameras.append((node[0], node[1]))
			else:
				index = node[0]
			
			for i in range(node[1].childCount()):
				dagPath = OpenMaya.MDagPath()
				childNode = OpenMaya.MFnDagNode(node[1].child(i))
				childNode.getPath(dagPath)
				searchQueue.put((index, childNode, selectedObjects.hasItem(dagPath) and dagPath.hasFn(OpenMaya.MFn.kCamera)))
		
		ProgressBarStep()
	
	return cameras

def RecursiveCheckIsTopNode(cSelectionList, currentNode): # Checks if the given node has ANY selected parent, grandparent, etc joints
	if currentNode.parentCount() == 0:
		return True
	
	for i in range(currentNode.parentCount()):
		parentDagPath = OpenMaya.MDagPath()
		parentNode = OpenMaya.MFnDagNode(currentNode.parent(i))
		parentNode.getPath(parentDagPath)
	
		if not parentDagPath.hasFn(OpenMaya.MFn.kJoint): # Not a joint, but still check parents
			if not RecursiveCheckIsTopNode(cSelectionList, parentNode):
				return False # A parent joint is selected, we're done
			else:
				continue # No parent joints are selected, ignore this node
		
		if cSelectionList.hasItem(parentDagPath):
			return False
		else:
			if not RecursiveCheckIsTopNode(cSelectionList, parentNode):
				return False
				
	return True
	
def WriteJointData(f, jointNode):
	# Get the joint's transform
	path = OpenMaya.MDagPath() 
	jointNode.getPath(path)
	transform = OpenMaya.MFnTransform(path)
	
	# Get joint position
	pos = transform.getTranslation(OpenMaya.MSpace.kWorld)
	
	# Get scale (almost always 1)
	scaleUtil = OpenMaya.MScriptUtil()
	scaleUtil.createFromList([1,1,1], 3)
	scalePtr = scaleUtil.asDoublePtr()
	transform.getScale(scalePtr)
	scale = [OpenMaya.MScriptUtil.getDoubleArrayItem(scalePtr, 0), OpenMaya.MScriptUtil.getDoubleArrayItem(scalePtr, 1), OpenMaya.MScriptUtil.getDoubleArrayItem(scalePtr, 2)]
	
	# Get rotation matrix (mat is a 4x4, but the last row and column arn't needed)
	rotQuaternion = OpenMaya.MQuaternion()
	transform.getRotation(rotQuaternion, OpenMaya.MSpace.kWorld)
	mat = rotQuaternion.asMatrix()
	
	# Debug info: as euler rotation
	#eulerRotation = rotQuaternion.asEulerRotation()
	#eulerRotation.reorderIt(OpenMaya.MEulerRotation.kXYZ)
	
	# Write
	f.write("OFFSET %f, %f, %f\n" % (pos.x*CM_TO_INCH, pos.y*CM_TO_INCH, pos.z*CM_TO_INCH))
	f.write("SCALE %f, %f, %f\n" % (scale[0], scale[1], scale[2]))
	f.write("X %f, %f, %f\n" % (mat(0,0), mat(0,1), mat(0,2)))
	#f.write("\t\t// World-space euler angels XYZ: %f, %f, %f\n" % (math.degrees(eulerRotation.x), math.degrees(eulerRotation.y), math.degrees(eulerRotation.z)))
	f.write("Y %f, %f, %f\n" % (mat(1,0), mat(1,1), mat(1,2)))
	f.write("Z %f, %f, %f\n" % (mat(2,0), mat(2,1), mat(2,2)))

def WriteNodeFloat(f, name, value, no_p=False):
	if no_p:
		f.write("\"%s\" : %f \n" % (name, value))
	else:
		f.write("\"%s\" : %f ,\n" % (name, value))

def WriteCameraData(f, cameraNode):
	# Get the camera's transform
	path = OpenMaya.MDagPath()
	cameraNode.getPath(path)
	transform = OpenMaya.MFnTransform(path)

	#fov = cmds.camera(query=True, horizontalFieldOfView=True)
	#print fov
	fov = 40
	
	# Get camera position
	pos = transform.getTranslation(OpenMaya.MSpace.kWorld)
	
	# Get scale (almost always 1)
	scaleUtil = OpenMaya.MScriptUtil()
	scaleUtil.createFromList([1,1,1], 3)
	scalePtr = scaleUtil.asDoublePtr()
	transform.getScale(scalePtr)
	scale = [OpenMaya.MScriptUtil.getDoubleArrayItem(scalePtr, 0), OpenMaya.MScriptUtil.getDoubleArrayItem(scalePtr, 1), OpenMaya.MScriptUtil.getDoubleArrayItem(scalePtr, 2)]
	
	# Get rotation matrix (mat is a 4x4, but the last row and column arn't needed)
	rotQuaternion = OpenMaya.MQuaternion()
	transform.getRotation(rotQuaternion, OpenMaya.MSpace.kWorld)
	mat = rotQuaternion.asMatrix()
	
	# Debug info: as euler rotation
	eulerRotation = rotQuaternion.asEulerRotation()
	eulerRotation.reorderIt(OpenMaya.MEulerRotation.kXYZ)

	# euler rotation is in radians, not degrees

	eulerRotation.x = eulerRotation.x - (3.141/2)
	eulerRotation.z = eulerRotation.z - (3.141/2)
	#eulerRotation.y = eulerRotation.y + (3.141/2)
	#print ("%f %f %f" % (eulerRotation.x*180/3.141, eulerRotation.y*180/3.141, eulerRotation.z*180/3.141))
	mat = eulerRotation.asMatrix()
	
	# Write
	f.write("\"origin\" : [ %f, %f, %f],\n" % (pos.y*CM_TO_INCH, pos.x*-CM_TO_INCH, pos.z*CM_TO_INCH))
	f.write("\"dir\" : [ %f, %f, %f],\n" % (mat(1,0), mat(1,1), mat(1,2))) #(mat(0,0), mat(0,1), mat(0,2)))
	f.write("\"up\" : [ %f, %f, %f],\n" % (mat(2,0), mat(2,1), mat(2,2))) #(mat(1,0), mat(1,1), mat(1,2)))
	f.write("\"right\" : [ %f, %f, %f],\n" % (mat(0,0), mat(0,1), mat(0,2))) # (mat(2,0), mat(2,1), mat(2,2)))
	WriteNodeFloat(f, "flen", 24.0000)
	WriteNodeFloat(f, "fov", fov)
	WriteNodeFloat(f, "fdist", 400)
	WriteNodeFloat(f, "fstop", 0.7)
	WriteNodeFloat(f, "lense", 10, True)

# Get count for progress bar. No impact on export speed.
def GetNumInfo(selectedObjects):
	# Mesh array to check for duplicates.
	meshes = []
	maxValue = 0

	maxValue += len(cmds.ls(selection = True, type = "joint"))

	for i in range(0, selectedObjects.length()):
		# Grab mesh.
		object = OpenMaya.MObject()
		dagPath = OpenMaya.MDagPath()
		selectedObjects.getDependNode(i, object)
		selectedObjects.getDagPath(i, dagPath)
		# Check it's a mesh.
		if not dagPath.hasFn(OpenMaya.MFn.kMesh):
			continue
		dagPath.extendToShape()
		# Check for duplicate.
		if dagPath.partialPathName() in meshes:
			continue
		# Append.
		meshes.append(dagPath.partialPathName())
		# Get vert count for this mesh.
		maxValue += OpenMaya.MItMeshVertex(dagPath).count()
		# Get Face found for this mesh.
		maxValue += OpenMaya.MItMeshPolygon(dagPath).count()

	# Return value * 2 because we will loop over 2x for getting info and writing it to export.
	return maxValue * 2 + 1
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------- Export XModel -------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
def ExportXModel(filePath):
	# Progress bar
	numSelectedObjects = len(cmds.ls(selection=True))
	if numSelectedObjects == 0:
		return "Error: No objects selected for export"


	# Get data
	joints = GetJointList()
#	if len(joints) > 128:
#		return "Error: More than 128 joints"
	shapes = GetShapes(joints[0])
	
	if type(shapes) == str:
		return shapes
	
	# Open file
	f = None
	try:
		# Create export directory if it doesn't exist
		directory = os.path.dirname(filePath)
		if not os.path.exists(directory):
			os.makedirs(directory)
		
		# Create file
		f = open(filePath, 'w')
	except (IOError, OSError) as e:
		typex, value, traceback = sys.exc_info()
		return "Unable to create file:\n\n%s" % value.strerror
	
	# Write header
	LogExport("\n\nWriting header.\n")
	f.write("// Export filename: '%s'\n" % os.path.normpath(filePath))
	if cmds.file(query=True, exists=True):
		f.write("// Source filename: '%s'\n" % os.path.normpath(os.path.abspath(cmds.file(query=True, sceneName=True))).encode('ascii', 'ignore')) # Ignore Ascii characters using .encode()
	else:
		f.write("// Source filename: Unsaved\n")
	f.write("// Export time: %s\n\n" % datetime.datetime.now().strftime("%a %b %d %Y, %H:%M:%S")) 
	f.write("MODEL\n")

	if QueryToggableOption("CoD1Mode"):
		LogExport("Exporing Version 5 File\n")
		f.write("VERSION 5\n\n")
	else:
		LogExport("Exporing Version 6 File\n")
		f.write("VERSION 6\n\n")
	
	# Write joints
	LogExport("Writing %i joints.\n" % len(joints[0]))
	if len(joints[0]) == 0:
		LogExport("No joints selected; exporting with a default TAG_ORIGIN.\n")
		print "No joints selected; exporting with a default TAG_ORIGIN."
		f.write("NUMBONES 1\n")
		f.write("BONE 0 -1 \"TAG_ORIGIN\"\n\n")
		
		f.write("BONE 0\n")
		f.write("OFFSET 0.000000 0.000000 0.000000\n")
		f.write("SCALE 1.000000 1.000000 1.000000\n")
		f.write("X 1.000000 0.000000 0.000000\n")
		f.write("Y 0.000000 1.000000 0.000000\n")
		f.write("Z 0.000000 0.000000 1.000000\n")
	else:
		LogExport("Writing NUMBONES\n")
		f.write("NUMBONES %i\n" % len(joints[0]))
		if len(joints[1]) > 0:
			LogExport("Writing NUMCOSMETICS\n")
			# NUMCOSMETICS COUNT PARENTID
			f.write("NUMCOSMETICS %i %i\n" % (len(joints[1]), joints[2]) )
		LogExport("Writing Bone table.\n")
		for i, joint in enumerate(joints[0]):
			f.write("BONE %i %i \"%s\"\n" % (i, joint[0], joint[1]))
		LogExport("Writing Bone Information.\n")
		for i, joint in enumerate(joints[0]):
			f.write("\nBONE %i\n" % i)
			WriteJointData(f, joint[2])

	# Write verts
	LogExport("Writing vert data.\n")
	if len(shapes["verts"]) > 65536:
		LogExport("> 65536 verts, use EXPORTX to convert to XMODEL_BIN, will not work in older games.\n")
	f.write("\nNUMVERTS %i\n" % len(shapes["verts"]))
	for i, vert in enumerate(shapes["verts"]):
		f.write("VERT %i\n" % i)
		if QueryToggableOption("CoD1Mode"):
			f.write("OFFSET %f %f %f\n" % (vert[0].x*CM_TO_INCH, vert[0].y*CM_TO_INCH, vert[0].z*CM_TO_INCH)) # Offsets are stored in CM, but cod uses inches
		else:
			f.write("OFFSET %f, %f, %f\n" % (vert[0].x*CM_TO_INCH, vert[0].y*CM_TO_INCH, vert[0].z*CM_TO_INCH)) # Offsets are stored in CM, but cod uses inches
		f.write("BONES %i\n" % max(len(vert[1]), 1))
		if len(vert[1]) > 0:
			for bone in vert[1]:
				f.write("BONE %i %f\n" % (bone[0], bone[1]))
		else:
			f.write("BONE 0 1.000000\n")
		ProgressBarStep()
		f.write("\n")
	
	# Write faces
	LogExport("Writing face data.\n")
	f.write("NUMFACES %i\n" % len(shapes["faces"]))
	for j, face in enumerate(shapes["faces"]):
		f.write("TRI %i %i 0 0\n" % (face[0], face[1]))
		for i in range(0, 3):
			f.write("VERT %i\n" % face[2][i])
			f.write("NORMAL %f %f %f\n" % (face[5][i].x, face[5][i].y, face[5][i].z))
			f.write("COLOR %f %f %f %f\n" % (face[4][i].r, face[4][i].g, face[4][i].b, face[4][i].a))
			f.write("UV 1 %f %f\n" % (face[3][i][0], face[3][i][1]))
		ProgressBarStep()
		f.write("\n")
	
	# Write objects
	LogExport("Writing meshes/objects.\n")
	f.write("NUMOBJECTS %i\n" % len(shapes["meshes"]))
	for i, object in enumerate(shapes["meshes"]):
		f.write("OBJECT %i \"%s\"\n" % (i, object.split(":")[-1]))
	
	# Write materials
	LogExport("Writing materials.\n")
	f.write("\nNUMMATERIALS %i\n" % len(shapes["materials"]))
	for i, material in enumerate(shapes["materials"]):
		if QueryToggableOption("CoD1Mode"):
			f.write("MATERIAL %i \"%s\"\n" % (i, material[0].split(":")[-1]))
		else:
			f.write("MATERIAL %i \"%s\" \"%s\" \"%s\"\n" % (i, material[0].split(":")[-1], "Lambert", material[1]))
		
			# According to the Modrepository page on the XModel format, the following values don't matter
			f.write("COLOR 0.000000 0.000000 0.000000 1.000000\n"
					"TRANSPARENCY 0.000000 0.000000 0.000000 1.000000\n"
					"AMBIENTCOLOR 0.000000 0.000000 0.000000 1.000000\n"
					"INCANDESCENCE 0.000000 0.000000 0.000000 1.000000\n"
					"COEFFS 0.800000 0.000000\n"
					"GLOW 0.000000 0\n"
					"REFRACTIVE 6 1.000000\n"
					"SPECULARCOLOR -1.000000 -1.000000 -1.000000 1.000000\n"
					"REFLECTIVECOLOR -1.000000 -1.000000 -1.000000 1.000000\n"
					"REFLECTIVE -1 -1.000000\n"
					"BLINN -1.000000 -1.000000\n"
					"PHONG -1.000000\n\n")
		
	f.close()
	ProgressBarStep()
	ProgressBarStep()
	cmds.refresh()

	if QueryToggableOption('E2B'):
		LogExport("Converting to XMODEL_BIN\n")
		try:
			RunExport2Bin(filePath)
		except:
			MessageBox("The model exported successfully however Export2Bin failed to run, the model will need to be converted manually.\n\nPlease check your paths.")
	LogExport("\nFile Exported, close window when ready.\n")
def GetMaterialsFromMesh(mesh, dagPath):
	textures = {}
	
	# http://rabidsquirrelgames.googlecode.com/svn/trunk/Maya%20plugin/fileExportCmd.py
	# The code below gets a dictionary of [material name: material file name], ex: [a_material: a_material.dds]
	shaders = OpenMaya.MObjectArray()
	shaderIndices = OpenMaya.MIntArray()
	mesh.getConnectedShaders(dagPath.instanceNumber(), shaders, shaderIndices)
	
	for i in range(shaders.length()):
			shaderNode = OpenMaya.MFnDependencyNode(shaders[i])
			shaderPlug = shaderNode.findPlug("surfaceShader")
			material = OpenMaya.MPlugArray()
			shaderPlug.connectedTo(material, 1, 0);
			
			for j in range(material.length()):
					materialNode = OpenMaya.MFnDependencyNode(material[j].node())
					colorPlug = materialNode.findPlug("color")
					
					dgIt = OpenMaya.MItDependencyGraph(
						colorPlug,
						OpenMaya.MFn.kFileTexture,
						OpenMaya.MItDependencyGraph.kUpstream,
						OpenMaya.MItDependencyGraph.kBreadthFirst,
						OpenMaya.MItDependencyGraph.kNodeLevel)
					
					texturePath = ""
					
					try: # If there is no texture, this part can throw an exception
						dgIt.disablePruningOnFilter()
						textureNode = OpenMaya.MFnDependencyNode(dgIt.currentItem())
						texturePlug = textureNode.findPlug("fileTextureName")
						texturePath = os.path.basename(texturePlug.asString())
					except Exception:
						pass
					
					textures[i] = (materialNode.name(), texturePath)
	
	texturesToFaces = []
	for i in range(shaderIndices.length()):
		if shaderIndices[i] in textures:
			texturesToFaces.append(textures[shaderIndices[i]])
		else:
			texturesToFaces.append(None)
	
	return texturesToFaces

# Converts a set of vertices (toConvertVertexIndices) from object-relative IDs to face-relative IDs
# vertexIndices is a list of object-relative vertex indices in face order (from polyIter.getVertices)
# toConvertVertexIndices is any set of vertices from the same faces as vertexIndices, not necessarily the same length
# Returns false if a vertex index is unable to be converted (= bad vertex values)
def VerticesObjRelToLocalRel(vertexIndices, toConvertVertexIndices):
	# http://svn.gna.org/svn/cal3d/trunk/cal3d/plugins/cal3d_maya_exporter/MayaMesh.cpp
	localVertexIndices = OpenMaya.MIntArray()
	
	for i in range(toConvertVertexIndices.length()):
		found = False
		for j in range(vertexIndices.length()):
			if toConvertVertexIndices[i] == vertexIndices[j]:
				localVertexIndices.append(j)
				found = True
				break
		if not found:
			return False
	
	return localVertexIndices
		
def GetShapes(joints):
	LogExport("Beginning Export...\n")
	# Vars
	meshes = []
	verts = []
	tris = []
	materialDict = {}
	materials = []
	
	# Convert the joints to a dictionary, for simple searching for joint indices
	jointDict = {}
	for i, joint in enumerate(joints):
		jointDict[joint[2].partialPathName()] = i
	
	# Get all selected objects
	selectedObjects = OpenMaya.MSelectionList()
	OpenMaya.MGlobal.getActiveSelectionList(selectedObjects)
	
	# The global vert index at the start of each object
	currentStartingVertIndex = 0


	progressInfo = GetNumInfo(selectedObjects)

	if progressInfo == 0:
		return "No info to export."

	cmds.progressBar(OBJECT_NAMES['progress'][0], edit=True, maxValue = progressInfo)
	
	# Loop through all objects
	for i in range(0, selectedObjects.length()):
		# Get data on object
		object = OpenMaya.MObject()
		dagPath = OpenMaya.MDagPath()
		selectedObjects.getDependNode(i, object)
		selectedObjects.getDagPath(i, dagPath)
		
		# Ignore dag nodes that aren't shapes or shape transforms
		if not dagPath.hasFn(OpenMaya.MFn.kMesh):
			continue
		
		# Lower path to shape node
		# Selecting a shape transform or shape will get the same dagPath to the shape using this
		dagPath.extendToShape()
		
		# Check for duplicates
		if dagPath.partialPathName() in meshes:
			continue
		
		# Add shape to list
		meshes.append(dagPath.partialPathName())
		
		# Get mesh
		mesh = OpenMaya.MFnMesh(dagPath)
		
		# Get skin cluster
		clusterName = mel.eval("findRelatedSkinCluster " + dagPath.partialPathName()) # I couldn't figure out how to get the skin cluster via the API
		hasSkin = False
		if clusterName != None and clusterName != "" and not clusterName.isspace():
			hasSkin = True
			selList = OpenMaya.MSelectionList()
			selList.add(clusterName)
			clusterNode = OpenMaya.MObject()
			selList.getDependNode(0, clusterNode)
			skin = OpenMayaAnim.MFnSkinCluster(clusterNode)
		
		# Loop through all vertices
		vertIter = OpenMaya.MItMeshVertex(dagPath)
		# - Log Export - 
		LogExport("\nGrabbing mesh information from %s.\n" % dagPath.partialPathName())	
		LogExport("Grabbing verts from %s\n" % dagPath.partialPathName())	
		# - Log Export - 
		vertGetTime = time.time()
		while not vertIter.isDone():
			if not hasSkin:
				verts.append((vertIter.position(OpenMaya.MSpace.kWorld), []))
				vertIter.next()
				continue
			
			# Get weight values
			weightValues = OpenMaya.MDoubleArray()
			numWeights = OpenMaya.MScriptUtil() # Need this because getWeights crashes without being passed a count
			skin.getWeights(dagPath, vertIter.currentItem(), weightValues, numWeights.asUintPtr())
			
			# Get weight names
			weightJoints = OpenMaya.MDagPathArray()
			skin.influenceObjects(weightJoints)
			
			# Make sure the list of weight values and names match
			if weightValues.length() != weightJoints.length():
						# - Log Export - 
				LogExport("Failed to retrieve vertex weight list on '%s.vtx[%d]'; using default joints.\n" % (dagPath.partialPathName(), vertIter.index()), True)	
				PrintWarning("Failed to retrieve vertex weight list on '%s.vtx[%d]'; using default joints." % (dagPath.partialPathName(), vertIter.index()))
			
			# Remove weights of value 0 or weights from unexported joints
			finalWeights = []
			weightsSize = 0
			for i in range(0, weightJoints.length()):
				if weightValues[i] < 0.000001: # 0.000001 is the smallest decimal in xmodel exports
					continue
				jointName = weightJoints[i].partialPathName()
				if not jointName in jointDict:
					LogExport("Unexported joint %s is influencing vertex '%s.vtx[%d]' by %f%%\n" % (("'%s'" % jointName).ljust(15), dagPath.partialPathName(), vertIter.index(), weightValues[i]*100), True)
					PrintWarning("Unexported joint %s is influencing vertex '%s.vtx[%d]' by %f%%\n" % (("'%s'" % jointName).ljust(15), dagPath.partialPathName(), vertIter.index(), weightValues[i]*100))
				else:
					finalWeights.append([jointDict[jointName], weightValues[i]])
					weightsSize += weightValues[i]
			
			# Make sure the total weight adds up to 1
			if weightsSize > 0:
				weightMultiplier = 1 / weightsSize
				for weight in finalWeights:
					weight[1] *= weightMultiplier
			
			verts.append((
				vertIter.position(OpenMaya.MSpace.kWorld), # XYZ position
				finalWeights # List of weights
			))
			
			# Next vert
			ProgressBarStep()
			vertIter.next()
		# - Log Export - 
		LogExport("Grabbed %i verts from %s in %s seconds.\n" % (vertIter.count(), dagPath.partialPathName(), time.time() - vertGetTime))	
		# - Log Export - 
		# Get materials used by this mesh
		meshMaterials = GetMaterialsFromMesh(mesh, dagPath)

		
		
		# Loop through all faces
		polyIter = OpenMaya.MItMeshPolygon(dagPath)
		currentObjectVertexOffset = 0
		# - Log Export - 
		LogExport("Grabbing faces from %s\n" % dagPath.partialPathName())	
		faceGetTime = time.time()
		# - Log Export - 
		while not polyIter.isDone():
			# Get this poly's material
			polyMaterial = meshMaterials[polyIter.index()]
			
			# Every face must have a material
			if polyMaterial == None:
				PrintWarning("Found no material on face '%s.f[%d]'; ignoring face" % (dagPath.partialPathName(), polyIter.index()))
				polyIter.next()
				continue
			
			# Add this poly's material to the global list of used materials
			if not polyMaterial[0] in materialDict:
				materialDict[polyMaterial[0]] = len(materials)
				materials.append(polyMaterial)
			
			# Get vertex indices of this poly, and the vertex indices of this poly's triangles
			trianglePoints = OpenMaya.MPointArray()
			triangleIndices = OpenMaya.MIntArray()
			vertexIndices = OpenMaya.MIntArray()
			polyIter.getTriangles(trianglePoints, triangleIndices)
			polyIter.getVertices(vertexIndices)
			
			# localTriangleIndices is the same as triangleIndices, except each vertex is listed as the face-relative index intead of the object-realtive index
			localTriangleIndices = VerticesObjRelToLocalRel(vertexIndices, triangleIndices)
			if localTriangleIndices == False:
				return "Failed to convert object-relative vertices to face-relative on poly '%s.f[%d]'" % (dagPath.partialPathName(), polyIter.index())
			
			# Note: UVs, normals, and colors, are "per-vertex per face", because even though two faces may share
			# a vertex, they might have different UVs, colors, or normals. So, each face has to contain this info
			# for each of it's vertices instead of each vertex alone
			Us = OpenMaya.MFloatArray()
			Vs = OpenMaya.MFloatArray()
			normals = OpenMaya.MVectorArray()
			polyIter.getUVs(Us, Vs)
			polyIter.getNormals(normals, OpenMaya.MSpace.kWorld)
			
			# Add each triangle in this poly to the global face list
			for i in range(triangleIndices.length()/3): # vertexIndices.length() has 3 values per triangle
				# Put local indices into an array for easy access
				locals = [localTriangleIndices[i*3], localTriangleIndices[i*3+1], localTriangleIndices[i*3+2]]
				
				# Using polyIter.getColors() doesn't always work - sometimes values in the return array would
				# be valid Python objects, but when used they would cause Maya to completely crash. No idea
				# why that happens, but getting the colors individually fixed the problem.
				vert0Color = OpenMaya.MColor()
				vert1Color = OpenMaya.MColor()
				vert2Color = OpenMaya.MColor()
				polyIter.getColor(vert0Color, locals[0])
				polyIter.getColor(vert1Color, locals[1])
				polyIter.getColor(vert2Color, locals[2])
				
				# Make sure it has color
				if CONVERT_BLACK_VERTS_TO_WHITE:
					if vert0Color == OpenMaya.MColor(0,0,0):
						vert0Color = OpenMaya.MColor(1,1,1)
					if vert1Color == OpenMaya.MColor(0,0,0):
						vert1Color = OpenMaya.MColor(1,1,1)
					if vert2Color == OpenMaya.MColor(0,0,0):
						vert2Color = OpenMaya.MColor(1,1,1)
				elif vert0Color == OpenMaya.MColor(0,0,0) or vert1Color == OpenMaya.MColor(0,0,0) or vert2Color == OpenMaya.MColor(0,0,0):
					PrintWarning("A color on face '%s.f[%d]' is 0" % (dagPath.partialPathName(), polyIter.index()))
					
				# Note: Vertices are in 0,2,1 order to make CoD happy
				tris.append((
					len(meshes)-1, # Shape index
					materialDict[polyMaterial[0]], # Matertial index 
					(currentStartingVertIndex + triangleIndices[i*3], currentStartingVertIndex + triangleIndices[i*3+2], currentStartingVertIndex + triangleIndices[i*3+1]), # Vert indices
					((Us[locals[0]], 1-Vs[locals[0]]),		(Us[locals[2]], 1-Vs[locals[2]]),		(Us[locals[1]], 1-Vs[locals[1]])),	  # UVs
					(vert0Color, 							vert2Color,								vert1Color),  		  				  # Colors
					(OpenMaya.MVector(normals[locals[0]]),	OpenMaya.MVector(normals[locals[2]]),	OpenMaya.MVector(normals[locals[1]])) # Normals; Must copy the normals into a new container, because the original is destructed at the end of this poltIter iteration.
				))
			
			# Next poly
			ProgressBarStep()
			polyIter.next()

		# - Log Export - 
		LogExport("Grabbed %i faces from %s in %s seconds.\n" % (polyIter.count(), dagPath.partialPathName(), time.time() - faceGetTime))	
		# - Log Export - 
		
		# Update starting vertex index
		currentStartingVertIndex = len(verts)
		
	# Error messages
	if len(meshes) == 0:
		print "No meshes selected to export."
	if len(verts) == 0:
		print "No vertices found in selected meshes."
	if len(tris) == 0:
		print "No faces found in selected meshes."
	if len(materials) == 0:
		print "No materials found on the selected meshes."
		
	# Done!
	return {"meshes": meshes, "verts": verts, "faces": tris, "materials": materials}

	
	
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------- Export XAnim --------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
def ExportXAnim(filePath):
	# Progress bar
	numSelectedObjects = len(cmds.ls(selection=True))
	if numSelectedObjects == 0:
		return "Error: No objects selected for export"

	# Get data
	joints = GetJointList()
	if len(joints[0]) == 0:
		return "Error: No joints selected for export"
#	if len(joints) > 128:
#		print "Warning: More than 128 joints have been selected. The animation might not work in WaW"
	
	# Get settings
	frameStart = cmds.intField(OBJECT_NAMES['xanim'][0]+"_FrameStartField", query=True, value=True)
	frameEnd = cmds.intField(OBJECT_NAMES['xanim'][0]+"_FrameEndField", query=True, value=True)
	fps = cmds.intField(OBJECT_NAMES['xanim'][0]+"_FPSField", query=True, value=True)
	QMultiplier = math.pow(2,cmds.intField(OBJECT_NAMES['xanim'][0]+"_qualityField", query=True, value=True))
	multiplier = 1/QMultiplier
	fps = fps/multiplier;
	if frameStart < 0 or frameStart > frameEnd:
		return "Error: Invalid frame range (start < 0 or start > end)"
	if fps <= 0:
		return "Error: Invalid FPS (fps < 0)"
	if multiplier <= 0 or multiplier > 1:
		return "Error: Invalid multiplier (multiplier < 0 && multiplier >= 1)"
	# Open file
	f = None
	try:
		# Create export directory if it doesn't exist
		directory = os.path.dirname(filePath)
		if not os.path.exists(directory):
			os.makedirs(directory)
		
		# Create files
		f = open(filePath, 'w')
	except (IOError, OSError) as e:
		typex, value, traceback = sys.exc_info()
		return "Unable to create files:\n\n%s" % value.strerror

	cmds.progressBar(OBJECT_NAMES['progress'][0], edit=True, maxValue=frameEnd + 1)
	
	# Write header
	f.write("// Export filename: '%s'\n" % os.path.normpath(filePath))
	if cmds.file(query=True, exists=True):
		f.write("// Source filename: '%s'\n" % os.path.normpath(os.path.abspath(cmds.file(query=True, sceneName=True))).encode('ascii', 'ignore'))
	else:
		f.write("// Source filename: Unsaved\n")
	f.write("// Export time: %s\n\n" % datetime.datetime.now().strftime("%a %b %d %Y, %H:%M:%S"))
	f.write("ANIMATION\n")
	f.write("VERSION 3\n\n")
	
	# Write parts
	f.write("NUMPARTS %i\n" % len(joints[0]))
	for i, joint in enumerate(joints[0]):
		f.write("PART %i \"%s\"\n" % (i, joint[1]))
	
	fLength = ((frameEnd-frameStart+1) / multiplier)
	# Write animation data
	f.write("\nFRAMERATE %i\n" % fps)
	f.write("NUMFRAMES %i\n" % fLength)
	
	currentFrame = cmds.currentTime(query=True)
	for i in range(int(frameStart/multiplier), int((frameEnd+1)/multiplier)):
		f.write("\nFRAME %i" % i)
		if cmds.checkBox("CoDMAYA_ReverseAnim", query=True, value=True):
			cmds.currentTime(((frameEnd+1)-i)*multiplier)
		else:
			cmds.currentTime(i*multiplier)
		
		for j, joint in enumerate(joints[0]):
			f.write("\nPART %i\n" % j)
			WriteJointData(f, joint[2])

		ProgressBarStep()
	
	cmds.currentTime(currentFrame)
	
	# Write notetrack
	slotIndex = cmds.optionMenu(OBJECT_NAMES['xanim'][0]+"_SlotDropDown", query=True, select=True)
	noteList = cmds.getAttr(OBJECT_NAMES['xanim'][2]+(".notetracks[%i]" % slotIndex)) or ""
	notes = noteList.split(",")
	cleanNotes = []
	
	for note in notes:
		parts = note.split(":")
		if note.strip() == "" or len(parts) < 2:
			continue
			
		name = "".join([c for c in parts[0] if c.isalnum() or c=="_"])
		if name == "":
			continue
			
		frame=0
		try: 
			frame = int(parts[1])
		except ValueError:
			continue
			
		cleanNotes.append((name, frame))
		
	f.write("\nNOTETRACKS\n")
	for i, joint in enumerate(joints[0]):
		if i == 0 and len(cleanNotes) > 0:
			f.write("\nPART 0\nNUMTRACKS 1\nNOTETRACK 0\n")
			f.write("NUMKEYS %i\n" % len(cleanNotes))
			for note in cleanNotes:
				f.write("FRAME %i \"%s\"\n" % (note[1], note[0]))
		else:
			f.write("\nPART %i\nNUMTRACKS 0\n" % i)
	
	f.close()

	ProgressBarStep()

	cmds.refresh()

	if QueryToggableOption('E2B'):
		try:
			RunExport2Bin(filePath)
		except:
			MessageBox("The animation exported successfully however Export2Bin failed to run, the animation will need to be converted manually.\n\nPlease check your paths.")
	
def WriteDummyTargetModelBoneRoot(f, numframes):
	f.write("""
		"targetModelBoneRoots" : [
		{
			"name" : "TAG_ORIGIN",
			"animation" : [
		""")
	for i in range(0,numframes):
		if i+1 == numframes:
			f.write("""
				{
					"frame" : %d,
					"offset" : [ 0.0000, 0.0000, 0.0000 ],
					"axis" : {
						"x" : [  0.0000, -1.0000,  0.0000 ],
						"y" : [  1.0000,  0.0000,  0.0000 ],
						"z" : [  0.0000,  0.0000,  1.0000 ]
					}
				}
		""" % i)
		else:
			f.write("""
				{
					"frame" : %d,
					"offset" : [ 0.0000, 0.0000, 0.0000 ],
					"axis" : {
						"x" : [  0.0000, -1.0000,  0.0000 ],
						"y" : [  1.0000,  0.0000,  0.0000 ],
						"z" : [  0.0000,  0.0000,  1.0000 ]
					}
				},
		""" % i)
	f.write("""]
		},
		{
			"name" : "tag_align",
			"animation" : [
		""")
	'''
	for i in range(0,numframes):
		if i+1 == numframes:
			f.write("""
				{
					"frame" : %d,
					"offset" : [ 0.0154, -0.0251, 0.0000 ],
					"axis" : {
						"x" : [  0.0000, -1.0000,  0.0000 ],
						"y" : [  1.0000,  0.0000,  0.0000 ],
						"z" : [  0.0000,  0.0000,  1.0000 ]
					}
				}
		""" % i)
		else:
			f.write("""
				{
					"frame" : %d,
					"offset" : [ 0.0154, -0.0251, 0.0000 ],
					"axis" : {
						"x" : [  0.0000, -1.0000,  0.0000 ],
						"y" : [  1.0000,  0.0000,  0.0000 ],
						"z" : [  0.0000,  0.0000,  1.0000 ]
					}
				},
		""" % i)
			'''
	f.write("""]
		}
	],
		""")

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------- Export XCam --------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
def ExportXCam(filePath):
	# Progress bar
	numSelectedObjects = len(cmds.ls(selection=True))
	if numSelectedObjects == 0:
		return "Error: No objects selected for export"
	
	cmds.progressBar(OBJECT_NAMES['progress'][0], edit=True, maxValue=numSelectedObjects+1)
	
	# Get data
	cameras = GetCameraList()
	if len(cameras) == 0:
		return "Error: No cameras selected for export"
	# Get settings
	frameStart = cmds.intField(OBJECT_NAMES['xcam'][0]+"_FrameStartField", query=True, value=True)
	frameEnd = cmds.intField(OBJECT_NAMES['xcam'][0]+"_FrameEndField", query=True, value=True)
	fps = cmds.intField(OBJECT_NAMES['xcam'][0]+"_FPSField", query=True, value=True)
	QMultiplier = math.pow(2,cmds.intField(OBJECT_NAMES['xcam'][0]+"_qualityField", query=True, value=True))
	#multiplier = 1/QMultiplier
	multiplier = 1
	fps = fps/multiplier;
	if frameStart < 0 or frameStart > frameEnd:
		return "Error: Invalid frame range (start < 0 or start > end)"
	if fps <= 0:
		return "Error: Invalid FPS (fps < 0)"
	if multiplier <= 0 or multiplier > 1:
		return "Error: Invalid multiplier (multiplier < 0 && multiplier >= 1)"
	# Open file
	f = None
	try:
		# Create export directory if it doesn't exist
		directory = os.path.dirname(filePath)
		if not os.path.exists(directory):
			os.makedirs(directory)
		
		# Create files
		f = open(filePath, 'w')
	except (IOError, OSError) as e:
		typex, value, traceback = sys.exc_info()
		return "Unable to create files:\n\n%s" % value.strerror
	fLength = ((frameEnd-frameStart+1) / multiplier)
	# Write header
	f.write("{\n")
	f.write("\"version\" : 1,\n")
	if cmds.file(query=True, exists=True):
		f.write("	\"scene\": \"%s\",\n" % os.path.normpath(os.path.abspath(cmds.file(query=True, sceneName=True))).encode('ascii', 'ignore').replace('\\','/'))
	f.write("""	"align" : {
		"tag" : "tag_align",
		"offset" : [ 0.0154, -0.0251, 0.0000 ],
		"axis" : {
			"x" : [ -0.0000, -1.0000, -0.0000 ],
			"y" : [  1.0000, -0.0000, -0.0000 ],
			"z" : [  0.0000, -0.0000,  1.0000 ]
		}
	},
	"framerate" : %d,
	"numframes" : %d,
	""" % (fps, fLength))
	
	WriteDummyTargetModelBoneRoot(f,fLength)

	# Write parts
	f.write("""
		"cameras" : [
		""")
	currentFrame = cmds.currentTime(query=True)
	for i, camera in enumerate(cameras):
		name = camera[1].partialPathName().split("|")
		name = name[len(name)-1].split(":") # Remove namespace prefixes
		name = name[len(name)-1]
		f.write("""{
			"name" : "%s",
			"index" : %d,
			"type" : "Perspective",
			"aperture" : "FOCAL_LENGTH", """ % (name,i)) # why did I make the cam index a string and not an int? linker bitches about that
		WriteCameraData(f, camera[1])
		f.write(",\n")
		WriteNodeFloat(f, "aspectratio", 16.0/9.0)
		WriteNodeFloat(f, "nearz", 4)   # game default
		WriteNodeFloat(f, "farz", 4000) # game doesnt have a default value for it, trial and error, here we come		
		f.write(""""animation" : [
			""")
		for j in range(int(frameStart), int((frameEnd+1))):
			cmds.currentTime(j)
			f.write("""{
				"frame" : %d,
				""" % j)
			WriteCameraData(f, camera[1])
			if j == frameEnd:
				f.write("}\n")
			else:
				f.write("},\n")
		f.write("""]
				}
			""")
	f.write("""],
		"cameraSwitch" : [
		],
			""")
	cmds.currentTime(currentFrame)
	
	# Write notetrack
	slotIndex = cmds.optionMenu(OBJECT_NAMES['xcam'][0]+"_SlotDropDown", query=True, select=True)
	noteList = cmds.getAttr(OBJECT_NAMES['xcam'][2]+(".notetracks[%i]" % slotIndex)) or ""
	notes = noteList.split(",")
	cleanNotes = []
	
	for note in notes:
		parts = note.split(":")
		if note.strip() == "" or len(parts) < 2:
			continue
			
		name = "".join([c for c in parts[0] if c.isalnum() or c=="_"])
		if name == "":
			continue
			
		frame=0
		try: 
			frame = int(parts[1])
		except ValueError:
			continue
			
		cleanNotes.append((name, frame))
		
	f.write("\n\"notetracks\" : [\n")
	for note in cleanNotes:
		f.write("{\n \"name\" : \"%s\",\n \"frame\" : %d\n},\n" % (note[0], note[1]))
	f.write("]\n}")
	
	f.close()
	ProgressBarStep()
	cmds.refresh()

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------ Viewmodel Tools -------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
def DoesObjectExist(name, type):
	if not cmds.objExists(name):
		MessageBox("Error: Missing %s '%s'" % (type, name))
		return False
		
	return True

def CreateNewGunsleeveMayaFile(required_parameter):
	global WarningsDuringExport
	
	# Save reminder
	if not SaveReminder(False):
		return
	
	# Get paths
	filePath = cmds.file(query=True, sceneName=True)
	split1 = os.path.split(filePath)
	split2 = os.path.splitext(split1[1])
	exportPath = os.path.join(split1[0], "gunsleeves_" + split2[0] + ".xmodel_export")
	
	# Create a new file and import models
	cmds.file(force=True, newFile=True)
	cmds.file(os.path.join(GetRootFolder(), "bin/maya/rigs/viewmodel/ViewModel_DefMesh.mb"), i=True, type="mayaBinary")
	cmds.file(filePath, i=True, type="mayaBinary")
	
	# Check to make sure objects exist
	if not DoesObjectExist("J_Gun", "joint"): return
	if not DoesObjectExist("tag_weapon", "tag"): return
	if not DoesObjectExist("GunExport", "object set"): return
	if not DoesObjectExist("DefViewSkeleton", "object set"): return
	if not DoesObjectExist("tag_view", "tag"): return
	if not cmds.objExists("viewmodelSleeves_OpForce") and not cmds.objExists("viewmodelSleeves_Marines"):
		MessageBox("Error: Missing viewsleeves 'viewmodelSleeves_OpForce' or 'viewmodelSleeves_Marines'")
		return
		
	# Attach gun to rig
	cmds.select("J_Gun", replace=True)
	cmds.select("tag_weapon", add=True)
	cmds.parent()
	
	# Select things to export
	cmds.select("GunExport", replace=True)
	cmds.select("DefViewSkeleton", toggle=True)
	cmds.select("tag_view", toggle=True)
	if cmds.objExists("viewmodelSleeves_OpForce"):
		cmds.select("viewmodelSleeves_OpForce", toggle=True, hierarchy=True)
	else:
		cmds.select("viewmodelSleeves_Marines", toggle=True, hierarchy=True)
	
	# Export
	if cmds.control("w"+OBJECT_NAMES['progress'][0], exists=True):
		cmds.deleteUI("w"+OBJECT_NAMES['progress'][0])
	progressWindow = cmds.window("w"+OBJECT_NAMES['progress'][0], title=OBJECT_NAMES['progress'][1], width=302, height=22, sizable=False)
	cmds.columnLayout()
	progressControl = cmds.progressBar(OBJECT_NAMES['progress'][0], width=300)
	cmds.showWindow(progressWindow)
	cmds.refresh() # Force the progress bar to be drawn
	
	# Export
	WarningsDuringExport = 0
	response = None
	try:
		response = ExportXModel(exportPath)
	except Exception as e:
		response = "An unhandled error occurred during export:\n\n" + traceback.format_exc()
	
	# Delete progress bar
	cmds.deleteUI(progressWindow, window=True)
	
	# Handle response
	if type(response) == str or type(response) == unicode:
		MessageBox(response)
	elif WarningsDuringExport > 0:
		MessageBox("Warnings occurred during export. Check the script editor output for more details.")
	
	if type(response) != str and type(response) != unicode:
		MessageBox("Export saved to\n\n" + os.path.normpath(exportPath))
	
def CreateNewViewmodelRigFile(required_parameter):
	# Save reminder
	if not SaveReminder(False):
		return
	
	# Get path
	filePath = cmds.file(query=True, sceneName=True)
	
	# Create a new file and import models
	cmds.file(force=True, newFile=True)
	cmds.file(os.path.join(GetRootFolder(), "bin/maya/rigs/viewmodel/ViewModel_Rig.mb"), reference=True, type="mayaBinary", namespace="rig", options="v=0")
	cmds.file(filePath, reference=True, type="mayaBinary", namespace="VM_Gun")
	
	# Check to make sure objects exist
	if not DoesObjectExist("VM_Gun:J_Gun", "joint"): return
	if not cmds.objExists("rig:DefMesh:tag_weapon") and not cmds.objExists("ConRig:DefMesh:tag_weapon"):
		MessageBox("Error: Missing viewsleeves 'rig:DefMesh:tag_weapon' or 'ConRig:DefMesh:tag_weapon'")
		return
	
	# Connect gun to rig
	if cmds.objExists("rig:DefMesh:tag_weapon"):
		cmds.select("rig:DefMesh:tag_weapon", replace=True)
	else:
		cmds.select("ConRig:DefMesh:tag_weapon", replace=True)
		
	cmds.select("VM_Gun:J_Gun", toggle=True)
	cmds.parentConstraint(weight=1, name="VMParentConstraint")
	cmds.select(clear=True)
	
def SwitchGunInCurrentRigFile(required_parameter):
	# Save reminder
	if not SaveReminder():
		return
	
	# Make sure the rig is correct
	if not cmds.objExists("rig:DefMesh:tag_weapon") and not cmds.objExists("ConRig:DefMesh:tag_weapon"):
		MessageBox("Error: Missing rig:DefMesh:tag_weapon' or 'ConRig:DefMesh:tag_weapon'")
		return
	
	if not DoesObjectExist("VM_Gun:J_Gun", "joint"): return
	
	# Prompt user to select a new gun file
	gunPath = cmds.fileDialog2(fileMode=1, fileFilter="Maya Files (*.ma *.mb)", caption="Select a New Gun File", startingDirectory=GetRootFolder())
	if gunPath == None or len(gunPath) == 0 or gunPath[0].strip() == "":
		return
	gunPath = gunPath[0].strip()
	
	# Delete the constraint
	cmds.delete("VMParentConstraint")
	
	# Delete any hand attachments
	if cmds.objExists("rig:Hand_Extra_RI_GRP.Parent"):
		parentRI = cmds.getAttr("rig:Hand_Extra_RI_GRP.Parent")
		if parentRI != "":
			cmds.delete(parentRI)
	if cmds.objExists("rig:Hand_Extra_LE_GRP.Parent"):
		parentLE = cmds.getAttr("rig:Hand_Extra_LE_GRP.Parent")
		if parentLE != "":
			cmds.delete(parentLE)
		
	# Switch guns
	cmds.file(gunPath, loadReference="VM_GunRN");
	
	# Connect gun to rig
	if cmds.objExists("rig:DefMesh:tag_weapon"):
		cmds.select("rig:DefMesh:tag_weapon", replace=True)
	else:
		cmds.select("ConRig:DefMesh:tag_weapon", replace=True)
		
	cmds.select("VM_Gun:J_Gun", toggle=True)
	cmds.parentConstraint(weight=1, name="VMParentConstraint")
	cmds.select(clear=True)
	
	
	
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------- XModel Export Window ----------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------		
def CreateXModelWindow():
	# Create window
	if cmds.control(OBJECT_NAMES['xmodel'][0], exists=True):
		cmds.deleteUI(OBJECT_NAMES['xmodel'][0])
	
	cmds.window(OBJECT_NAMES['xmodel'][0], title=OBJECT_NAMES['xmodel'][1], width=340, height=1, retain=True, maximizeButton=False)
	form = cmds.formLayout(OBJECT_NAMES['xmodel'][0]+"_Form")
	
	# Controls
	slotDropDown = cmds.optionMenu(OBJECT_NAMES['xmodel'][0]+"_SlotDropDown", changeCommand="CoDMayaTools.RefreshXModelWindow()", annotation="Each slot contains different a export path, settings, and saved selection")
	for i in range(1, EXPORT_WINDOW_NUMSLOTS+1):
		cmds.menuItem(OBJECT_NAMES['xmodel'][0]+"_SlotDropDown"+("_s%i" % i), label="Slot %i" % i)
	
	separator1 = cmds.separator(style='in', height=16)
	separator2 = cmds.separator(style='in')
	
	saveToLabel = cmds.text(label="Save to:", annotation="This is where the .xmodel_export is saved to")
	saveToField = cmds.textField(OBJECT_NAMES['xmodel'][0]+"_SaveToField", height=21, changeCommand="CoDMayaTools.GeneralWindow_SaveToField('xmodel')", annotation="This is where the .xmodel_export is saved to")
	fileBrowserButton = cmds.button(label="...", height=21, command="CoDMayaTools.GeneralWindow_FileBrowser('xmodel', \"XModel Intermediate File (*.xmodel_export)\")", annotation="Open a file browser dialog")
	
	exportSelectedButton = cmds.button(label="Export Selected", command="CoDMayaTools.GeneralWindow_ExportSelected('xmodel', False)", annotation="Export all currently selected objects from the scene (current frame)\nWarning: Will automatically overwrite if the export path if it already exists")
	saveSelectionButton = cmds.button(label="Save Selection", command="CoDMayaTools.GeneralWindow_SaveSelection('xmodel')", annotation="Save the current object selection")
	getSavedSelectionButton = cmds.button(label="Get Saved Selection", command="CoDMayaTools.GeneralWindow_GetSavedSelection('xmodel')", annotation="Reselect the saved selection")
	
	exportMultipleSlotsButton = cmds.button(label="Export Multiple Slots", command="CoDMayaTools.GeneralWindow_ExportMultiple('xmodel')", annotation="Automatically export multiple slots at once, using each slot's saved selection")
	exportInMultiExportCheckbox = cmds.checkBox(OBJECT_NAMES['xmodel'][0]+"_UseInMultiExportCheckBox", label="Use current slot for Export Multiple", changeCommand="CoDMayaTools.GeneralWindow_ExportInMultiExport('xmodel')", annotation="Check this make the 'Export Multiple Slots' button export this slot")
	setCosmeticParentbone = cmds.button(OBJECT_NAMES['xmodel'][0]+"_MarkCosmeticParent", label="Set selected as Cosmetic Parent", command="CoDMayaTools.SetCosmeticParent('xmodel')", annotation="Set this bone as our cosmetic parent. All bones under this will be cosmetic.")
	RemoveCosmeticParent = cmds.button(OBJECT_NAMES['xmodel'][0]+"_ClearCosmeticParent", label="Clear Cosmetic Parent", command="CoDMayaTools.ClearCosmeticParent('xmodel')", annotation="Remove the cosmetic parent.")

	# Setup form
	cmds.formLayout(form, edit=True,
		attachForm=[(slotDropDown, 'top', 6), (slotDropDown, 'left', 10), (slotDropDown, 'right', 10),
					(separator1, 'left', 0), (separator1, 'right', 0),
					(separator2, 'left', 0), (separator2, 'right', 0),
					(saveToLabel, 'left', 12),
					(fileBrowserButton, 'right', 10),
					(exportMultipleSlotsButton, 'bottom', 6), (exportMultipleSlotsButton, 'left', 10),
					(exportInMultiExportCheckbox, 'bottom', 9), (exportInMultiExportCheckbox, 'right', 6),
					(exportSelectedButton, 'left', 10),
					(saveSelectionButton, 'right', 10),
					(setCosmeticParentbone, 'left', 10),
					(RemoveCosmeticParent, 'left', 10)],
					#(exportSelectedButton, 'bottom', 6), (exportSelectedButton, 'left', 10),
					#(saveSelectionButton, 'bottom', 6), (saveSelectionButton, 'right', 10),
					#(getSavedSelectionButton, 'bottom', 6)],
		
		attachControl=[	(separator1, 'top', 0, slotDropDown),
						(saveToLabel, 'bottom', 9, exportSelectedButton),
						(saveToField, 'bottom', 5, exportSelectedButton), (saveToField, 'left', 5, saveToLabel), (saveToField, 'right', 5, fileBrowserButton),
						(fileBrowserButton, 'bottom', 5, exportSelectedButton),
						(exportSelectedButton, 'bottom', 5, separator2),
						(saveSelectionButton, 'bottom', 5, separator2),
						(setCosmeticParentbone, 'bottom', 5, separator2),
						(RemoveCosmeticParent, 'bottom', 5, separator2),
						(saveSelectionButton, 'bottom', 5, setCosmeticParentbone),
						(exportSelectedButton, 'bottom', 5, setCosmeticParentbone),
						(setCosmeticParentbone, 'bottom', 5, RemoveCosmeticParent),
						(getSavedSelectionButton, 'bottom', 5, separator2), (getSavedSelectionButton, 'right', 10, saveSelectionButton),
						(getSavedSelectionButton, 'bottom', 5, setCosmeticParentbone),
						(separator2, 'bottom', 5, exportMultipleSlotsButton)])

def RefreshXModelWindow():
	# Refresh/create node
	if len(cmds.ls(OBJECT_NAMES['xmodel'][2])) == 0:
		cmds.createNode("renderLayer", name=OBJECT_NAMES['xmodel'][2], skipSelect=True)
	
	cmds.lockNode(OBJECT_NAMES['xmodel'][2], lock=False)
	
	if not cmds.attributeQuery("slot", node=OBJECT_NAMES['xmodel'][2], exists=True):
		cmds.addAttr(OBJECT_NAMES['xmodel'][2], longName="slot", attributeType='short', defaultValue=1)
	if not cmds.attributeQuery("paths", node=OBJECT_NAMES['xmodel'][2], exists=True):
		cmds.addAttr(OBJECT_NAMES['xmodel'][2], longName="paths", multi=True, dataType='string')
		cmds.setAttr(OBJECT_NAMES['xmodel'][2]+".paths", size=EXPORT_WINDOW_NUMSLOTS)
	if not cmds.attributeQuery("selections", node=OBJECT_NAMES['xmodel'][2], exists=True):
		cmds.addAttr(OBJECT_NAMES['xmodel'][2], longName="selections", multi=True, dataType='stringArray')
		cmds.setAttr(OBJECT_NAMES['xmodel'][2]+".selections", size=EXPORT_WINDOW_NUMSLOTS)
	if not cmds.attributeQuery("useinmultiexport", node=OBJECT_NAMES['xmodel'][2], exists=True):
		cmds.addAttr(OBJECT_NAMES['xmodel'][2], longName="useinmultiexport", multi=True, attributeType='bool', defaultValue=False)
		cmds.setAttr(OBJECT_NAMES['xmodel'][2]+".useinmultiexport", size=EXPORT_WINDOW_NUMSLOTS)
	if not cmds.attributeQuery("Cosmeticbone", node=OBJECT_NAMES['xmodel'][2], exists=True):
		cmds.addAttr(OBJECT_NAMES['xmodel'][2], longName="Cosmeticbone", dataType="string")	

	cmds.lockNode(OBJECT_NAMES['xmodel'][2], lock=True)
	
	# Set values
	slotIndex = cmds.optionMenu(OBJECT_NAMES['xmodel'][0]+"_SlotDropDown", query=True, select=True)
	path = cmds.getAttr(OBJECT_NAMES['xmodel'][2]+(".paths[%i]" % slotIndex))
	cmds.setAttr(OBJECT_NAMES['xmodel'][2]+".slot", slotIndex)
	cmds.textField(OBJECT_NAMES['xmodel'][0]+"_SaveToField", edit=True, fileName=path)

	useInMultiExport = cmds.getAttr(OBJECT_NAMES['xmodel'][2]+(".useinmultiexport[%i]" % slotIndex))
	cmds.checkBox(OBJECT_NAMES['xmodel'][0]+"_UseInMultiExportCheckBox", edit=True, value=useInMultiExport)
	

def SetCosmeticParent(reqarg):
	selection = cmds.ls(selection = True, type = "joint")  

	if(len(selection) > 1):
		MessageBox("Only 1 Cosmetic Parent is allowed.")
		return
	elif(len(selection) == 0):
		MessageBox("No joint selected.")
		return		

	cmds.setAttr(OBJECT_NAMES['xmodel'][2] + ".Cosmeticbone", selection[0], type="string")

	MessageBox("\"%s\" has now been set as the cosmetic parent." % str(selection[0]))

def ClearCosmeticParent(reqarg):
	cosmetic_bone = cmds.getAttr(OBJECT_NAMES["xmodel"][2]+ ".Cosmeticbone")

	if cosmetic_bone is None:
		cmds.error("No cosmetic bone set.")

	cosmetic_bone = cosmetic_bone.split("|")[-1].split(":")[-1]
	
	if cosmetic_bone != "" or cosmetic_bone is not None:
		cmds.setAttr(OBJECT_NAMES['xmodel'][2] + ".Cosmeticbone", "", type="string")
		MessageBox("Cosmetic Parent \"%s\" has now been removed." % cosmetic_bone)
	
	
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------- XAnim Export Window ----------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------	
def CreateXAnimWindow():
	# Create window
	if cmds.control(OBJECT_NAMES['xanim'][0], exists=True):
		cmds.deleteUI(OBJECT_NAMES['xanim'][0])
	
	cmds.window(OBJECT_NAMES['xanim'][0], title=OBJECT_NAMES['xanim'][1], width=1, height=1, retain=True, maximizeButton=False)
	form = cmds.formLayout(OBJECT_NAMES['xanim'][0]+"_Form")
	
	# Controls
	slotDropDown = cmds.optionMenu(OBJECT_NAMES['xanim'][0]+"_SlotDropDown", changeCommand="CoDMayaTools.RefreshXAnimWindow()", annotation="Each slot contains different a export path, frame range, notetrack, and saved selection")
	for i in range(1, EXPORT_WINDOW_NUMSLOTS+1):
		cmds.menuItem(OBJECT_NAMES['xmodel'][0]+"_SlotDropDown"+("_s%i" % i), label="Slot %i" % i)
	
	separator1 = cmds.separator(style='in')
	separator2 = cmds.separator(style='in')
	separator3 = cmds.separator(style='in')
	
	framesLabel = cmds.text(label="Frames:", annotation="Range of frames to export")
	framesStartField = cmds.intField(OBJECT_NAMES['xanim'][0]+"_FrameStartField", height=21, width=35, minValue=0, changeCommand="CoDMayaTools.UpdateFrameRange('xanim')", annotation="Starting frame to export (inclusive)")
	framesToLabel = cmds.text(label="to")
	framesEndField = cmds.intField(OBJECT_NAMES['xanim'][0]+"_FrameEndField", height=21, width=35, minValue=0, changeCommand="CoDMayaTools.UpdateFrameRange('xanim')", annotation="Ending frame to export (inclusive)")
	GrabFrames = cmds.button(label="Grab Frames", width=75, command="CoDMayaTools.SetFrames('xanim')", annotation="Get frame end and start from scene.")
	fpsLabel = cmds.text(label="FPS:")
	fpsField = cmds.intField(OBJECT_NAMES['xanim'][0]+"_FPSField", height=21, width=35, value=1, minValue=1, changeCommand="CoDMayaTools.UpdateFramerate('xanim')", annotation="Animation FPS")
	qualityLabel = cmds.text(label="Quality (0-10)", annotation="Quality of the animation, higher values result in less jitter but produce larger files. Default is 0")
	qualityField = cmds.intField(OBJECT_NAMES['xanim'][0]+"_qualityField", height=21, width=35, value=0, minValue=0, maxValue=10, step=1, changeCommand="CoDMayaTools.UpdateMultiplier('xanim')", annotation="Quality of the animation, higher values result in less jitter but produce larger files.")
	
	notetracksLabel = cmds.text(label="Notetrack:", annotation="Notetrack info for the animation")
	noteList = cmds.textScrollList(OBJECT_NAMES['xanim'][0]+"_NoteList", allowMultiSelection=False, selectCommand="CoDMayaTools.SelectNote('xanim')", annotation="List of notes in the notetrack")
	addNoteButton = cmds.button(label="Add Note", width=75, command="CoDMayaTools.AddNote('xanim')", annotation="Add a note to the notetrack")
	ReadNotesButton = cmds.button(label="Grab Notes", width=75, command="CoDMayaTools.ReadNotetracks('xanim')", annotation="Grab Notes from Notetrack in Outliner")
	ClearNotes = cmds.button(label="Clear Notes", width=75, command="CoDMayaTools.ClearNotes('xanim')", annotation="Clear ALL notetracks.")
	RenameNoteTrack = cmds.button(label="Rename Note", command="CoDMayaTools.RenameNotes('xanim')", annotation="Rename the currently selected note.")
	removeNoteButton = cmds.button(label="Remove Note", command="CoDMayaTools.RemoveNote('xanim')", annotation="Remove the currently selected note from the notetrack")
	noteFrameLabel = cmds.text(label="Frame:", annotation="The frame the currently selected note is applied to")
	noteFrameField = cmds.intField(OBJECT_NAMES['xanim'][0]+"_NoteFrameField", changeCommand="CoDMayaTools.UpdateNoteFrame('xanim')", height=21, width=30, minValue=0, annotation="The frame the currently selected note is applied to")
	
	saveToLabel = cmds.text(label="Save to:", annotation="This is where .xanim_export is saved to")
	saveToField = cmds.textField(OBJECT_NAMES['xanim'][0]+"_SaveToField", height=21, changeCommand="CoDMayaTools.GeneralWindow_SaveToField('xanim')", annotation="This is where .xanim_export is saved to")
	fileBrowserButton = cmds.button(label="...", height=21, command="CoDMayaTools.GeneralWindow_FileBrowser('xanim', \"XAnim Intermediate File (*.xanim_export)\")", annotation="Open a file browser dialog")
	
	exportSelectedButton = cmds.button(label="Export Selected", command="CoDMayaTools.GeneralWindow_ExportSelected('xanim', False)", annotation="Export all currently selected joints from the scene (specified frames)\nWarning: Will automatically overwrite if the export path if it already exists")
	saveSelectionButton = cmds.button(label="Save Selection", command="CoDMayaTools.GeneralWindow_SaveSelection('xanim')", annotation="Save the current object selection")
	getSavedSelectionButton = cmds.button(label="Get Saved Selection", command="CoDMayaTools.GeneralWindow_GetSavedSelection('xanim')", annotation="Reselect the saved selection")
	
	exportMultipleSlotsButton = cmds.button(label="Export Multiple Slots", command="CoDMayaTools.GeneralWindow_ExportMultiple('xanim')", annotation="Automatically export multiple slots at once, using each slot's saved selection")
	exportInMultiExportCheckbox = cmds.checkBox(OBJECT_NAMES['xanim'][0]+"_UseInMultiExportCheckBox", label="Use current slot for Export Multiple", changeCommand="CoDMayaTools.GeneralWindow_ExportInMultiExport('xanim')", annotation="Check this make the 'Export Multiple Slots' button export this slot")
	ReverseAnimation = cmds.checkBox("CoDMAYA_ReverseAnim", label="Export Animation Reversed", annotation="Check this if you want to export the anim. backwards. Usefule for reversing to make opposite sprints, etc.", value=False)
	# Setup form
	cmds.formLayout(form, edit=True,
		attachForm=[(slotDropDown, 'top', 6), (slotDropDown, 'left', 10), (slotDropDown, 'right', 10),
					(separator1, 'left', 0), (separator1, 'right', 0),
					(framesLabel, 'left', 10),
					(fpsLabel, 'left', 10),
					(qualityLabel, 'left', 10),
					(notetracksLabel, 'left', 10),
					(noteList, 'left', 10),
					(ReverseAnimation, 'left', 10),
					(addNoteButton, 'right', 10),
					(ReadNotesButton, 'right', 10),
					(RenameNoteTrack, 'right', 10),
					(ClearNotes, 'right', 10),
					(removeNoteButton, 'right', 10),
					(noteFrameField, 'right', 10),
					(separator2, 'left', 0), (separator2, 'right', 0),
					(saveToLabel, 'left', 12),
					(fileBrowserButton, 'right', 10),
					(exportMultipleSlotsButton, 'bottom', 6), (exportMultipleSlotsButton, 'left', 10),
					(exportInMultiExportCheckbox, 'bottom', 9), (exportInMultiExportCheckbox, 'right', 6),
					(exportSelectedButton, 'left', 10),
					(saveSelectionButton, 'right', 10),
					(separator3, 'left', 0), (separator3, 'right', 0)],
		
		attachControl=[	(separator1, 'top', 6, slotDropDown),
						(framesLabel, 'top', 8, separator1),
						(framesStartField, 'top', 5, separator1), (framesStartField, 'left', 4, framesLabel),
						(framesToLabel, 'top', 8, separator1), (framesToLabel, 'left', 4+35+4, framesLabel),
						(framesEndField, 'top', 5, separator1), (framesEndField, 'left', 4, framesToLabel),
						(GrabFrames, 'top', 5, separator1), (GrabFrames, 'left', 4, framesEndField),
						(fpsLabel, 'top', 8, framesStartField),
						(fpsField, 'top', 5, framesStartField), (fpsField, 'left', 21, fpsLabel),
						(qualityLabel, 'top', 8, fpsField),
						(qualityField, 'top', 5, fpsField), (qualityField, 'left', 21, qualityLabel),
						(notetracksLabel, 'top', 5, qualityLabel),
						(noteList, 'top', 5, notetracksLabel), (noteList, 'right', 10, removeNoteButton), (noteList, 'bottom', 60, separator2),
						(ReverseAnimation, 'top', 10, noteList), (ReverseAnimation, 'right', 10, removeNoteButton),
						(addNoteButton, 'top', 5, notetracksLabel),
						(ReadNotesButton, 'top', 5, addNoteButton),
						(RenameNoteTrack, 'top', 5, ReadNotesButton),
						(ClearNotes, 'top', 5, RenameNoteTrack),
						(removeNoteButton, 'top', 5, ClearNotes),
						(noteFrameField, 'top', 5, removeNoteButton),
						(noteFrameLabel, 'top', 8, removeNoteButton), (noteFrameLabel, 'right', 4, noteFrameField),
						(separator2, 'bottom', 5, fileBrowserButton),
						(saveToLabel, 'bottom', 10, exportSelectedButton),
						(saveToField, 'bottom', 5, exportSelectedButton), (saveToField, 'left', 5, saveToLabel), (saveToField, 'right', 5, fileBrowserButton),
						(fileBrowserButton, 'bottom', 5, exportSelectedButton),
						(exportSelectedButton, 'bottom', 5, separator3),
						(saveSelectionButton, 'bottom', 5, separator3),
						(getSavedSelectionButton, 'bottom', 5, separator3), (getSavedSelectionButton, 'right', 10, saveSelectionButton),
						(separator3, 'bottom', 5, exportMultipleSlotsButton)
						])
		
def RefreshXAnimWindow():
	# Refresh/create node
	if len(cmds.ls(OBJECT_NAMES['xanim'][2])) == 0:
		cmds.createNode("renderLayer", name=OBJECT_NAMES['xanim'][2], skipSelect=True)
	
	cmds.lockNode(OBJECT_NAMES['xanim'][2], lock=False)
	
	if not cmds.attributeQuery("slot", node=OBJECT_NAMES['xanim'][2], exists=True):
		cmds.addAttr(OBJECT_NAMES['xanim'][2], longName="slot", attributeType='short', defaultValue=1)
	if not cmds.attributeQuery("paths", node=OBJECT_NAMES['xanim'][2], exists=True):
		cmds.addAttr(OBJECT_NAMES['xanim'][2], longName="paths", multi=True, dataType='string')
		cmds.setAttr(OBJECT_NAMES['xanim'][2]+".paths", size=EXPORT_WINDOW_NUMSLOTS)
	if not cmds.attributeQuery("selections", node=OBJECT_NAMES['xanim'][2], exists=True):
		cmds.addAttr(OBJECT_NAMES['xanim'][2], longName="selections", multi=True, dataType='stringArray')
		cmds.setAttr(OBJECT_NAMES['xanim'][2]+".selections", size=EXPORT_WINDOW_NUMSLOTS)
	if not cmds.attributeQuery("frameRanges", node=OBJECT_NAMES['xanim'][2], exists=True):
		cmds.addAttr(OBJECT_NAMES['xanim'][2], longName="frameRanges", multi=True, dataType='long2')
		cmds.setAttr(OBJECT_NAMES['xanim'][2]+".frameRanges", size=EXPORT_WINDOW_NUMSLOTS)
	if not cmds.attributeQuery("framerate", node=OBJECT_NAMES['xanim'][2], exists=True):
		cmds.addAttr(OBJECT_NAMES['xanim'][2], longName="framerate", multi=True, attributeType='long', defaultValue=30)
		cmds.setAttr(OBJECT_NAMES['xanim'][2]+".framerate", size=EXPORT_WINDOW_NUMSLOTS)
	if not cmds.attributeQuery("multiplier", node=OBJECT_NAMES['xanim'][2], exists=True):
		cmds.addAttr(OBJECT_NAMES['xanim'][2], longName="multiplier", multi=True, attributeType='long', defaultValue=30)
		cmds.setAttr(OBJECT_NAMES['xanim'][2]+".multiplier", size=EXPORT_WINDOW_NUMSLOTS)
	if not cmds.attributeQuery("notetracks", node=OBJECT_NAMES['xanim'][2], exists=True):
		cmds.addAttr(OBJECT_NAMES['xanim'][2], longName="notetracks", multi=True, dataType='string') # Formatted as "<name>:<frame>,<name>:<frame>,..."
		cmds.setAttr(OBJECT_NAMES['xanim'][2]+".notetracks", size=EXPORT_WINDOW_NUMSLOTS)
	if not cmds.attributeQuery("useinmultiexport", node=OBJECT_NAMES['xanim'][2], exists=True):
		cmds.addAttr(OBJECT_NAMES['xanim'][2], longName="useinmultiexport", multi=True, attributeType='bool', defaultValue=False)
		cmds.setAttr(OBJECT_NAMES['xanim'][2]+".useinmultiexport", size=EXPORT_WINDOW_NUMSLOTS)
	
	cmds.lockNode(OBJECT_NAMES['xanim'][2], lock=True)
	
	# Set values
	slotIndex = cmds.optionMenu(OBJECT_NAMES['xanim'][0]+"_SlotDropDown", query=True, select=True)	
	cmds.setAttr(OBJECT_NAMES['xanim'][2]+".slot", slotIndex)
	
	path = cmds.getAttr(OBJECT_NAMES['xanim'][2]+(".paths[%i]" % slotIndex))
	cmds.textField(OBJECT_NAMES['xanim'][0]+"_SaveToField", edit=True, fileName=path)
	
	frameRange = cmds.getAttr(OBJECT_NAMES['xanim'][2]+(".frameRanges[%i]" % slotIndex))
	if frameRange == None:
		cmds.setAttr(OBJECT_NAMES['xanim'][2]+(".frameRanges[%i]" % slotIndex), 0, 0, type='long2')
		cmds.intField(OBJECT_NAMES['xanim'][0]+"_FrameStartField", edit=True, value=0)
		cmds.intField(OBJECT_NAMES['xanim'][0]+"_FrameEndField", edit=True, value=0)
	else:
		cmds.intField(OBJECT_NAMES['xanim'][0]+"_FrameStartField", edit=True, value=frameRange[0][0])
		cmds.intField(OBJECT_NAMES['xanim'][0]+"_FrameEndField", edit=True, value=frameRange[0][1])
	
	framerate = cmds.getAttr(OBJECT_NAMES['xanim'][2]+(".framerate[%i]" % slotIndex))
	cmds.intField(OBJECT_NAMES['xanim'][0]+"_FPSField", edit=True, value=framerate)
	
	noteFrameField = cmds.intField(OBJECT_NAMES['xanim'][0]+"_NoteFrameField", edit=True, value=0)
	cmds.textScrollList(OBJECT_NAMES['xanim'][0]+"_NoteList", edit=True, removeAll=True)
	noteList = cmds.getAttr(OBJECT_NAMES['xanim'][2]+(".notetracks[%i]" % slotIndex)) or ""
	notes = noteList.split(",")
	for note in notes:
		parts = note.split(":")
		if note.strip() == "" or len(parts) == 0:
			continue
		
		name = "".join([c for c in parts[0] if c.isalnum() or c=="_"])
		if name == "":
			continue
		
		cmds.textScrollList(OBJECT_NAMES['xanim'][0]+"_NoteList", edit=True, append=name)
		
	useInMultiExport = cmds.getAttr(OBJECT_NAMES['xanim'][2]+(".useinmultiexport[%i]" % slotIndex))
	cmds.checkBox(OBJECT_NAMES['xanim'][0]+"_UseInMultiExportCheckBox", edit=True, value=useInMultiExport)
	
	
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------- XCam Export Window -----------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------	
def CreateXCamWindow():
	# Create window
	if cmds.control(OBJECT_NAMES['xcam'][0], exists=True):
		cmds.deleteUI(OBJECT_NAMES['xcam'][0])
	
	cmds.window(OBJECT_NAMES['xcam'][0], title=OBJECT_NAMES['xcam'][1], width=1, height=1, retain=True, maximizeButton=False)
	form = cmds.formLayout(OBJECT_NAMES['xcam'][0]+"_Form")
	
	# Controls
	slotDropDown = cmds.optionMenu(OBJECT_NAMES['xcam'][0]+"_SlotDropDown", changeCommand="CoDMayaTools.RefreshXCamWindow()", annotation="Each slot contains different a export path, frame range, notetrack, and saved selection")
	for i in range(1, EXPORT_WINDOW_NUMSLOTS+1):
		cmds.menuItem(OBJECT_NAMES['xmodel'][0]+"_SlotDropDown"+("_s%i" % i), label="Slot %i" % i)
	
	separator1 = cmds.separator(style='in')
	separator2 = cmds.separator(style='in')
	separator3 = cmds.separator(style='in')
	
	framesLabel = cmds.text(label="Frames:", annotation="Range of frames to export")
	framesStartField = cmds.intField(OBJECT_NAMES['xcam'][0]+"_FrameStartField", height=21, width=35, minValue=0, changeCommand="CoDMayaTools.UpdateFrameRange('xcam')", annotation="Starting frame to export (inclusive)")
	framesToLabel = cmds.text(label="to")
	framesEndField = cmds.intField(OBJECT_NAMES['xcam'][0]+"_FrameEndField", height=21, width=35, minValue=0, changeCommand="CoDMayaTools.UpdateFrameRange('xcam')", annotation="Ending frame to export (inclusive)")
	fpsLabel = cmds.text(label="FPS:")
	fpsField = cmds.intField(OBJECT_NAMES['xcam'][0]+"_FPSField", height=21, width=35, value=1, minValue=1, changeCommand="CoDMayaTools.UpdateFramerate('xcam')", annotation="Animation FPS")
	#qualityLabel = cmds.text(label="Quality (0-10)", annotation="Quality of the animation, higher values result in less jitter but produce larger files. Default is 0")
	#qualityField = cmds.intField(OBJECT_NAMES['xcam'][0]+"_qualityField", height=21, width=35, value=0, minValue=0, maxValue=10, step=1, changeCommand=XCamWindow_UpdateMultiplier, annotation="Quality of the animation, higher values result in less jitter but produce larger files.")
	
	notetracksLabel = cmds.text(label="Notetrack:", annotation="Notetrack info for the animation")
	noteList = cmds.textScrollList(OBJECT_NAMES['xcam'][0]+"_NoteList", allowMultiSelection=False, selectCommand="CoDMayaTools.SelectNote('xcam')", annotation="List of notes in the notetrack")
	addNoteButton = cmds.button(label="Add Note", width=75, command="CoDMayaTools.AddNote('xcam')", annotation="Add a note to the notetrack")
	ReadNotesButton = cmds.button(label="Grab Notes", width=75, command="CoDMayaTools.ReadNotetracks('xcam')", annotation="Grab Notes from Notetrack in Outliner")
	RenameNoteTrack = cmds.button(label="Rename Note", command="CoDMayaTools.RenameNotes('xcam')", annotation="Rename the currently selected note.")
	removeNoteButton = cmds.button(label="Remove Note", command="CoDMayaTools.RemoveNote('xcam')", annotation="Remove the currently selected note from the notetrack")
	noteFrameLabel = cmds.text(label="Frame:", annotation="The frame the currently selected note is applied to")
	noteFrameField = cmds.intField(OBJECT_NAMES['xcam'][0]+"_NoteFrameField", changeCommand="CoDMayaTools.UpdateNoteFrame('xcam')", height=21, width=30, minValue=0, annotation="The frame the currently selected note is applied to")
	GrabFrames = cmds.button(label="Grab Frames", width=75, command="CoDMayaTools.SetFrames('xcam')", annotation="Get frame end and start from scene.")
	ClearNotes = cmds.button(label="Clear Notes", width=75, command="CoDMayaTools.ClearNotes('xcam')", annotation="Clear ALL notetracks.")
	saveToLabel = cmds.text(label="Save to:", annotation="This is where .xcam_export is saved to")
	saveToField = cmds.textField(OBJECT_NAMES['xcam'][0]+"_SaveToField", height=21, changeCommand="CoDMayaTools.GeneralWindow_SaveToField('xcam')", annotation="This is where .xcam_export is saved to")
	fileBrowserButton = cmds.button(label="...", height=21, command="CoDMayaTools.GeneralWindow_FileBrowser('xcam', \"XCam Intermediate File (*.xcam_export)\")", annotation="Open a file browser dialog")
	
	exportSelectedButton = cmds.button(label="Export Selected", command="CoDMayaTools.GeneralWindow_ExportSelected('xcam', False)", annotation="Export all currently selected joints from the scene (specified frames)\nWarning: Will automatically overwrite if the export path if it already exists")
	saveSelectionButton = cmds.button(label="Save Selection", command="CoDMayaTools.GeneralWindow_SaveSelection('xcam')", annotation="Save the current object selection")
	getSavedSelectionButton = cmds.button(label="Get Saved Selection", command="CoDMayaTools.GeneralWindow_GetSavedSelection('xcam')", annotation="Reselect the saved selection")
	
	exportMultipleSlotsButton = cmds.button(label="Export Multiple Slots", command="CoDMayaTools.GeneralWindow_ExportMultiple('xcam')", annotation="Automatically export multiple slots at once, using each slot's saved selection")
	exportInMultiExportCheckbox = cmds.checkBox(OBJECT_NAMES['xcam'][0]+"_UseInMultiExportCheckBox", label="Use current slot for Export Multiple", changeCommand="CoDMayaTools.GeneralWindow_ExportInMultiExport('xcam')", annotation="Check this make the 'Export Multiple Slots' button export this slot")
	#ReverseAnimation = cmds.checkBox("CoDMAYA_ReverseAnim", label="Export Animation Reversed", annotation="Check this if you want to export the anim. backwards. Usefule for reversing to make opposite sprints, etc.", value=False)
	# Setup form
	cmds.formLayout(form, edit=True,
		attachForm=[(slotDropDown, 'top', 6), (slotDropDown, 'left', 10), (slotDropDown, 'right', 10),
					(separator1, 'left', 0), (separator1, 'right', 0),
					(framesLabel, 'left', 10),
					(fpsLabel, 'left', 10),
					#(qualityLabel, 'left', 10),
					(notetracksLabel, 'left', 10),
					(noteList, 'left', 10),
					#(ReverseAnimation, 'left', 10),
					(addNoteButton, 'right', 10),
					(ReadNotesButton, 'right', 10),
					(RenameNoteTrack, 'right', 10),
					(ClearNotes, 'right', 10),
					(removeNoteButton, 'right', 10),
					(noteFrameField, 'right', 10),
					(separator2, 'left', 0), (separator2, 'right', 0),
					(saveToLabel, 'left', 12),
					(fileBrowserButton, 'right', 10),
					(exportMultipleSlotsButton, 'bottom', 6), (exportMultipleSlotsButton, 'left', 10),
					(exportInMultiExportCheckbox, 'bottom', 9), (exportInMultiExportCheckbox, 'right', 6),
					(exportSelectedButton, 'left', 10),
					(saveSelectionButton, 'right', 10),
					(separator3, 'left', 0), (separator3, 'right', 0)],
		
		attachControl=[	(separator1, 'top', 6, slotDropDown),
						(framesLabel, 'top', 8, separator1),
						(framesStartField, 'top', 5, separator1), (framesStartField, 'left', 4, framesLabel),
						(framesToLabel, 'top', 8, separator1), (framesToLabel, 'left', 4+35+4, framesLabel),
						(framesEndField, 'top', 5, separator1), (framesEndField, 'left', 4, framesToLabel),
						(GrabFrames, 'top', 5, separator1), (GrabFrames, 'left', 4, framesEndField),
						(fpsLabel, 'top', 8, framesStartField),
						(fpsField, 'top', 5, framesStartField), (fpsField, 'left', 21, fpsLabel),
						#(qualityLabel, 'top', 8, fpsField),
						#(qualityField, 'top', 5, fpsField), (qualityField, 'left', 21, qualityLabel),
						(notetracksLabel, 'top', 5, fpsField),
						(noteList, 'top', 5, notetracksLabel), (noteList, 'right', 10, removeNoteButton), (noteList, 'bottom', 60, separator2),
						#(ReverseAnimation, 'top', 10, noteList), (ReverseAnimation, 'right', 10, removeNoteButton),
						(addNoteButton, 'top', 5, notetracksLabel),
						(ReadNotesButton, 'top', 5, addNoteButton),
						(RenameNoteTrack, 'top', 5, ReadNotesButton),
						(ClearNotes, 'top', 5, RenameNoteTrack),
						(removeNoteButton, 'top', 5, ClearNotes),
						(noteFrameField, 'top', 5, removeNoteButton),
						(noteFrameLabel, 'top', 8, removeNoteButton), (noteFrameLabel, 'right', 4, noteFrameField),
						(separator2, 'bottom', 5, fileBrowserButton),
						(saveToLabel, 'bottom', 10, exportSelectedButton),
						(saveToField, 'bottom', 5, exportSelectedButton), (saveToField, 'left', 5, saveToLabel), (saveToField, 'right', 5, fileBrowserButton),
						(fileBrowserButton, 'bottom', 5, exportSelectedButton),
						(exportSelectedButton, 'bottom', 5, separator3),
						(saveSelectionButton, 'bottom', 5, separator3),
						(getSavedSelectionButton, 'bottom', 5, separator3), (getSavedSelectionButton, 'right', 10, saveSelectionButton),
						(separator3, 'bottom', 5, exportMultipleSlotsButton)
						])


def RefreshXCamWindow():
	# Refresh/create node
	if len(cmds.ls(OBJECT_NAMES['xcam'][2])) == 0:
		cmds.createNode("renderLayer", name=OBJECT_NAMES['xcam'][2], skipSelect=True)
	
	cmds.lockNode(OBJECT_NAMES['xcam'][2], lock=False)
	
	if not cmds.attributeQuery("slot", node=OBJECT_NAMES['xcam'][2], exists=True):
		cmds.addAttr(OBJECT_NAMES['xcam'][2], longName="slot", attributeType='short', defaultValue=1)
	if not cmds.attributeQuery("paths", node=OBJECT_NAMES['xcam'][2], exists=True):
		cmds.addAttr(OBJECT_NAMES['xcam'][2], longName="paths", multi=True, dataType='string')
		cmds.setAttr(OBJECT_NAMES['xcam'][2]+".paths", size=EXPORT_WINDOW_NUMSLOTS)
	if not cmds.attributeQuery("selections", node=OBJECT_NAMES['xcam'][2], exists=True):
		cmds.addAttr(OBJECT_NAMES['xcam'][2], longName="selections", multi=True, dataType='stringArray')
		cmds.setAttr(OBJECT_NAMES['xcam'][2]+".selections", size=EXPORT_WINDOW_NUMSLOTS)
	if not cmds.attributeQuery("frameRanges", node=OBJECT_NAMES['xcam'][2], exists=True):
		cmds.addAttr(OBJECT_NAMES['xcam'][2], longName="frameRanges", multi=True, dataType='long2')
		cmds.setAttr(OBJECT_NAMES['xcam'][2]+".frameRanges", size=EXPORT_WINDOW_NUMSLOTS)
	if not cmds.attributeQuery("framerate", node=OBJECT_NAMES['xcam'][2], exists=True):
		cmds.addAttr(OBJECT_NAMES['xcam'][2], longName="framerate", multi=True, attributeType='long', defaultValue=30)
		cmds.setAttr(OBJECT_NAMES['xcam'][2]+".framerate", size=EXPORT_WINDOW_NUMSLOTS)
	if not cmds.attributeQuery("multiplier", node=OBJECT_NAMES['xcam'][2], exists=True):
		cmds.addAttr(OBJECT_NAMES['xcam'][2], longName="multiplier", multi=True, attributeType='long', defaultValue=30)
		cmds.setAttr(OBJECT_NAMES['xcam'][2]+".multiplier", size=EXPORT_WINDOW_NUMSLOTS)
	if not cmds.attributeQuery("notetracks", node=OBJECT_NAMES['xcam'][2], exists=True):
		cmds.addAttr(OBJECT_NAMES['xcam'][2], longName="notetracks", multi=True, dataType='string') # Formatted as "<name>:<frame>,<name>:<frame>,..."
		cmds.setAttr(OBJECT_NAMES['xcam'][2]+".notetracks", size=EXPORT_WINDOW_NUMSLOTS)
	if not cmds.attributeQuery("useinmultiexport", node=OBJECT_NAMES['xcam'][2], exists=True):
		cmds.addAttr(OBJECT_NAMES['xcam'][2], longName="useinmultiexport", multi=True, attributeType='bool', defaultValue=False)
		cmds.setAttr(OBJECT_NAMES['xcam'][2]+".useinmultiexport", size=EXPORT_WINDOW_NUMSLOTS)
	
	cmds.lockNode(OBJECT_NAMES['xcam'][2], lock=True)
	
	# Set values
	slotIndex = cmds.optionMenu(OBJECT_NAMES['xcam'][0]+"_SlotDropDown", query=True, select=True)	
	cmds.setAttr(OBJECT_NAMES['xcam'][2]+".slot", slotIndex)
	
	path = cmds.getAttr(OBJECT_NAMES['xcam'][2]+(".paths[%i]" % slotIndex))
	cmds.textField(OBJECT_NAMES['xcam'][0]+"_SaveToField", edit=True, fileName=path)
	
	frameRange = cmds.getAttr(OBJECT_NAMES['xcam'][2]+(".frameRanges[%i]" % slotIndex))
	if frameRange == None:
		cmds.setAttr(OBJECT_NAMES['xcam'][2]+(".frameRanges[%i]" % slotIndex), 0, 0, type='long2')
		cmds.intField(OBJECT_NAMES['xcam'][0]+"_FrameStartField", edit=True, value=0)
		cmds.intField(OBJECT_NAMES['xcam'][0]+"_FrameEndField", edit=True, value=0)
	else:
		cmds.intField(OBJECT_NAMES['xcam'][0]+"_FrameStartField", edit=True, value=frameRange[0][0])
		cmds.intField(OBJECT_NAMES['xcam'][0]+"_FrameEndField", edit=True, value=frameRange[0][1])
	
	framerate = cmds.getAttr(OBJECT_NAMES['xcam'][2]+(".framerate[%i]" % slotIndex))
	cmds.intField(OBJECT_NAMES['xcam'][0]+"_FPSField", edit=True, value=framerate)
	
	noteFrameField = cmds.intField(OBJECT_NAMES['xcam'][0]+"_NoteFrameField", edit=True, value=0)
	cmds.textScrollList(OBJECT_NAMES['xcam'][0]+"_NoteList", edit=True, removeAll=True)
	noteList = cmds.getAttr(OBJECT_NAMES['xcam'][2]+(".notetracks[%i]" % slotIndex)) or ""
	notes = noteList.split(",")
	for note in notes:
		parts = note.split(":")
		if note.strip() == "" or len(parts) == 0:
			continue
		
		name = "".join([c for c in parts[0] if c.isalnum() or c=="_"])
		if name == "":
			continue
		
		cmds.textScrollList(OBJECT_NAMES['xcam'][0]+"_NoteList", edit=True, append=name)
		
	useInMultiExport = cmds.getAttr(OBJECT_NAMES['xcam'][2]+(".useinmultiexport[%i]" % slotIndex))
	cmds.checkBox(OBJECT_NAMES['xcam'][0]+"_UseInMultiExportCheckBox", edit=True, value=useInMultiExport)
	
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------- xAnim/xcam Export Data --------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""
Set Frames

Querys start and end frames and set thems for the window given by windowID

"""
def SetFrames(windowID):
    start = cmds.playbackOptions(minTime=True, query=True)
    end = cmds.playbackOptions(maxTime=True, query=True)  # Query start and end froms.
    cmds.intField(OBJECT_NAMES[windowID][0] + "_FrameStartField", edit=True, value=start)
    cmds.intField(OBJECT_NAMES[windowID][0] + "_FrameEndField", edit=True, value=end)
    UpdateFrameRange(windowID)

"""
Update Frame Range

Updates start and end frame when set by user or by other means.

"""
def UpdateFrameRange(windowID):
	slotIndex = cmds.optionMenu(OBJECT_NAMES[windowID][0]+"_SlotDropDown", query=True, select=True)
	start = cmds.intField(OBJECT_NAMES[windowID][0]+"_FrameStartField", query=True, value=True)
	end = cmds.intField(OBJECT_NAMES[windowID][0]+"_FrameEndField", query=True, value=True)
	cmds.setAttr(OBJECT_NAMES[windowID][2]+(".frameRanges[%i]" % slotIndex), start, end, type='long2')

"""
Update Framerate

Updates framerate when set by user or by other means.

"""
def UpdateFramerate(windowID):
	slotIndex = cmds.optionMenu(OBJECT_NAMES[windowID][0]+"_SlotDropDown", query=True, select=True)
	fps = cmds.intField(OBJECT_NAMES[windowID][0]+"_FPSField", query=True, value=True)
	cmds.setAttr(OBJECT_NAMES[windowID][2]+(".framerate[%i]" % slotIndex), fps)

"""
Update multiplier

Updates multiplier when set by user or by other means.

"""
def UpdateMultiplier(windowID):
	slotIndex = cmds.optionMenu(OBJECT_NAMES[windowID][0]+"_SlotDropDown", query=True, select=True)
	fps = cmds.intField(OBJECT_NAMES[windowID][0]+"_qualityField", query=True, value=True)
	cmds.setAttr(OBJECT_NAMES[windowID][2]+(".multiplier[%i]" % slotIndex), fps)

"""
Add notetrack

Add notetrack to window and attribute when user creates one.

"""
def AddNote(windowID):
	slotIndex = cmds.optionMenu(OBJECT_NAMES[windowID][0]+"_SlotDropDown", query=True, select=True)
	if cmds.promptDialog(title="Add Note to Slot %i's Notetrack" % slotIndex, message="Enter the note's name:\t\t  ") != "Confirm":
		return
	
	userInput = cmds.promptDialog(query=True, text=True)
	noteName = "".join([c for c in userInput if c.isalnum() or c=="_"]) # Remove all non-alphanumeric characters
	if noteName == "":
		MessageBox("Invalid note name")
		return
		
	existingItems = cmds.textScrollList(OBJECT_NAMES[windowID][0]+"_NoteList", query=True, allItems=True)
	
	if existingItems != None and noteName in existingItems:
		MessageBox("A note with this name already exists")
		
	noteList = cmds.getAttr(OBJECT_NAMES[windowID][2]+(".notetracks[%i]" % slotIndex)) or ""
	noteList += "%s:%i," % (noteName, cmds.currentTime(query=True))
	cmds.setAttr(OBJECT_NAMES['xanim'][2]+(".notetracks[%i]" % slotIndex), noteList, type='string')
	
	cmds.textScrollList(OBJECT_NAMES[windowID][0]+"_NoteList", edit=True, append=noteName, selectIndexedItem=len((existingItems or []))+1)
	SelectNote(windowID)

"""
Read notetracks 

Read notetracks from imported animations.

"""
def ReadNotetracks(windowID):
	slotIndex = cmds.optionMenu(OBJECT_NAMES[windowID][0]+"_SlotDropDown", query=True, select=True)
	existingItems = cmds.textScrollList(OBJECT_NAMES[windowID][0]+"_NoteList", query=True, allItems=True)
	noteList = cmds.getAttr(OBJECT_NAMES[windowID][2]+(".notetracks[%i]" % slotIndex)) or ""

	notetracks = {"WraithNotes" : "translateX",
				  "SENotes": "translateX", 
				  "NoteTrack" : "MainNote"}

	for notetrack, attribute in notetracks.iteritems():
		if cmds.objExists(notetrack):
			cmds.select( clear=True )
			cmds.select( notetrack, hi=True )

			notes = cmds.ls( selection=True, type="transform" ) # Grab what is selected.

			for NoteTrack in notes: # Go through each one.
				try:
					for note in cmds.keyframe(NoteTrack, attribute="translateX", sl=False, q=True, tc=True): # See where are the keyframes.
						if NoteTrack == "end" or NoteTrack == "loop_end":
							continue
						noteList += "%s:%i," % (NoteTrack, note) # Add Notes to Aidan's list.
						cmds.setAttr(OBJECT_NAMES[windowID][2]+(".notetracks[%i]" % slotIndex), noteList, type='string')
						cmds.textScrollList(OBJECT_NAMES[windowID][0]+"_NoteList", edit=True, append=NoteTrack, selectIndexedItem=len((existingItems or []))+1)
				except Exception as e:
					print("Error has occured while reading note: %s, the error was: '%s', Skipping." % (NoteTrack, e))
					pass

	SelectNote(windowID)

"""
Rename notetrack 

Rename selected notetrack.

"""
def RenameNotes(windowID):
	slotIndex = cmds.optionMenu(OBJECT_NAMES[windowID][0]+"_SlotDropDown", query=True, select=True)
	currentIndex = cmds.textScrollList(OBJECT_NAMES[windowID][0]+"_NoteList", query=True, selectIndexedItem=True)
	if currentIndex != None and len(currentIndex) > 0 and currentIndex[0] >= 1:
		if cmds.promptDialog(title="Rename NoteTrack in slot", message="Enter new notetrack name:\t\t  ") != "Confirm":
			return
	
		userInput = cmds.promptDialog(query=True, text=True)
		noteName = "".join([c for c in userInput if c.isalnum() or c=="_"]) # Remove all non-alphanumeric characters
		if noteName == "":
			MessageBox("Invalid note name")
			return
		currentIndex = currentIndex[0]
		noteList = cmds.getAttr(OBJECT_NAMES[windowID][2]+(".notetracks[%i]" % slotIndex)) or ""
		notes = noteList.split(",")
		noteInfo = notes[currentIndex-1].split(":")
		note = int(noteInfo[1])
		NoteTrack = userInput
		
		# REMOVE NOTE

		cmds.textScrollList(OBJECT_NAMES[windowID][0]+"_NoteList", edit=True, removeIndexedItem=currentIndex)
		noteList = cmds.getAttr(OBJECT_NAMES[windowID][2]+(".notetracks[%i]" % slotIndex)) or ""
		notes = noteList.split(",")
		del notes[currentIndex-1]
		noteList = ",".join(notes)
		cmds.setAttr(OBJECT_NAMES[windowID][2]+(".notetracks[%i]" % slotIndex), noteList, type='string')

		# REMOVE NOTE
		noteList = cmds.getAttr(OBJECT_NAMES[windowID][2]+(".notetracks[%i]" % slotIndex)) or ""
		noteList += "%s:%i," % (NoteTrack, note) # Add Notes to Aidan's list.
		cmds.setAttr(OBJECT_NAMES[windowID][2]+(".notetracks[%i]" % slotIndex), noteList, type='string')
		cmds.textScrollList(OBJECT_NAMES[windowID][0]+"_NoteList", edit=True, append=NoteTrack, selectIndexedItem=currentIndex)
		SelectNote(windowID)


"""
Remove Note 

Remove selected notetrack.

"""	
def RemoveNote(windowID):
	slotIndex = cmds.optionMenu(OBJECT_NAMES[windowID][0]+"_SlotDropDown", query=True, select=True)
	currentIndex = cmds.textScrollList(OBJECT_NAMES[windowID][0]+"_NoteList", query=True, selectIndexedItem=True)
	if currentIndex != None and len(currentIndex) > 0 and currentIndex[0] >= 1:
		currentIndex = currentIndex[0]
		cmds.textScrollList(OBJECT_NAMES[windowID][0]+"_NoteList", edit=True, removeIndexedItem=currentIndex)
		noteList = cmds.getAttr(OBJECT_NAMES[windowID][2]+(".notetracks[%i]" % slotIndex)) or ""
		notes = noteList.split(",")
		del notes[currentIndex-1]
		noteList = ",".join(notes)
		cmds.setAttr(OBJECT_NAMES[windowID][2]+(".notetracks[%i]" % slotIndex), noteList, type='string')
		SelectNote(windowID)

"""
Clear notetracks 

Clear ALL notetracks.

"""
def ClearNotes(windowID):
	slotIndex = cmds.optionMenu(OBJECT_NAMES[windowID][0]+"_SlotDropDown", query=True, select=True)
	notes = cmds.textScrollList(OBJECT_NAMES[windowID][0]+"_NoteList", query=True, allItems=True)
	if notes is None:
		return
	for note in notes:
		cmds.textScrollList(OBJECT_NAMES[windowID][0]+"_NoteList", edit=True, removeItem=note)
	noteList = cmds.getAttr(OBJECT_NAMES[windowID][2]+(".notetracks[%i]" % slotIndex)) or ""
	notetracks = noteList.split(",")
	del notetracks
	noteList = ""
	cmds.setAttr(OBJECT_NAMES[windowID][2]+(".notetracks[%i]" % slotIndex), noteList, type='string')
	SelectNote(windowID)
	
"""
Update Notetrack

Update notetrack information.

"""	
def UpdateNoteFrame(windowID):
	newFrame = cmds.intField(OBJECT_NAMES[windowID][0] + "_NoteFrameField", query = True, value = True)
	slotIndex = cmds.optionMenu(OBJECT_NAMES[windowID][0]+"_SlotDropDown", query=True, select=True)
	currentIndex = cmds.textScrollList(OBJECT_NAMES[windowID][0]+"_NoteList", query=True, selectIndexedItem=True)
	if currentIndex != None and len(currentIndex) > 0 and currentIndex[0] >= 1:
		currentIndex = currentIndex[0]
		noteList = cmds.getAttr(OBJECT_NAMES[windowID][2]+(".notetracks[%i]" % slotIndex)) or ""
		notes = noteList.split(",")
		parts = notes[currentIndex-1].split(":")
		if len(parts) < 2:
			parts("Error parsing notetrack string (A) at %i: %s" % (currentIndex, noteList))
		notes[currentIndex-1] = "%s:%i" % (parts[0], newFrame)
		noteList = ",".join(notes)
		cmds.setAttr(OBJECT_NAMES[windowID][2]+(".notetracks[%i]" % slotIndex), noteList, type='string')
	
"""
Select notetracks

Select notetrack 

"""
def SelectNote(windowID):
	slotIndex = cmds.optionMenu(OBJECT_NAMES[windowID][0]+"_SlotDropDown", query=True, select=True)
	currentIndex = cmds.textScrollList(OBJECT_NAMES[windowID][0]+"_NoteList", query=True, selectIndexedItem=True)
	if currentIndex != None and len(currentIndex) > 0 and currentIndex[0] >= 1:
		currentIndex = currentIndex[0]
		noteList = cmds.getAttr(OBJECT_NAMES[windowID][2]+(".notetracks[%i]" % slotIndex)) or ""
		notes = noteList.split(",")
		parts = notes[currentIndex-1].split(":")
		if len(parts) < 2:
			error("Error parsing notetrack string (B) at %i: %s" % (currentIndex, noteList))
			
		frame=0
		try: 
			frame = int(parts[1])
		except ValueError:
			pass
			
		noteFrameField = cmds.intField(OBJECT_NAMES[windowID][0]+"_NoteFrameField", edit=True, value=frame)

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------- General Export Window ---------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
# GeneralWindow_... are callback functions that are used by both export windows
def GeneralWindow_SaveToField(windowID):
	slotIndex = cmds.optionMenu(OBJECT_NAMES[windowID][0]+"_SlotDropDown", query=True, select=True)
	filePath = cmds.textField(OBJECT_NAMES[windowID][0]+"_SaveToField", query=True, fileName=True)
	cmds.setAttr(OBJECT_NAMES[windowID][2]+(".paths[%i]" % slotIndex), filePath, type='string')
	
def GeneralWindow_FileBrowser(windowID, formatExtension):
	defaultFolder = GetRootFolder()
	if windowID == 'xanim':
		defaultFolder = defaultFolder + 'xanim_export/'
	elif windowID == 'xcam':
		defaultFolder = defaultFolder + 'xanim_export/'
	elif windowID == 'xmodel':
		defaultFolder = defaultFolder + 'model_export/'
	saveTo = cmds.fileDialog2(fileMode=0, fileFilter=formatExtension, caption="Export To", startingDirectory=defaultFolder)
	if saveTo == None or len(saveTo) == 0 or saveTo[0].strip() == "":
		return
	saveTo = saveTo[0].strip()
	
	cmds.textField(OBJECT_NAMES[windowID][0]+"_SaveToField", edit=True, fileName=saveTo)
	GeneralWindow_SaveToField(windowID)

def GeneralWindow_SaveSelection(windowID):
	slotIndex = cmds.optionMenu(OBJECT_NAMES[windowID][0]+"_SlotDropDown", query=True, select=True)
	selection = cmds.ls(selection=True)
	if selection == None or len(selection) == 0:
		return
	cmds.setAttr(OBJECT_NAMES[windowID][2]+(".selections[%i]" % slotIndex), len(selection), *selection, type='stringArray')
	
def GeneralWindow_GetSavedSelection(windowID):
	slotIndex = cmds.optionMenu(OBJECT_NAMES[windowID][0]+"_SlotDropDown", query=True, select=True)
	selection = cmds.getAttr(OBJECT_NAMES[windowID][2]+(".selections[%i]" % slotIndex))
	
	validSelection = []
	for obj in selection:
		if cmds.objExists(obj):
			validSelection.append(obj)
	
	# Remove non-existing objects from the saved list
	cmds.setAttr(OBJECT_NAMES[windowID][2]+(".selections[%i]" % slotIndex), len(validSelection), *validSelection, type='stringArray')
	
	if validSelection == None or len(validSelection) == 0:
		MessageBox("No selection saved to slot %i" % slotIndex)
		return False
	
	cmds.select(validSelection)
	return True

def GeneralWindow_ExportSelected(windowID, exportingMultiple):
	global WarningsDuringExport
	
	slotIndex = cmds.optionMenu(OBJECT_NAMES[windowID][0]+"_SlotDropDown", query=True, select=True)
	
	# Get path
	filePath = cmds.textField(OBJECT_NAMES[windowID][0]+"_SaveToField", query=True, fileName=True)
	if filePath.strip() == "":
		if exportingMultiple:
			MessageBox("Invalid path on slot %i:\n\nPath is empty." % slotIndex)
		else:
			MessageBox("Invalid path:\n\nPath is empty.")
		return
		
	if os.path.isdir(filePath):
		if exportingMultiple:
			MessageBox("Invalid path on slot %i:\n\nPath points to an existing directory." % slotIndex)
		else:
			MessageBox("Invalid path:\n\nPath points to an existing directory.")
		return
		
	# Save reminder
	if not exportingMultiple and not SaveReminder():
		return
	
	# Progress bar
	if cmds.control("w"+OBJECT_NAMES['progress'][0], exists=True):
		cmds.deleteUI("w"+OBJECT_NAMES['progress'][0])
	progressWindow = cmds.window("w"+OBJECT_NAMES['progress'][0], title=OBJECT_NAMES['progress'][1], width=302, height=22, sizeable=False)
	cmds.columnLayout()
	progressControl = cmds.progressBar(OBJECT_NAMES['progress'][0], width=300)
	if QueryToggableOption("PrintExport") and windowID == "xmodel":
		cmds.scrollField("ExportLog", editable=False, wordWrap=False, width = 300)
	cmds.showWindow(progressWindow)
	cmds.refresh() # Force the progress bar to be drawn
	
	# Export
	if not exportingMultiple:
		WarningsDuringExport = 0
	response = None
	try:
		exec("response = %s(\"%s\")" % (OBJECT_NAMES[windowID][4], filePath))
	except Exception as e:
		response = "An unhandled error occurred during export:\n\n" + traceback.format_exc()

	if windowID == "xanim":
		cmds.deleteUI(progressWindow, window=True)
	
	# Delete progress bar
	if not QueryToggableOption("PrintExport") and windowID == "xmodel":
		cmds.deleteUI(progressWindow, window=True)
	
	# Handle response
	
	if type(response) == str or type(response) == unicode:
		if exportingMultiple:
			MessageBox("Slot %i\n\n%s" % (slotIndex, response))
		else:
			MessageBox(response)
	elif WarningsDuringExport > 0 and not exportingMultiple:
		MessageBox("Warnings occurred during export. Check the script editor output for more details.")

def GeneralWindow_ExportMultiple(windowID):
	originalSlotIndex = cmds.optionMenu(OBJECT_NAMES[windowID][0]+"_SlotDropDown", query=True, select=True)
	any = False
	for i in range(1, EXPORT_WINDOW_NUMSLOTS+1):
		useInMultiExport = cmds.getAttr(OBJECT_NAMES[windowID][2]+(".useinmultiexport[%i]" % i))
		if useInMultiExport:
			any = True
			break
	
	if not any:
		MessageBox("No slots set to export.")
		return
	
	if not SaveReminder():
		return
		
	WarningsDuringExport = 0
	originalSelection = cmds.ls(selection=True)
	
	for i in range(1, EXPORT_WINDOW_NUMSLOTS+1):
		useInMultiExport = cmds.getAttr(OBJECT_NAMES[windowID][2]+(".useinmultiexport[%i]" % i))
		if useInMultiExport:
			print "Exporting slot %i in multiexport" % i
			cmds.optionMenu(OBJECT_NAMES[windowID][0]+"_SlotDropDown", edit=True, select=i)
			exec(OBJECT_NAMES[windowID][3] + "()") # Refresh window
			if GeneralWindow_GetSavedSelection(windowID):
				GeneralWindow_ExportSelected(windowID, True)
	
	if originalSelection == None or len(originalSelection) == 0:
		cmds.select(clear=True)
	else:
		cmds.select(originalSelection)
	
	if WarningsDuringExport > 0:
		MessageBox("Warnings occurred during export. Check the script editor output for more details.")			
	
	# Reset slot
	cmds.optionMenu(OBJECT_NAMES[windowID][0]+"_SlotDropDown", edit=True, select=originalSlotIndex)
	exec(OBJECT_NAMES[windowID][3] + "()") # Refresh window
	
def GeneralWindow_ExportInMultiExport(windowID):
	slotIndex = cmds.optionMenu(OBJECT_NAMES[windowID][0]+"_SlotDropDown", query=True, select=True)
	useInMultiExport = cmds.checkBox(OBJECT_NAMES[windowID][0]+"_UseInMultiExportCheckBox", query=True, value=True)
	cmds.setAttr(OBJECT_NAMES[windowID][2]+(".useinmultiexport[%i]" % slotIndex), useInMultiExport)

	
	
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------- General GUI --------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
def SaveReminder(allowUnsaved=True):
	if cmds.file(query=True, modified=True):
		if cmds.file(query=True, exists=True):
			result = cmds.confirmDialog(message="Save changes to %s?" % cmds.file(query=True, sceneName=True), button=["Yes", "No", "Cancel"], defaultButton="Yes", title="Save Changes")
			if result == "Yes":
				cmds.file(save=True)
			elif result != "No":
				return False
		else: # The file has never been saved (has no name)
			if allowUnsaved:
				result = cmds.confirmDialog(message="The current scene is not saved. Continue?", button=["Yes", "No"], defaultButton="Yes", title="Save Changes")
				if result != "Yes":
					return False
			else:
				MessageBox("The scene needs to be saved first")
				return False
				
	return True

def PrintWarning(message):
	global WarningsDuringExport
	if WarningsDuringExport < MAX_WARNINGS_SHOWN:
		print "WARNING: %s" % message
		WarningsDuringExport += 1
	elif WarningsDuringExport == MAX_WARNINGS_SHOWN:
		print "More warnings not shown because printing text is slow...\n"
		WarningsDuringExport = MAX_WARNINGS_SHOWN+1

def MessageBox(message):
	cmds.confirmDialog(message=message, button='OK', defaultButton='OK', title=OBJECT_NAMES['menu'][1])
		
def ShowWindow(windowID):
	exec(OBJECT_NAMES[windowID][3] + "()") # Refresh window
	cmds.showWindow(OBJECT_NAMES[windowID][0])

def ProgressBarStep():
	cmds.progressBar(OBJECT_NAMES['progress'][0], edit=True, step=1)

def LogExport(text, isWarning = False):
	if QueryToggableOption("PrintExport"):
		if isWarning:
			global WarningsDuringExport
			if WarningsDuringExport < MAX_WARNINGS_SHOWN:
				cmds.scrollField("ExportLog", edit = True, insertText = text)
				WarningsDuringExport += 1
			elif WarningsDuringExport == MAX_WARNINGS_SHOWN:
				cmds.scrollField("ExportLog", edit = True, insertText = "More warnings not shown because printing text is slow...\n")
				WarningsDuringExport = MAX_WARNINGS_SHOWN+1		
		else:
			cmds.scrollField("ExportLog", edit = True, insertText = text)
	
def AboutWindow():
	result = cmds.confirmDialog(message="Call of Duty Tools for Maya, created by Aidan Shafran (with assistance from The Internet).\nMaintained by Ray1235 (Maciej Zaremba) & Scobalula\n\nThis script is under the GNU General Public License. You may modify or redistribute this script, however it comes with no warranty. Go to http://www.gnu.org/licenses/ for more details.", button=['OK', 'Visit Forum Topic', 'CoD File Formats'], defaultButton='OK', title="About " + OBJECT_NAMES['menu'][1])
	if result == "Visit Forum Topic":
		GoToForumTopic()
	elif result == "CoD File Formats":
		webbrowser.open("http://aidanshafran.com/codmayatools/codformats.html")

def LegacyWindow():
	result = cmds.confirmDialog(message="""CoD1 mode exports models that are compatible with CoD1.
When this mode is disabled, the plugin will export models that are compatible with CoD2 and newer.
""", button=['OK'], defaultButton='OK', title="Legacy options")
		
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------- Versioning (Deprecated) --------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
def HasInternetAccess():
	# http://stackoverflow.com/questions/3764291/checking-network-connection
	'''
	try:
		urllib2.urlopen('http://8.8.8.8', timeout=1) # Use IP address (google.com) instead of domain name, to avoid DNS lookup time
		return True
	except urllib2.URLError as err:
		return False
	'''
	response = os.system("ping -c 1 8.8.8.8")
	if response == 0:
		return True
	else:
		return False
def CheckForUpdates():
	try:
		if not HasInternetAccess(): # Apparently, the timeout does not affect DNS lookup time, so internet connectivity needs to be checked before getting update info to avoid long script load times if there is no internet
			return None
			
		response = urllib2.urlopen(VERSION_CHECK_URL, timeout=2)
		info = response.readlines()
		response.close()
		
		if not info or len(info) == 0:
			return None

		mostRecentVersion = float(info[0])
		downloadUpdateURL = info[1] # Location of the most recent file
		
		if mostRecentVersion > FILE_VERSION:
			return (mostRecentVersion, downloadUpdateURL)
	except Exception:
		pass
	
	return None
    
def DownloadUpdate(downloadUpdateURL):
	try:
		if not HasInternetAccess():
			return None
			
		response = urllib2.urlopen(downloadUpdateURL, timeout=5)
		newCode = response.read()
		response.close()

		root, ext = os.path.splitext(__file__)
		updateFile = root + ".py"
		
		file = open(updateFile, 'w')
		file.write(newCode)
		file.close()
		
		MessageBox("The script has been updated. Click 'Reload Script' or restart Maya to apply the changes.")
	except Exception:
		result = cmds.confirmDialog(message="Something went wrong while updating. You can download the update manually from the forum topic.", button=['OK', 'Visit Forum Topic'], defaultButton='OK', title=OBJECT_NAMES['menu'][1])
		if result == "Visit Forum Topic":
			GoToForumTopic()

def GoToForumTopic():
	webbrowser.open("http://ugx-mods.com/forum/index.php?topic=12224.0")	
	
	
	
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------- Get/Set Root Folder ----------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------
def SetRootFolder(msg=None, game="none"):
	#if game == "none":
	#	game = currentGame
	#if game == "none":
	#	res = cmds.confirmDialog(message="Please select the game you're working with", button=['OK'], defaultButton='OK', title="WARNING")
	#	return None
	# Get current root folder (this also makes sure the reg key exists)
	codRootPath = GetRootFolder(False, game)
	
	# Open input box
	#if cmds.promptDialog(title="Set Root Path", message=msg or "Change your root path:\t\t\t", text=codRootPath) != "Confirm":
	#	return None
	
	codRootPath = cmds.fileDialog2(fileMode=3, dialogStyle=2)[0] + "/"
	
	# Check to make sure the path exists
	if not os.path.isdir(codRootPath):
		MessageBox("Given root path does not exist")
		return None
		
	# cmds.promptDialog(title="Set Root Path", message=codRootPath)
	# Set path
	# , 0, reg.KEY_SET_VALUE)
	storageKey = reg.OpenKey(GLOBAL_STORAGE_REG_KEY[0], GLOBAL_STORAGE_REG_KEY[1], 0, reg.KEY_SET_VALUE)
	reg.SetValueEx(storageKey, "RootPath", 0, reg.REG_SZ, codRootPath)
	reg.CloseKey(storageKey)
	
	return codRootPath
	
def GetRootFolder(firstTimePrompt=False, game="none"):
#	if game == "none":
#		game = currentGame
#	if game == "none":
#		res = cmds.confirmDialog(message="Please select the game you're working with", button=['OK'], defaultButton='OK', title="WARNING")
#		return None
	codRootPath = ""
	
	try:
		storageKey = reg.OpenKey(GLOBAL_STORAGE_REG_KEY[0], GLOBAL_STORAGE_REG_KEY[1])
		codRootPath = reg.QueryValueEx(storageKey, "RootPath")[0]
		reg.CloseKey(storageKey)
	except WindowsError:
		# First time, create key
		storageKey = reg.CreateKey(GLOBAL_STORAGE_REG_KEY[0], GLOBAL_STORAGE_REG_KEY[1])
		reg.SetValueEx(storageKey, "RootPath", 0, reg.REG_SZ, "")
		reg.CloseKey(storageKey)
		# http://store.steampowered.com/agecheck/app/311210/
		# Try to get root path from cod registry value
#		try:
#			if game == "CoD5":
#				codKey = reg.OpenKey(reg.HKEY_LOCAL_MACHINE, "SOFTWARE\\Wow6432Node\\Activision\\Call of Duty WAW")
#				codRootPath = reg.QueryValueEx(codKey, "InstallPath")[0]
#				reg.CloseKey(codKey)
#			elif game == "CoD4":
#				codKey = reg.OpenKey(reg.HKEY_LOCAL_MACHINE, "SOFTWARE\\Wow6432Node\\Activision\\Call of Duty 4")
#				codRootPath = reg.QueryValueEx(codKey, "InstallPath")[0]
#				reg.CloseKey(codKey)
#			elif game == "BO3":
#				codRootPath = ""
#		except WindowsError:
#			pass
		
	if not os.path.isdir(codRootPath):
		codRootPath = ""
		
	# Set root path value
	#reg.SetValueEx(storageKey, "RootPath", 0, reg.REG_SZ, codRootPath)

	# First-time prompt
	if firstTimePrompt:
		result = SetRootFolder("Your root folder path hasn't been confirmed yet. If the following is not\ncorrect, please fix it:", game)
		if result:
			codRootPath = result
		
	return codRootPath	

def RunExport2Bin(file):	
	p = GetExport2Bin()

	directory = os.path.dirname(os.path.realpath(file))
	

	if os.path.splitext(os.path.basename(p))[0] == "export2bin":
		p = subprocess.Popen([p, "*"], cwd=directory)
	elif os.path.splitext(os.path.basename(p))[0] == "exportx":
		p = subprocess.Popen([p, "-f %s" % file])

def SetExport2Bin():
	export2binpath = cmds.fileDialog2(fileMode=1, dialogStyle=2)[0]
	
	# Check to make sure the path exists
	if not os.path.isfile(export2binpath):
		MessageBox("Given path does not exist")
		return ""
	storageKey = reg.OpenKey(GLOBAL_STORAGE_REG_KEY[0], GLOBAL_STORAGE_REG_KEY[1], 0, reg.KEY_SET_VALUE)
	reg.SetValueEx(storageKey, "Export2BinPath", 0, reg.REG_SZ, export2binpath)
	reg.CloseKey(storageKey)
	
	return export2binpath

def GetExport2Bin(skipSet=True):
	export2binpath = ""
	try:
		storageKey = reg.OpenKey(GLOBAL_STORAGE_REG_KEY[0], GLOBAL_STORAGE_REG_KEY[1])
		export2binpath = reg.QueryValueEx(storageKey, "Export2BinPath")[0]
		reg.CloseKey(storageKey)
	except WindowsError:
		# First time, create key
		storageKey = reg.CreateKey(GLOBAL_STORAGE_REG_KEY[0], GLOBAL_STORAGE_REG_KEY[1])
		reg.SetValueEx(storageKey, "Export2BinPath", 0, reg.REG_SZ, "")
		reg.CloseKey(storageKey)

	if not os.path.isfile(export2binpath):
		export2binpath = ""

	if not skipSet:
		result = SetExport2Bin()
		if result:
			export2binpath = result

	return export2binpath

 	
def ForceExport2Bin(yesno):
	try:
		storageKey = reg.OpenKey(GLOBAL_STORAGE_REG_KEY[0], GLOBAL_STORAGE_REG_KEY[1])
		bE2B = reg.QueryValueEx(storageKey, "UseExport2Bin")[0]
		reg.CloseKey(storageKey)
	except WindowsError:
		storageKey = reg.OpenKey(GLOBAL_STORAGE_REG_KEY[0], GLOBAL_STORAGE_REG_KEY[1], 0, reg.KEY_SET_VALUE)
		reg.SetValueEx(storageKey, "UseExport2Bin", 0, reg.REG_SZ, "off")
		reg.CloseKey(storageKey)

	storageKey = reg.OpenKey(GLOBAL_STORAGE_REG_KEY[0], GLOBAL_STORAGE_REG_KEY[1], 0, reg.KEY_SET_VALUE)
	reg.SetValueEx(storageKey, "UseExport2Bin", 0, reg.REG_SZ, yesno)
	reg.CloseKey(storageKey)
	CreateMenu()

# Support for custom options, so I don't have to make new funca
def UseOption(name, default="off"):
	bE2B = default
	try:
		storageKey = reg.OpenKey(GLOBAL_STORAGE_REG_KEY[0], GLOBAL_STORAGE_REG_KEY[1])
		bE2B = reg.QueryValueEx(storageKey, "Use%s" % name)[0]
		reg.CloseKey(storageKey)
	except WindowsError:
		storageKey = reg.OpenKey(GLOBAL_STORAGE_REG_KEY[0], GLOBAL_STORAGE_REG_KEY[1], 0, reg.KEY_SET_VALUE)
		reg.SetValueEx(storageKey, "Use%s" % name, 0, reg.REG_SZ, "off")
		reg.CloseKey(storageKey)

	if bE2B == "on":
		res = True
	else:
		res = False

	return res

def ToggleOption(name, default="off"):
	bE2B = default
	try:
		storageKey = reg.OpenKey(GLOBAL_STORAGE_REG_KEY[0], GLOBAL_STORAGE_REG_KEY[1])
		bE2B = reg.QueryValueEx(storageKey, "Use%s" % name)[0]
		reg.CloseKey(storageKey)
	except WindowsError:
		storageKey = reg.OpenKey(GLOBAL_STORAGE_REG_KEY[0], GLOBAL_STORAGE_REG_KEY[1], 0, reg.KEY_SET_VALUE)
		reg.SetValueEx(storageKey, "Use%s" % name, 0, reg.REG_SZ, "off")
		reg.CloseKey(storageKey)

	if bE2B == "off":
		bE2B = "on"
	else:
		bE2B = "off"

	storageKey = reg.OpenKey(GLOBAL_STORAGE_REG_KEY[0], GLOBAL_STORAGE_REG_KEY[1], 0, reg.KEY_SET_VALUE)
	reg.SetValueEx(storageKey, "Use%s" % name, 0, reg.REG_SZ, bE2B)
	reg.CloseKey(storageKey)
	CreateMenu()
    
def ForceOption(name, yesno):
	try:
		storageKey = reg.OpenKey(GLOBAL_STORAGE_REG_KEY[0], GLOBAL_STORAGE_REG_KEY[1])
		bE2B = reg.QueryValueEx(storageKey, "Use%s" % name)[0]
		reg.CloseKey(storageKey)
	except WindowsError:
		storageKey = reg.OpenKey(GLOBAL_STORAGE_REG_KEY[0], GLOBAL_STORAGE_REG_KEY[1], 0, reg.KEY_SET_VALUE)
		reg.SetValueEx(storageKey, "Use%s" % name, 0, reg.REG_SZ, "off")
		reg.CloseKey(storageKey)

	storageKey = reg.OpenKey(GLOBAL_STORAGE_REG_KEY[0], GLOBAL_STORAGE_REG_KEY[1], 0, reg.KEY_SET_VALUE)
	reg.SetValueEx(storageKey, "Use%s" % name, 0, reg.REG_SZ, yesno)
	reg.CloseKey(storageKey)
	CreateMenu()

"""
Check for updates using a seperate EXE.

"""
def CheckForUpdatesEXE():
	if QueryToggableOption("AutoUpdate"):
		try:
			p = ("%s -name %s -version %f -version_info_url %s" % (os.path.join(WORKING_DIR, "autoUpdate.exe"), "CoDMayaTools.py", FILE_VERSION, VERSION_CHECK_URL))
			subprocess.Popen(p)
		except:
			return
	else:
		return

	
#def SetGame(name):
#	currentGame = name

##########################################################
#   Ray's Animation Toolkit                              #
#                                                        #
#   Credits:                                             #
#   Aidan - teaching me how to make plugins like this :) #
##########################################################

def GenerateCamAnim(reqarg=""):
	useDefMesh = False
	if (cmds.objExists(getObjectByAlias("camera")) == False):
		print "Camera doesn't exist"
		return
	if (cmds.objExists(getObjectByAlias("weapon")) == False):
		print "Weapon doesn't exist"
		return
	animStart = cmds.playbackOptions(query=True, minTime=True)
	animEnd = cmds.playbackOptions(query=True, maxTime=True)
	jointGun = cmds.xform(getObjectByAlias("weapon"), query=True, rotation=True)
	jointGunPos = cmds.xform(getObjectByAlias("weapon"), query=True, translation=True)
	GunMoveXorig = jointGunPos[0]*-0.025
	GunRotYAddorig = jointGunPos[0]*-0.5
	GunRotXAddorig = jointGunPos[1]*-0.25
	progressW = cmds.progressWindow(minValue=animStart,maxValue=animEnd)
	for i in range(int(animStart),int(animEnd+1)):
		cmds.currentTime(i)
		jointGun = cmds.xform(getObjectByAlias("weapon"), query=True, rotation=True)
		jointGunPos = cmds.xform(getObjectByAlias("weapon"), query=True, translation=True)
		GunMoveX = jointGunPos[0]*-0.025
		GunRotYAdd = jointGunPos[0]*-0.5
		GunRotXAdd = jointGunPos[1]*-0.25
		GunRot = jointGun
		GunRot[0] = jointGun[0]
		GunRot[0] = GunRot[0] * 0.025
		GunRot[1] = jointGun[1]
		GunRot[1] = GunRot[1] * 0.025
		GunRot[2] = jointGun[2]
		GunRot[2] = GunRot[2] * 0.025
		print GunRot
		print jointGun
		cmds.select(getObjectByAlias("camera"), replace=True)
		# cmds.rotate(GunRot[0], GunRot[1], GunRot[2], rotateXYZ=True)
		cmds.setKeyframe(v=(GunMoveX-GunMoveXorig),at='translateX')
		cmds.setKeyframe(v=GunRot[0]+(GunRotXAdd-GunRotXAddorig),at='rotateX')
		cmds.setKeyframe(v=(GunRot[1]+(GunRotYAdd-GunRotYAddorig)),at='rotateY')
		cmds.setKeyframe(v=GunRot[2],at='rotateZ')
		cmds.progressWindow(edit=True,step=1)
	cmds.progressWindow(edit=True,endProgress=True)

def RemoveCameraKeys(reqarg=""):
	if (cmds.objExists(getObjectByAlias("camera")) == False):
		print "ERROR: Camera doesn't exist"
		return
	else:
		print "Camera exists!"
		jointCamera = cmds.joint(getObjectByAlias("camera"), query=True)
	animStart = cmds.playbackOptions(query=True, minTime=True)
	animEnd = cmds.playbackOptions(query=True, maxTime=True)
	cmds.select(getObjectByAlias("camera"), replace=True)
		#cmds.setAttr('tag_camera.translateX',0)
		#cmds.setAttr('tag_camera.translateY',0)
		#cmds.setAttr('tag_camera.translateZ',0)
		#cmds.setAttr('tag_camera.rotateX',0)
		#cmds.setAttr('tag_camera.rotateY',0)
		#cmds.setAttr('tag_camera.rotateZ',0)
	# cmds.rotate(GunRot[0], GunRot[1], GunRot[2], rotateXYZ=True)
	cmds.cutKey(clear=True,time=(animStart,animEnd+1))

def RemoveCameraAnimData(reqarg=""):
	if (cmds.objExists(getObjectByAlias("camera")) == False):
		print "ERROR: Camera doesn't exist"
		return
	else:
		print "Camera exists!"
		jointCamera = cmds.joint(getObjectByAlias("camera"), query=True)
	animStart = cmds.playbackOptions(query=True, animationStartTime=True)
	animEnd = cmds.playbackOptions(query=True, animationEndTime=True)
	cmds.cutKey(clear=True,time=(animStart,animEnd+1))
	cmds.select(getObjectByAlias("camera"), replace=True)
	cmds.setAttr(getObjectByAlias("camera")+'.translateX',0)
	cmds.setAttr(getObjectByAlias("camera")+'.translateY',0)
	cmds.setAttr(getObjectByAlias("camera")+'.translateZ',0)
	cmds.setAttr(getObjectByAlias("camera")+'.rotateX',0)
	cmds.setAttr(getObjectByAlias("camera")+'.rotateY',0)
	cmds.setAttr(getObjectByAlias("camera")+'.rotateZ',0)

def setObjectAlias(aname):
	if len(cmds.ls("CoDMayaTools")) == 0:
		cmds.createNode("renderLayer", name="CoDMayaTools", skipSelect=True)
	if not cmds.attributeQuery("objAlias%s" % aname, node="CoDMayaTools", exists=True):
		cmds.addAttr("CoDMayaTools", longName="objAlias%s" % aname, dataType='string')
	objects = cmds.ls(selection=True);
	if len(objects) == 1:
		print "Marking selected object as %s" % aname
	else:
		print "Selected more than 1 object or none at all"
		return
	obj = objects[0]
	cmds.setAttr("CoDMayaTools.objAlias%s" % aname, obj, type='string')

def getObjectByAlias(aname):
	if len(cmds.ls("CoDMayaTools")) == 0:
		cmds.createNode("renderLayer", name="CoDMayaTools", skipSelect=True)
	if not cmds.attributeQuery("objAlias%s" % aname, node="CoDMayaTools", exists=True):
		return ""
	return cmds.getAttr("CoDMayaTools.objAlias%s" % aname) or ""

def SetToggableOption(name="", val=0):
	if not val:
		val = int(cmds.menuItem(name, query=True, checkBox=True ))

	try:
		storageKey = reg.OpenKey(GLOBAL_STORAGE_REG_KEY[0], GLOBAL_STORAGE_REG_KEY[1], 0, reg.KEY_ALL_ACCESS)
	except WindowsError:
		storageKey = reg.CreateKey(GLOBAL_STORAGE_REG_KEY[0], GLOBAL_STORAGE_REG_KEY[1])
		storageKey = reg.OpenKey(GLOBAL_STORAGE_REG_KEY[0], GLOBAL_STORAGE_REG_KEY[1], 0, reg.KEY_ALL_ACCESS)

	reg.SetValueEx(storageKey, "Setting_%s" % name, 0, reg.REG_DWORD, val )

def QueryToggableOption(name=""):
	try:
		storageKey = reg.OpenKey(GLOBAL_STORAGE_REG_KEY[0], GLOBAL_STORAGE_REG_KEY[1], 0, reg.KEY_ALL_ACCESS)
		reg.QueryValueEx(storageKey, "Setting_%s" % name)[0]
	except WindowsError:
		storageKey = reg.OpenKey(GLOBAL_STORAGE_REG_KEY[0], GLOBAL_STORAGE_REG_KEY[1], 0, reg.KEY_ALL_ACCESS)
		try:
			reg.SetValueEx(storageKey, "Setting_%s" % name, 0, reg.REG_DWORD , 0 )
		except:
			return 1

	return reg.QueryValueEx(storageKey, "Setting_%s" % name)[0]

# ---- Create windows ----
try:
	storageKey = reg.OpenKey(GLOBAL_STORAGE_REG_KEY[0], GLOBAL_STORAGE_REG_KEY[1])
except WindowsError:
	storageKey = reg.CreateKey(GLOBAL_STORAGE_REG_KEY[0], GLOBAL_STORAGE_REG_KEY[1]) # Seems to fail because above in the bin function it tries to open the key but doesn't exist and stops there, so I heck it and added this.

try:
	storageKey = reg.OpenKey(GLOBAL_STORAGE_REG_KEY[0], GLOBAL_STORAGE_REG_KEY[1])
	codRootPath = reg.QueryValueEx(storageKey, "RootPath")[0]
	reg.CloseKey(storageKey)
except WindowsError:
	cmds.confirmDialog(message="It looks like this is your first time running CoD Maya Tools.\nYou will be asked to choose your game's root path.", button=['OK'], defaultButton='OK', title="First time configuration") #MessageBox("Please set your root path before starting to work with CoD Maya Tools")
	SetRootFolder()
	res = cmds.confirmDialog(message="Are you using Export2Bin/ExportX? (only required for Black Ops 3)", button=['Yes', 'No'], defaultButton='No', title="First time configuration")
	if res == "Yes":
		SetExport2Bin()
		SetToggableOption(name="E2B", val=1)
	else:
		SetToggableOption(name="E2B", val=0)
	res = cmds.confirmDialog(message="Enable Automatic Updates?", button=['Yes', 'No'], defaultButton='No', title="First time configuration")
	if res == "Yes":
		SetToggableOption(name="AutoUpdate", val=1)
	else:
		SetToggableOption(name="AutoUpdate", val=0)
	cmds.confirmDialog(message="You're set! You can now export models and anims to any CoD!")
	

CheckForUpdatesEXE()
CreateMenu()
CreateXAnimWindow()
CreateXModelWindow()
CreateXCamWindow()

print "CoDMayaTools initialized."
