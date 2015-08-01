from panda3d.core import *
loadPrcFile('config/config_client.prc')
from direct.showbase.ShowBaseWide import ShowBase
base = ShowBase()
from direct.gui.DirectGui import *
from lib.coginvasion.gui.Dialog import GlobalDialog
from direct.distributed.ClientRepository import ClientRepository
from lib.coginvasion.suit.DistributedSuit import DistributedSuit
from direct.interval.IntervalGlobal import *
from lib.coginvasion.toon import ParticleLoader
from lib.coginvasion.suit.VicePresident import VicePresident

class game:
	process = 'client'
import __builtin__
__builtin__.game = game()

from lib.coginvasion.toon import Toon
from direct.gui.DirectGui import *

base.cr = ClientRepository([])
base.cTrav = CollisionTraverser()

base.cr.isShowingPlayerIds = False

base.enableParticles()

#base.disableMouse()



vfs = VirtualFileSystem.getGlobalPtr()
vfs.mount(Filename("phase_0.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_3.mf"), ".", VirtualFileSystem.MFReadOnly)
box = loader.loadModel("phase_3/models/gui/dialog_box_gui.bam")
font = loader.loadFont("phase_3/models/fonts/ImpressBT.ttf")
"""
base.transitions.fadeScreen(0.5)

gui = OnscreenImage(image = box, color = (1, 1, 0.75, 1), scale = (1.9, 1.4, 1.4))

waiting_lbl = OnscreenText(text = "Final Scores", pos = (0, 0.5, 0), font = font, scale = (0.12))

names_lbl = OnscreenText(text = "Little Doggy:\nMax:\nA Slow Turtle:\nToon 1:\nToon 2:\nToon 3:\nMr. Toon:\nMrs. Toon:", scale = 0.095, pos = (-0.85, 0.3, 0), font = font, align = TextNode.ALeft)
points_lbl = OnscreenText(text = "25 Points\n23 Points\n10 Points\n9 Points\n8 Points\n7 Points\n6 Points\n6 Points", scale = 0.095, pos = (0.85, 0.3, 0), font = font, align = TextNode.ARight)
"""
suit = DistributedSuit(base.cr)
suit.doId = 0
suit.generate()
suit.announceGenerate()
suit.generateSuit("B", "movershaker", "s", 123, 0)
suit.reparentTo(render)
suit.setH(180)
suit.animFSM.request("attack", ["canned"])

base.camLens.setMinFov(70.0 / (4./3.))

sfx = base.loadMusic("phase_7/audio/bgm/encntr_suit_winning_indoor.mid")
base.playMusic(sfx, looping = 1)
"""
toon = Toon.Toon(base.cr)
toon.setDNAStrand("00/00/00/00/00/00/00/00/00/00/00/00/00/00/00")
toon.generateToon()
toon.reparentTo(render)
toon.animFSM.request('neutral')

base.camera.reparentTo(toon)
base.camera.setPos(0, 7, 3)
base.camera.setH(180)
"""
#vp = VicePresident()
#vp.generate()
#vp.reparentTo(render)
#vp.fsm.request('emerge', [])
#Sequence(Wait(2.0), Func(vp.fsm.request, 'knockDown')).start()
#Sequence(Wait(2.0),
#	Func(vp.fsm.request, 'throwGear', [Point3(-30, -70, -50)]),
#	Wait(4.5), Func(vp.fsm.request, 'jump'),
#	Wait(5.0), Func(vp.fsm.request, 'knockDown'),
#	Wait(7.0),
#	Func(vp.fsm.request, 'riseUp'),
#	Wait(4.5)).loop()
"""

maze = loader.loadModel("models/camera.egg.pz")
maze.reparentTo(render)
maze.setZ(5)
maze.ls()
maze.find('**/o2').setSx(5)


shine = loader.loadModel("phase_4/models/minigames/shine.egg")
shine.reparentTo(maze)
shine.setPos(-0.43, 0.28, 0.63)
shine.setHpr(180.00, 0.00, 0.00)
shine.setTwoSided(1)
#shine.setScale(5.0)

flashSfx = base.loadSfx("phase_4/audio/sfx/Photo_shutter.mp3")

flash = Sequence(
	Func(base.playSfx, flashSfx),
	LerpScaleInterval(
		shine,
		duration = 0.2,
		scale = 25.0,
		startScale = 0.0
	),
	LerpScaleInterval(
		shine,
		duration = 0.05,
		scale = 0.0,
		startScale = 25.0
	)
)
Sequence(Wait(1.0), Func(flash.start)).loop()
"""
#focus = loader.loadModel("phase_4/models/minigames/photo_game_viewfinder.bam")
#focus.reparentTo(aspect2d)
#focus.setColorScale(0.25, 1, 0.25, 1)

#maze = loader.loadModel("maze_1player.egg")
#maze.find('**/maze_walls').setSz(1.5)
#maze.reparentTo(render)
#maze.ls()

#camTex = Texture('sometex')

#texBuffer = base.win.makeTextureBuffer("viewfinder_buffer", 650, 470, camTex, to_ram = True)
#texCam = base.makeCamera(texBuffer)
#texCam.reparentTo(camera)
#texCam.setPos(0.2, 0, 0.2)
#lens = PerspectiveLens()
#lens.setAspectRatio(1/1)
#texCam.node().setLens(lens)
#texCam.node().setCameraMask(BitMask32.bit(1))

def makePic():
	base.screenshot(source = texBuffer.getTexture())
	#OnscreenImage(tex, scale = 0.7)

#base.acceptOnce("m", makePic)



#mml.setPos(-0.16, 0.130005, 0)
#mml.setHpr(0, 0, 0)

#camera.place()

#sfx = base.loadSfx("phase_3.5/audio/sfx/SA_hangup.mp3")
#Sequence(Wait(1.0), Func(base.playSfx, sfx), Wait(2.1), Func(sfx.stop)).start()

#base.oobe()
base.run()
