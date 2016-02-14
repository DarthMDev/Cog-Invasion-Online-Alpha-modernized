from panda3d.core import *
loadPrcFile('config/config_client.prc')
loadPrcFileData('', 'framebuffer-multisample 1')
loadPrcFileData('', 'multisamples 2048')
loadPrcFileData('', 'tk-main-loop 0')
#loadPrcFileData('', 'notify-level debug')
loadPrcFileData('', 'audio-library-name p3fmod_audio')
loadPrcFileData('', 'egg-load-old-curves 0')
#loadPrcFileData('', 'interpolate-frames 1')
from direct.showbase.ShowBaseWide import ShowBase
base = ShowBase()
from direct.gui.DirectGui import *
from direct.actor.Actor import Actor
from direct.particles.ParticleEffect import ParticleEffect
from lib.coginvasion.globals import CIGlobals
from direct.interval.IntervalGlobal import *
from direct.distributed.ClientRepository import ClientRepository
from lib.coginvasion.toon.Toon import Toon
from lib.coginvasion.toon import NameTag, ToonDNA, ToonHead
from direct.directutil import Mopath
from direct.showbase.Audio3DManager import Audio3DManager
from direct.showutil.Rope import Rope
import glob

base.enableParticles()

base.cr = ClientRepository([])
base.cr.isShowingPlayerIds = False
base.audio3d = Audio3DManager(base.sfxManagerList[0], camera)

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

base.cTrav = CollisionTraverser()
base.shadowTrav = CollisionTraverser()
"""
tunnel = loader.loadModel("safe_zone_entrance_tunnel_TT.bam")
tunnel.reparentTo(render)

toon = Toon(base.cr)
toon.setDNAStrand("00/00/00/00/00/00/00/00/00/00/00/00/00/00/00")
toon.generateToon()
toon.reparentTo(render)

smiley = loader.loadModel('models/smiley.egg.pz')
smiley.reparentTo(render)
smiley.setX(45)
smiley.setY(5)
smiley.setZ(0)

toon.setPos(-15, -5, 0)
toon.setHpr(180, 0, 0)
toon.reparentTo(smiley)
toon.animFSM.request('run')

smiley.setHpr(-90, 0, 0)

ival = Sequence(LerpPosInterval(smiley, duration = 1.0, pos = (35, 5, 0), startPos = (45, 5, 0)), LerpHprInterval(smiley, duration = 2.0, hpr = (0, 0, 0), startHpr = (-90, 0, 0)))
Sequence(Wait(3.0), Func(ival.start)).start()


torsoType2flagY = {"dgs_shorts": -1.5, "dgs_skirt": -1.5, "dgm_shorts": -1.1, "dgm_skirt": -1.1, "dgl_shorts": -1.1, "dgl_skirt": -1.1}

flag = loader.loadModel('phase_4/models/minigames/flag.egg')
flag.find('**/flag').setTwoSided(1)
flag.find('**/flag_pole').setColor(0.1, 0.1, 0.1, 1.0)
flag.find('**/flag').setColor(1, 0, 0, 1.0)
flag.reparentTo(render)

anim = 'neutral'

toon = Toon(base.cr)
toon.parseDNAStrand("00/01/04/17/01/17/01/17/03/03/09/09/09/04/00")
toon.generateToon()
toon.reparentTo(render)
toon.animFSM.request(anim)
toon.setX(-5)

flag.reparentTo(toon.find('**/def_joint_attachFlower'))
flag.setPos(0.2, torsoType2flagY[toon.torso], -1)

flag2 = loader.loadModel('phase_4/models/minigames/flag.egg')
flag2.find('**/flag').setTwoSided(1)
flag2.find('**/flag_pole').setColor(0.1, 0.1, 0.1, 1.0)
flag2.find('**/flag').setColor(0, 0, 1, 1.0)
flag2.reparentTo(render)

toon2 = Toon(base.cr)
toon2.parseDNAStrand("00/01/04/17/00/17/01/17/03/03/09/09/09/04/00")
toon2.generateToon()
toon2.reparentTo(render)
toon2.animFSM.request(anim)
toon2.setX(0)

flag2.reparentTo(toon2.find('**/def_joint_attachFlower'))
flag2.setPos(0.2, torsoType2flagY[toon2.torso], -1)

flag3 = loader.loadModel('phase_4/models/minigames/flag.egg')
flag3.find('**/flag').setTwoSided(1)
flag3.find('**/flag_pole').setColor(0.1, 0.1, 0.1, 1.0)
flag3.find('**/flag').setColor(0, 0, 1, 1.0)
flag3.reparentTo(render)

toon3 = Toon(base.cr)
toon3.parseDNAStrand("00/01/04/17/02/17/01/17/03/03/09/09/09/04/00")
toon3.generateToon()
toon3.reparentTo(render)
toon3.animFSM.request(anim)
toon3.setX(5)

flag3.reparentTo(toon3.find('**/def_joint_attachFlower'))
flag3.setPos(0.2, torsoType2flagY[toon3.torso], -1)
"""

