from panda3d.core import *
loadPrcFile('config/config_client.prc')
loadPrcFileData('', 'framebuffer-multisample 1')
loadPrcFileData('', 'multisamples 2048')
loadPrcFileData('', 'tk-main-loop 0')
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
from lib.coginvasion.toon import NameTag
from direct.directutil import Mopath

base.enableParticles()

base.cr = ClientRepository([])
base.cr.isShowingPlayerIds = False

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

tag = NameTag.NameTag("Ducky")
tag.reparentTo(render)
tag.show()

base.camLens.setMinFov(CIGlobals.DefaultCameraFov / (4./3.))

#base.oobe()
base.run()

