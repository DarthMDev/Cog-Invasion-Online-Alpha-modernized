"""

  Filename: DistributedGagShop.py
  Created by: blach (20Dec14)

"""

from pandac.PandaModules import CollisionNode, CollisionSphere, NodePath
from direct.distributed.DistributedNode import DistributedNode
from direct.actor.Actor import Actor
from lib.coginvasion.gui.GagShop import GagShop
from lib.coginvasion.npc.Char import Char
from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.hood.DistributedShop import DistributedShop

class DistributedGagShop(DistributedShop):
    
    def __init__(self, cr):
        try:
            self.DistributedGagShop_initialized
            return
        except:
            self.DistributedGagShop_initialized = 1
        DistributedShop.__init__(self, cr)
        self.gagShopStateData = GagShop(self, 'gagShopDone')
        self.clerk = None
        self.barrel = None
        self.gagsInBarrel = None
        return
        
    def enterAccepted(self):
        if not self.inShop:
            self.acceptOnce(self.gagShopStateData.doneEvent, self.handleGagShopDone)
            self.gagShopStateData.load()
            self.gagShopStateData.enter()
            self.inShop = True
        
    def handleGagShopDone(self):
        self.gagShopStateData.exit()
        self.gagShopStateData.unload()
        self.d_requestExit()
        
    def setupClerk(self):
        self.clerk = Char()
        self.clerk.generateChar(CIGlobals.Goofy)
        self.clerk.reparentTo(self)
        self.clerk.setName(CIGlobals.Goofy)
        self.clerk.setupNameTag()
        self.clerk.animFSM.request('neutral')
        self.barrel = loader.loadModel("phase_5.5/models/estate/wheelbarrel.bam")
        self.barrel.find('**/dirt').remove_node()
        self.barrel.reparent_to(self)
        self.barrel.set_x(-3.5)
        self.barrel.set_h(90)
        tart1 = loader.loadModel("phase_3.5/models/props/tart.bam")
        tart1.reparent_to(self.barrel)
        tart1.set_scale(0.6)
        tart1.set_pos(0, 0.65, 1)
        tart1.set_p(30.26)
        tart2 = loader.loadModel("phase_3.5/models/props/tart.bam")
        tart2.reparent_to(self.barrel)
        tart2.set_scale(0.6)
        tart2.set_z(1.14)
        slice1 = loader.loadModel("phase_5/models/props/cream-pie-slice.bam")
        slice1.reparent_to(self.barrel)
        slice1.set_scale(0.6)
        slice1.set_pos(0, -0.56, 1.42)
        slice1.set_hpr(323.97, 37.87, 0)
        slice2 = loader.loadModel("phase_5/models/props/cream-pie-slice.bam")
        slice2.reparent_to(self.barrel)
        slice2.set_scale(0.6)
        slice2.set_pos(tart2.get_pos() + (0, 0, 0.35))
        slice2.set_hpr(tart2.get_hpr())
        cake1 = Actor("phase_5/models/props/birthday-cake-mod.bam",
                    {"chan": "phase_5/models/props/birthday-cake-chan.bam"})
        cake1.setPlayRate(0.3, "chan")
        cake1.loop("chan")
        cake1.set_scale(0.6)
        cake1.reparent_to(self.barrel)
        cake1.set_pos(0, 0.94, 1.40)
        cake2 = Actor("phase_5/models/props/birthday-cake-mod.bam",
                    {"chan": "phase_5/models/props/birthday-cake-chan.bam"})
        cake2.setPlayRate(-0.3, "chan")
        cake2.loop("chan")
        cake2.set_pos(0, -0.1, 1.4)
        cake2.set_scale(0.5)
        cake2.reparent_to(self.barrel)
        self.gagsInBarrel = [
            tart1, tart2, slice1, slice2, cake1, cake2
        ]
        del tart1
        del tart2
        del slice1
        del slice2
        del cake1
        del cake2
        
    def removeClerk(self):
        DistributedShop.removeClerk(self)
        if self.gagsInBarrel:
            for gag in self.gagsInBarrel:
                if type(gag) == Actor:
                    gag.delete()
                else:
                    gag.removeNode()
                del gag
            self.gagsInBarrel = None
        if self.barrel:
            self.barrel.removeNode()
            self.barrel = None
        
    def disable(self):
        self.ignore(self.gagShopStateData.doneEvent)
        if self.inShop:
            self.gagShopStateData.unload()
            self.gagShopStateData.exit()
        DistributedShop.disable(self)
        
    def delete(self):
        DistributedShop.delete(self)
        self.gagShopStateData = None
