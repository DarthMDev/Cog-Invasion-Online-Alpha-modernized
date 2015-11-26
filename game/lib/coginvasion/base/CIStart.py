"""

  Filename: CIStart.py
  Created by: blach (17June14)

"""

from panda3d.core import *
import __builtin__

import Logger
Logger.Starter()

from lib.coginvasion.manager.SettingsManager import SettingsManager
jsonfile = "settings.json"
print "CIStart: Reading settings file " + jsonfile
sm = SettingsManager()

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
from panda3d.core import *
print "CIStart: Using Panda3D version {0}".format(PandaSystem.getVersionString())

try:
    import aes
    import niraidata
    # Config
    prc = niraidata.CONFIG
    iv, key, prc = prc[:16], prc[16:32], prc[32:]
    prc = aes.decrypt(prc, key, iv)
    for line in prc.split('\n'):
        line = line.strip()
        if line:
            loadPrcFileData('coginvasion config', line)
    print "CIStart: Running production"
except:
    loadPrcFile('config/Confauto.prc')
    loadPrcFile('config/config_client.prc')
    print "CIStart: Running dev"

sm.maybeFixAA()

from direct.showbase.ShowBaseWide import ShowBase
base = ShowBase()
base.cTrav = CollisionTraverser()

if base.config.GetString('load-display') == 'pandagl':
    print "CIStart: Using OpenGL graphics library."
elif base.config.GetString('load-display') == 'pandadx9':
    print "CIStart: Using DirectX 9 graphics library."
else:
    print "CIStart: Using an unknown graphics library."

if base.config.GetString('audio-library-name') == 'p3miles_audio':
    print "CIStart: Using Miles audio library."
elif base.config.GetString('audio-library-name') == 'p3fmod_audio':
    print "CIStart: Using FMOD audio library."
elif base.config.GetString('audio-library-name') == 'p3openal_audio':
    print "CIStart: Using OpenAL audio library."

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
sm.applySettings(jsonfile)
if base.win == None:
    print "CIStart: Unable to open window; aborting."
    sys.exit()
else:
    print "CIStart: Successfully opened window."
ConfigVariableDouble('decompressor-step-time').setValue(0.01)
ConfigVariableDouble('extractor-step-time').setValue(0.01)

DirectGuiGlobals.setDefaultFontFunc(CIGlobals.getToonFont)
DirectGuiGlobals.setDefaultFont(CIGlobals.getToonFont())
DirectGuiGlobals.setDefaultRolloverSound(loader.loadSfx("phase_3/audio/sfx/GUI_rollover.mp3"))
DirectGuiGlobals.setDefaultClickSound(loader.loadSfx("phase_3/audio/sfx/GUI_create_toon_fwd.mp3"))
DirectGuiGlobals.setDefaultDialogGeom(loader.loadModel("phase_3/models/gui/dialog_box_gui.bam"))

from lib.coginvasion.nametag import NametagGlobals
from lib.coginvasion.margins.MarginManager import MarginManager
from lib.coginvasion.margins import MarginGlobals

NametagGlobals.setMe(base.cam)
NametagGlobals.setCardModel('phase_3/models/props/panel.bam')
NametagGlobals.setArrowModel('phase_3/models/props/arrow.bam')
NametagGlobals.setChatBalloon3dModel('phase_3/models/props/chatbox.bam')
NametagGlobals.setChatBalloon2dModel('phase_3/models/props/chatbox_noarrow.bam')
NametagGlobals.setThoughtBalloonModel('phase_3/models/props/chatbox_thought_cutout.bam')
chatButtonGui = loader.loadModel('phase_3/models/gui/chat_button_gui.bam')
NametagGlobals.setPageButton(chatButtonGui.find('**/Horiz_Arrow_UP'), chatButtonGui.find('**/Horiz_Arrow_DN'),
                             chatButtonGui.find('**/Horiz_Arrow_Rllvr'), chatButtonGui.find('**/Horiz_Arrow_UP'))
NametagGlobals.setQuitButton(chatButtonGui.find('**/CloseBtn_UP'), chatButtonGui.find('**/CloseBtn_DN'),
                             chatButtonGui.find('**/CloseBtn_Rllvr'), chatButtonGui.find('**/CloseBtn_UP'))
soundRlvr = DirectGuiGlobals.getDefaultRolloverSound()
NametagGlobals.setRolloverSound(soundRlvr)
soundClick = DirectGuiGlobals.getDefaultClickSound()
NametagGlobals.setClickSound(soundClick)

base.marginManager = MarginManager()
base.margins = aspect2d.attachNewNode(base.marginManager, DirectGuiGlobals.MIDGROUND_SORT_INDEX + 1)
base.leftCells = [
    base.marginManager.addCell(0.1, -0.6, base.a2dTopLeft),
    base.marginManager.addCell(0.1, -1.0, base.a2dTopLeft),
    base.marginManager.addCell(0.1, -1.4, base.a2dTopLeft)
]
base.bottomCells = [
    base.marginManager.addCell(0.4, 0.1, base.a2dBottomCenter),
    base.marginManager.addCell(-0.4, 0.1, base.a2dBottomCenter),
    base.marginManager.addCell(-1.0, 0.1, base.a2dBottomCenter),
    base.marginManager.addCell(1.0, 0.1, base.a2dBottomCenter)
]
base.rightCells = [
    base.marginManager.addCell(-0.1, -0.6, base.a2dTopRight),
    base.marginManager.addCell(-0.1, -1.0, base.a2dTopRight),
    base.marginManager.addCell(-0.1, -1.4, base.a2dTopRight)
]

# HACK: I don't feel like making a new file that inherits from ShowBase so I'm just going to do this...
def setCellsActive(cells, active):
    for cell in cells:
        cell.setActive(active)
    base.marginManager.reorganize()
base.setCellsActive = setCellsActive

def windowEvent(win):
    ShowBase.windowEvent(base, win)
    base.marginManager.updateMarginVisibles()
base.windowEvent = windowEvent

def maybeDoSomethingWithMusic(condition):
    # 0 = paused
    # 1 = restarted
    width, height, fs, music, sfx, tex_detail, model_detail, aa, af = sm.getSettings(jsonfile)
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
music = base.loadMusic(CIGlobals.getThemeSong())
base.playMusic(music, looping = 1, volume = 0.75)
il.load()

base.run()
