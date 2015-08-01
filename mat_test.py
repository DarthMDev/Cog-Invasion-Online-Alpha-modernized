from pandac.PandaModules import *
loadPrcFile('config/config_client.prc')
from direct.showbase.ShowBaseWide import ShowBase
base = ShowBase()
from direct.distributed.ClientRepository import ClientRepository
from direct.interval.IntervalGlobal import *

vfs = VirtualFileSystem.getGlobalPtr()
vfs.mount(Filename("phase_0.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_3.mf"), ".", VirtualFileSystem.MFReadOnly)
vfs.mount(Filename("phase_3.5.mf"), ".", VirtualFileSystem.MFReadOnly)
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

import __builtin__

class game:
	process = 'client'
__builtin__.game = game

from lib.toontown.makeatoon.MakeAToon import MakeAToon
from lib.toontown.toon.Toon import Toon

base.cr = ClientRepository(['astron/direct.dc'])
base.cr.isShowingPlayerIds = False
base.cTrav = CollisionTraverser()

base.camLens.setMinFov(70.0 / (4./3.))

from direct.actor.Actor import Actor

dgmRoot = camera.attachNewNode('root')

dgm = Actor("phase_4/models/minigames/v_dgm.egg", {"sgunidle": "phase_4/models/minigames/v_dgm-shotgun-idle.egg",
	"sgunshoot": "phase_4/models/minigames/v_dgm-shotgun-shoot.egg",
	"sgundraw": "phase_4/models/minigames/v_dgm-shotgun-draw.egg"})
dgm.reparentTo(dgmRoot)
dgm.loop("sgunidle")
dgm.setDepthWrite(True)
dgm.setDepthTest(True)

drawSfx = base.loadSfx("phase_4/audio/sfx/draw_primary.wav")
shootSfx = base.loadSfx("phase_4/audio/sfx/shotgun_shoot.wav")
shootSfx.setVolume(0.5)
cockBack = base.loadSfx("phase_4/audio/sfx/shotgun_cock_back.wav")
cockFwd = base.loadSfx("phase_4/audio/sfx/shotgun_cock_forward.wav")

Sequence(
	Func(base.playSfx, drawSfx),
	LerpQuatInterval(dgm, duration = 0.5, quat = (0, 0, 0), startHpr = (70, -50, 0), blendType = 'easeOut'),
	Wait(3.0),
	Func(base.playSfx, shootSfx),
	ActorInterval(dgm, "sgunshoot", playRate = 1),
	Func(dgm.loop, "sgunidle"),
	Wait(1.0),
	Func(base.playSfx, shootSfx),
	ActorInterval(dgm, "sgunshoot", playRate = 1),
	Func(dgm.loop, "sgunidle"),
	Wait(5.0),
	Func(base.playSfx, shootSfx),
	ActorInterval(dgm, "sgunshoot", playRate = 1),
	Wait(0.1),
	Func(base.playSfx, shootSfx),
	ActorInterval(dgm, "sgunshoot", playRate = 1),
	Wait(0.1),
	Func(base.playSfx, shootSfx),
	ActorInterval(dgm, "sgunshoot", playRate = 1),
	Func(dgm.loop, "sgunidle"),
	Wait(2.0),
	Func(drawSfx.play),
	LerpQuatInterval(dgm, duration = 0.5, quat = (70, -50, 0), startHpr = (0, 0, 0), blendType = 'easeIn'),
	SoundInterval(cockBack),
	SoundInterval(cockFwd),
)


from lib.toontown.npc import NPCGlobals

toon = Toon(base.cr)
toon.setDNAStrand(NPCGlobals.NPC_DNA["Flippy"])
toon.generateToon()
toon.reparentTo(render)
toon.loop("squirt")
shotgun = loader.loadModel("shotgun.egg")
shotgun.setScale(0.75)
shotgun.setPos(-0.5, -0.2, 0.19)
shotgun.setHpr(350, 272.05, 0)
#shotgun.reparentTo(dgm.exposeJoint(None, "modelRoot", "Bone.029"))
#shotgun.setColorScale(0.25, 0.25, 1, 1)
shotgun.reparentTo(toon.find('**/def_joint_right_hold'))
#shotgun.place()

#base.disableMouse()

#dgmRoot.setPos(-0.42, -0.81, -1.77)
#dgmRoot.setHpr(355, 352.87, 0.00)

#dgmRoot.place()

base.camLens.setNear(0.1)

#base.oobe()

base.run()
