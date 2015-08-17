# Filename: StandaloneToon.py
# Created by:  blach (02May15)

from panda3d.core import *
loadPrcFile('config/config_client.prc')
loadPrcFileData('', 'frambuffer-multisample 1')
loadPrcFileData('', 'multisamples 16')
loadPrcFileData('', 'tk-main-loop 0')
loadPrcFileData('', 'egg-load-old-curves 0')

from direct.showbase.ShowBaseWide import ShowBase
base = ShowBase()
from direct.showbase.Audio3DManager import Audio3DManager
base.audio3d = Audio3DManager(base.sfxManagerList[0], camera)
base.audio3d.setDistanceFactor(25)
base.audio3d.setDropOffFactor(0.025)
from direct.distributed.ClientRepository import ClientRepository

import __builtin__
class game:
	process = 'client'
__builtin__.game = game()

from lib.coginvasion.toon import LocalToon
from lib.coginvasion.login.AvChoice import AvChoice

base.cTrav = CollisionTraverser()
base.shadowTrav = CollisionTraverser()
base.cr = ClientRepository(['phase_3/etc/direct.dc', 'phase_3/etc/toon.dc'])
base.cr.isShowingPlayerIds = False
base.cr.localAvChoice = AvChoice("00/08/00/10/01/12/01/10/18/18/07/00/00/00/00", "Ducky", 0, 0)

dclass = base.cr.dclassesByName['DistributedToon']
base.localAvatar = LocalToon.LocalToon(base.cr)
base.localAvatar.dclass = dclass
base.localAvatar.doId = base.cr.localAvChoice.getAvId()
base.localAvatar.generate()
base.localAvatar.setName(base.cr.localAvChoice.getName())
base.localAvatar.maxHealth = 137
base.localAvatar.health = 137
base.localAvatar.setDNAStrand(base.cr.localAvChoice.getDNA())
base.localAvatar.announceGenerate()
base.localAvatar.reparentTo(base.render)
base.localAvatar.enableAvatarControls()

base.enableParticles()

render.setAntialias(AntialiasAttrib.MMultisample)