base.camLens.setMinFov(CIGlobals.DefaultCameraFov / (4./3.))
	

smiley = loader.loadModel('models/smiley.egg.pz')
#smiley.reparentTo(render)

arrow = loader.loadModel('phase_3/models/props/arrow.bam')
arrow.reparentTo(aspect2d)
arrow.setScale(0.1)
arrow.setZ(-0.7)

import math

def update(task):
	bLocation = smiley.getPos(base.cam)
	bRotation = base.cam.getQuat(base.cam)
	bCamSpacePos = bRotation.xform(bLocation)
	bArrowRadians = math.atan2(bCamSpacePos[0], bCamSpacePos[1])
	bArrowDegrees = (bArrowRadians/math.pi) * 180
	arrow.setR(bArrowDegrees - 90)
	
	return task.cont
	
taskMgr.add(update, 'u')

render.setAntialias(AntialiasAttrib.MMultisample)

toon = Toon(base.cr)
toon.setDNAStrand("00/03/00/00/02/00/02/00/00/00/00/00/00/00/00")
toon.generateToon()
toon.reparentTo(render)
neutral = 0.6
run = 0.4
#toon.enableBlend()
#toon.setControlEffect('shout', neutral)
#toon.setControlEffect('run', run)
#toon.loop('shout')
#toon.loop('run')

#toon.enableBlend()
#toon.setControlEffect('toss', 0.4)
#toon.setControlEffect('run', 0.6)

toon.setBlend(frameBlend = False)

joints = ["forSleeveL", "forSleeveR", "endarmL", "endarmR", "Rh_wrist", "Lh_wrist",
								"midsleeveL", "midsleeveR", "scale_jnt20_1", "scale_jnt23_1", "jnt7_3", "jnt7_4",
								"jnt20_2", "jnt23_2", "joint_theNeck", "joint_head", "joint_Lhold", "joint_Rhold"]

toon.listJoints('torso')

#toon.makeSubpart("torso-shorts", ["Lpant_Top", "Rpant_Top"], parent = "torso")
#toon.makeSubpart("torso-body", ["Body1a"],
#				["Lpant_Top", "Rpant_Top"], parent = "torso")
toon.loop('run')
#toon.loop('run', partName = 'torso-shorts')
#toon.loop('pie', partName = 'torso', fromFrame = 63)

def blendTask(task):
	global neutral
	global run
	print run
	if run <= 0.0:
		toon.setControlEffect('neutral', 1.0)
		toon.setControlEffect('run', 0.0)
		return task.done
	if str(run) == "0.1":
		run = 0.0
	else:
		run -= 0.1
	neutral += 0.1
	toon.setControlEffect('neutral', neutral)
	toon.setControlEffect('run', run)
	task.delayTime = 0.05
	return task.again

#taskMgr.doMethodLater(1.0, blendTask, "blend")

#base.disableMouse()
camera.setPos(0, -10, 3)


#base.oobe()
base.run()
