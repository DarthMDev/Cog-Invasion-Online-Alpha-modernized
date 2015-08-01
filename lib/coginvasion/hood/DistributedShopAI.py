# Filename: DistributedShopAI.py
# Created by:  blach (14Jun15)

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.DistributedNodeAI import DistributedNodeAI

class DistributedShopAI(DistributedNodeAI):
	notify = directNotify.newCategory("DistributedShopAI")
	
	def __init__(self, air):
		try:
			self.DistributedShopAI_initialized
			return
		except:
			self.DistributedShopAI_initialized = 1
		DistributedNodeAI.__init__(self, air)
		self.avatars = []
	
	def requestEnter(self):
		"""
		Somebody requested to enter our gag shop, do some
		checks on this avId that they sent.
        """
		avId = self.air.getAvatarIdFromSender()
		if not avId in self.avatars:
			avatar = self.air.doId2do.get(avId)
			if avatar.getMoney() > 0:
				self.sendUpdateToAvatarId(avId, 'enterAccepted', [])
				self.avatars.append(avId)
			else:
				self.sendUpdateToAvatarId(avId, 'exitAccepted', [])
				self.sendUpdate('setChat', [1])
    
	def requestExit(self):
		avId = self.air.getAvatarIdFromSender()
		if avId in self.avatars:
			self.sendUpdateToAvatarId(avId, 'exitAccepted', [])
			self.sendUpdate('setChat', [0])
			self.avatars.remove(avId)
    
	def confirmPurchase(self, avId, money):
		obj = self.air.doId2do.get(avId)
		obj.b_setMoney(money)
    
	def disable(self):
		self.avatars = []
        
	def delete(self):
		del self.avatars
		DistributedNodeAI.delete(self)
