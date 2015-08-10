from panda3d.core import *
loadPrcFile('config/config_client.prc')
loadPrcFileData('', 'framebuffer-multisample 1')
loadPrcFileData('', 'multisamples 2048')
loadPrcFileData('', 'tk-main-loop 0')
#loadPrcFileData('', 'notify-level debug')
loadPrcFileData('', 'audio-library-name p3fmod_audio')
from direct.showbase.ShowBaseWide import ShowBase
base = ShowBase()
from direct.gui.DirectGui import *
from direct.actor.Actor import Actor
from direct.particles.ParticleEffect import ParticleEffect
from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.suit.Suit import Suit
from direct.interval.IntervalGlobal import *
from lib.coginvasion.suit.DistributedSuit import DistributedSuit
from direct.distributed.ClientRepository import ClientRepository
from lib.coginvasion.toon.Toon import Toon
from lib.coginvasion.toon import NameTag, ToonDNA, ToonHead
from direct.directutil import Mopath
from direct.showbase.Audio3DManager import Audio3DManager
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
"""
"""
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
"""
dna = ToonDNA.ToonDNA()
dna.parseDNAStrand(dna.dnaStrand)

head = ToonHead.ToonHead(base.cr)
head.generateHead(dna.gender, dna.animal, dna.head, 1)
head.getGeomNode().setDepthWrite(1)
head.getGeomNode().setDepthTest(1)
head.setH(180)
head.setScale(0.7)
#head.reparentTo(aspect2d)


from lib.coginvasion.base.SectionedSound import AudioClip

nextClip = None
testClip = None

def handlePartDone():
	global nextClip
	global testClip
	if nextClip:
		testClip.cleanup()
		testClip = AudioClip(1, nextClip)
		testClip.makeData()
		testClip.playAllParts()
	nextClip = None


testClip = AudioClip(1, "5050_orchestra")
testClip.makeData()
testClip.playAllParts()

def setNextClip(clip):
	global nextClip
	nextClip = clip

base.accept('AudioClip_partDone', handlePartDone)
base.accept('l', setNextClip, ['located_orchestra'])
"""

suit = DistributedSuit(base.cr)
suit.doId = 0
suit.generate()
suit.announceGenerate()
suit.setSuit("A", "mrhollywood", "s", 0)
suit.reparentTo(render)
suit.animFSM.request('die')

base.camLens.setMinFov(CIGlobals.DefaultCameraFov / (4./3.))

#base.oobe()
base.run()
