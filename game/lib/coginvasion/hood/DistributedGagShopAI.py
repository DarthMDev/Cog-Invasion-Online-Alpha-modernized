"""

  Filename: DistributedGagShopAI.py
  Created by: blach (20Dec14)

"""

from direct.directnotify.DirectNotifyGlobal import directNotify

from lib.coginvasion.hood.DistributedShopAI import DistributedShopAI

class DistributedGagShopAI(DistributedShopAI):
    notify = directNotify.newCategory("DistributedGagShopAI")
    
    def __init__(self, air):
        try:
            self.DistributedGagShopAI_initialized
            return
        except:
            self.DistributedGagShopAI_initialized = 1
        DistributedShopAI.__init__(self, air)
        return
        
    def confirmPurchase(self, ammoList, money):
        avId = self.air.getAvatarIdFromSender()
        DistributedShopAI.confirmPurchase(self, avId, money)
        obj = self.air.doId2do.get(avId)
        obj.b_setGagAmmo(ammoList)