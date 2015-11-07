# Filename: DistributedClerkNPCToonAI.py
# Created by:  blach (06Nov15)

from direct.directnotify.DirectNotifyGlobal import directNotify

from lib.coginvasion.globals import CIGlobals
from DistributedNPCToonAI import DistributedNPCToonAI

class DistributedClerkNPCToonAI(DistributedNPCToonAI):
    notify = directNotify.newCategory('DistributedClerkNPCToonAI')

    def confirmPurchase(self, gagIds, ammoList, money):
        avId = self.air.getAvatarIdFromSender()
        av = self.air.doId2do.get(avId)
        av.b_setMoney(money)
        if av:
            for i in range(len(gagIds)):
                gagId = gagIds[i]
                ammo = ammoList[i]
                av.b_setGagAmmo(gagId, ammo)

    def hasValidReasonToEnter(self, avId):
        av = self.air.doId2do.get(avId)
        if av.getMoney() < 1:
            return False
        return True

    def requestEnter(self):
        avId = self.air.getAvatarIdFromSender()
        if (self.currentAvatar != None or
        self.currentAvatar == None and not self.hasValidReasonToEnter(avId)):
            self.sendUpdateToAvatarId(avId, 'rejectEnter', [])
        else:
            self.currentAvatar = avId
            av = self.air.doId2do.get(avId)
            self.startWatchingCurrentAvatar()
            self.d_setChat("Choose what you want to buy.")
            self.sendUpdateToAvatarId(avId, 'enterAccepted', [])
            self.sendUpdate('lookAtAvatar', [avId])

    def requestExit(self):
        DistributedNPCToonAI.requestExit(self)
        if self.currentAvatar == None:
            self.d_setChat(CIGlobals.ShopGoodbye)
