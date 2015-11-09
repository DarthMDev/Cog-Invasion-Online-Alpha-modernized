"""

  Filename: Standalone.py
  Created by: DecodedLogic (07Nov15)
  This is so you can use client objects in a stand-alone program easily.
  
"""

from direct.distributed.ClientRepository import ClientRepository
from panda3d.core import CollisionTraverser, AntialiasAttrib, loadPrcFile, loadPrcFileData
from panda3d.core import CullBinManager
import __builtin__

from lib.coginvasion.toon.LocalToon import LocalToon
from lib.coginvasion.login.AvChoice import AvChoice

loadPrcFile('config/config_client.prc')
loadPrcFileData('', 'framebuffer-multisample 0')
loadPrcFileData('', 'multisamples 16')
loadPrcFileData('', 'tk-main-loop 0')
loadPrcFileData('', 'egg-load-old-curves 0')

cbm = CullBinManager.getGlobalPtr()
cbm.addBin('ground', CullBinManager.BTUnsorted, 18)
cbm.addBin('shadow', CullBinManager.BTBackToFront, 19)
cbm.addBin('gui-popup', CullBinManager.BTUnsorted, 60)

class Standalone:
    
    def __init__(self):
        self.process = 'client'
        __builtin__.game = self
        
        base.cr = ClientRepository(['phase_3/etc/direct.dc', 'phase_3/etc/toon.dc'])
        base.cr.isShowingPlayerIds = None
        base.shadowTrav = CollisionTraverser()
        base.cTrav = CollisionTraverser()
        
        # Let's enable particles.
        base.enableParticles()
        
        # Let's set our AntialiasAttrib level.
        render.setAntialias(AntialiasAttrib.MMultisample)
        
    def startAvatar(self, dnaStrand, name, health):
        # Let's set the DNA Strand.
        base.cr.localAvChoice = AvChoice(dnaStrand, name, 0, 0)
        
        # Let's start the avatar.
        dclass = base.cr.dclassesByName['DistributedToon']
        base.localAvatar = LocalToon(base.cr)
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
        
    def hasAvatar(self):
        return hasattr(base, 'localAvatar')