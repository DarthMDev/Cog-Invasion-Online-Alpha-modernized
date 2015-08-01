"""

  Filename: CIStart.py
  Created by: blach (17June14)

"""

from pandac.PandaModules import *
import __builtin__

import Logger
Logger.Starter()

from lib.coginvasion.manager.SettingsManager import SettingsManager
jsonfile = "settings.json"
print "CIStart: Reading settings file " + jsonfile

import os
class game:
	name = 'coginvasion'
	process = 'client'
	version = os.environ.get("GAME_VERSION")
	serverAddress = os.environ.get("GAME_SERVER")


__builtin__.game = game()
import time
import os
import sys
import random

import __builtin__

print "CIStart: Starting the game."
from pandac.PandaModules import *
print "CIStart: Using Panda3D version {0}".format(PandaSystem.getVersionString())
loadPrcFile("config/Confauto.prc")
loadPrcFile("config/config_client.prc")
print ConfigPageManager.getGlobalPtr()
from direct.showbase.ShowBaseWide import ShowBase
base = ShowBase()
if base.config.GetString('audio-library-name') == 'p3miles_audio':
	print "CIStart: Using RAD Game Tools, Miles Sound System."
elif base.config.GetString('audio-library-name') == 'p3fmod_audio':
	print "CIStart: Using FMOD audio library."
elif base.config.GetString('audio-library-name') == 'p3openal_audio':
	print "CIStart: Using OpenAL audio library."
else:
	print "CIStart: Using no or an unknown audio library."
from direct.gui import DirectGuiGlobals
from direct.gui.DirectGui import *
from direct.filter.CommonFilters import CommonFilters

vfs = VirtualFileSystem.getGlobalPtr()
vfs.mount(Filename("phase_0.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_3.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_3.5.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_4.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_5.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_5.5.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_6.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_7.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_8.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_9.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_10.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_11.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_12.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_13.mf"), ".", VirtualFileSystem.MFReadOnly)

import CogInvasionLoader
base.loader = CogInvasionLoader.CogInvasionLoader(base)
base.graphicsEngine.setDefaultLoader(base.loader.loader)
__builtin__.loader = base.loader
from lib.coginvasion.globals import CIGlobals
cbm = CullBinManager.getGlobalPtr()
cbm.addBin('ground', CullBinManager.BTUnsorted, 18)
cbm.addBin('shadow', CullBinManager.BTBackToFront, 19)
cbm.addBin('gui-popup', CullBinManager.BTUnsorted, 60)
base.setBackgroundColor(CIGlobals.DefaultBackgroundColor)
base.disableMouse()
base.enableParticles()
base.camLens.setNearFar(CIGlobals.DefaultCameraNear, CIGlobals.DefaultCameraFar)
base.transitions.IrisModelName = "phase_3/models/misc/iris.bam"
base.transitions.FadeModelName = "phase_3/models/misc/fade.bam"
base.setFrameRateMeter(False)
base.accept('f9', base.screenshot, ['screenshots/screenshot'])
from direct.filter.CommonFilters import CommonFilters
print "CIStart: Setting display preferences..."
SettingsManager().applySettings(jsonfile)
if base.win == None:
	print "CIStart: Unable to open window; aborting."
	sys.exit()
else:
	print "CIStart: Successfully opened window."
ConfigVariableDouble('decompressor-step-time').setValue(0.01)
ConfigVariableDouble('extractor-step-time').setValue(0.01)

print "CIStart: Setting default font..."
DirectGuiGlobals.setDefaultFontFunc(CIGlobals.getToonFont)
DirectGuiGlobals.setDefaultFont(CIGlobals.getToonFont())
print "CIStart: Setting default GUI sounds..."
DirectGuiGlobals.setDefaultRolloverSound(loader.loadSfx("phase_3/audio/sfx/GUI_rollover.mp3"))
DirectGuiGlobals.setDefaultClickSound(loader.loadSfx("phase_3/audio/sfx/GUI_create_toon_fwd.mp3"))
print "CIStart: Setting default Dialog geometry..."
DirectGuiGlobals.setDefaultDialogGeom(loader.loadModel("phase_3/models/gui/dialog_box_gui.bam"))

def maybeDoSomethingWithMusic(condition):
	# 0 = paused
	# 1 = restarted
	width, height, fs, music, sfx, tex_detail, model_detail, aa, af = SettingsManager().getSettings(jsonfile)
	if condition == 0:
		if music == True:
			base.enableMusic(False)
	elif condition == 1:
		if music == True:
			base.enableMusic(True)

base.accept("PandaPaused", maybeDoSomethingWithMusic, [0])
base.accept("PandaRestarted", maybeDoSomethingWithMusic, [1])

def doneInitLoad():
	print "CIStart: Initial game load finished."
	from lib.coginvasion.distributed import CogInvasionClientRepository
	base.cr = CogInvasionClientRepository.CogInvasionClientRepository(music, "ver-" + game.version)

print "CIStart: Starting initial game load..."
from InitialLoad import InitialLoad
il = InitialLoad(doneInitLoad)
music = base.loadMusic(CIGlobals.ThemeSong)
base.playMusic(music, looping = 1, volume = 0.75)
il.load()


base.run()
