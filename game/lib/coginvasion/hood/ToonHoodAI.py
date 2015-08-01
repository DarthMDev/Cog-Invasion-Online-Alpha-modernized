"""

  Filename: ToonHoodAI.py
  Created by: blach (05Jan15)

"""

from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.hood.HoodAI import HoodAI
from lib.coginvasion.shop.DistributedGagShopAI import DistributedGagShopAI
from lib.coginvasion.suit.DistributedSuitManagerAI import DistributedSuitManagerAI
from direct.directnotify.DirectNotifyGlobal import directNotify
from lib.coginvasion.suit.DistributedCogStationAI import DistributedCogStationAI
from lib.coginvasion.suit import CogBattleGlobals

class ToonHoodAI(HoodAI):
    notify = directNotify.newCategory("ToonHoodAI")

    def __init__(self, air, zoneId, hood):
        HoodAI.__init__(self, air, zoneId, hood)
        self.gagShop = None
        self.suitManager = None
        self.cogStation = None

    def startup(self):
        HoodAI.startup(self)
        #self.notify.info("Generating gag shop...")
        #self.gagShop = DistributedGagShopAI(self.air)
        #self.gagShop.generateWithRequired(self.zoneId)
        #x, y, z, h, p, r = self.hoodMgr.GagShopClerkPoints[self.hood]
        #self.gagShop.b_setPosHpr(x, y, z ,h, p, r)
        #if base.config.GetBool('want-suits', True):
        #	self.notify.info("Creating suit manager...")
        #	self.suitManager = DistributedSuitManagerAI(self.air)
        #	self.suitManager.generateWithRequired(self.zoneId)
        #else:
        #	self.notify.info("Won't create suits.")
        if CogBattleGlobals.HoodId2HoodIndex.get(self.hood, None) != None:
            self.cogStation = DistributedCogStationAI(self.air)
            self.cogStation.generateWithRequired(self.zoneId)
            self.cogStation.setHoodIndex(CogBattleGlobals.HoodId2HoodIndex[self.hood])
            self.cogStation.b_setLocationPoint(self.cogStation.getHoodIndex())
        else:
            self.notify.info("This ToonHood is not a cog battle area.")

    def shutdown(self):
        if self.gagShop:
            self.notify.info("Shutting down gag shop...")
            self.gagShop.requestDelete()
            self.gagShop = None
        if self.suitManager:
            self.notify.info("Shutting down suit manager...")
            self.suitManager.requestDelete()
            self.suitManager = None
        HoodAI.shutdown(self)
