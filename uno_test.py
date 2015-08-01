from panda3d.core import *
loadPrcFile('/c/Users/Brian/Documents/panda3d/Panda3D-CI/etc/Confauto.prc')
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

jj = Toon(base.cr)
jj.setDNAStrand("00/07/03/07/01/07/01/07/09/09/01/03/03/05/00")
jj.generateToon()
jj.reparentTo(render)
jj.setName('JJ')
jj.setupNameTag()


#base.oobe()
base.run()
