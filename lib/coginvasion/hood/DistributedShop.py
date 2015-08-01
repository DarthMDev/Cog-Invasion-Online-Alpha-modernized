# Filename: DistributedShop.py
# Created by:  blach (14Jun15)

from panda3d.core import NodePath, CollisionSphere, CollisionNode
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.DistributedNode import DistributedNode

from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.toon.Toon import Toon
from lib.coginvasion.npc import NPCGlobals

class DistributedShop(DistributedNode):
    notify = directNotify.newCategory("DistributedShop")

    def __init__(self, cr):
        try:
            self.DistributedShop_initialized
            return
        except:
            self.DistributedShop_initialized = 1
        DistributedNode.__init__(self, cr)
        NodePath.__init__(self, 'shop')
        self.inShop = False
        self.snp = None
        self.clerk = None
    
    def announceGenerate(self):
        DistributedNode.announceGenerate(self)
        self.__initCollisions('shopSphere' + str(self.doId))
        self.setupClerk()
        self.setParent(CIGlobals.SPRender)
            
    def disable(self):
        self.inShop = False
        self.snp = None
        self.removeClerk()
        DistributedNode.disable(self)
        
    def delete(self):
        self.inShop = None
        DistributedNode.delete(self)
        
    def enterAccepted(self):
        pass
    
    def __deleteCollisions(self):
        self.ignore("enter" + self.snp.node().getName())
        self.snp.removeNode()
        del self.snp
        
    def __handleEnterCollisionSphere(self, entry):
        self.notify.debug("Entering collision sphere...")
        self.d_requestEnter()
        
    def d_requestEnter(self):
        self.cr.playGame.getPlace().fsm.request('stop')
        self.sendUpdate('requestEnter', [])
        
    def d_requestExit(self):
        self.cr.playGame.getPlace().fsm.request('stop')
        self.sendUpdate('requestExit', [])
    
    def exitAccepted(self):
        self.cr.playGame.getPlace().fsm.request('walk')
        self.acceptOnce("enter" + self.snp.node().getName(), self.__handleEnterCollisionSphere)
        if self.inShop: self.inShop = False
    
    def _destroyDO(self):
        # A hacky workaround for the self.cr = None bug.
        
        # after this is called, the object is no longer a DistributedObject
        # but may still be used as a DelayDeleted object
        self.destroyDoStackTrace = StackTrace()
        # check for leftover cached data that was not retrieved or flushed by this object
        # this will catch typos in the data name in calls to get/setCachedData
        if hasattr(self, '_cachedData'):
            for name, cachedData in self._cachedData.iteritems():
                self.notify.warning('flushing unretrieved cached data: %s' % name)
                cachedData.flush()
            del self._cachedData
        
    def setupClerk(self):
        self.clerk = Toon(self.cr)
        self.clerk.setDNAStrand(NPCGlobals.NPC_DNA['Professor Pete'])
        self.clerk.generateToon()
        self.clerk.reparentTo(self)
        self.clerk.animFSM.request('neutral')
        
    def removeClerk(self):
        self.clerk.disable()
        self.clerk.delete()
        self.clerk = None
        
    def setChat(self, msgId):
        msgs = [CIGlobals.ShopGoodbye, CIGlobals.ShopNoMoney]
        self.clerk.setChat(msgs[msgId])
    
    def __initCollisions(self, name):
        self.notify.debug("Initializing collision sphere...")
        ss = CollisionSphere(0,0,0,5)
        ss.setTangible(0)
        snode = CollisionNode(name)
        snode.add_solid(ss)
        snode.set_collide_mask(CIGlobals.WallBitmask)
        self.snp = self.attach_new_node(snode)
        self.snp.setZ(3)
        self.acceptOnce("enter" + self.snp.node().getName(), self.__handleEnterCollisionSphere)
