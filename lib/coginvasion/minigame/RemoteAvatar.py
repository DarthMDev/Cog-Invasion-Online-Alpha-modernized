"""

  Filename: RemoteAvatar.py
  Created by: blach (28Apr15)

"""

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.showbase import Audio3DManager

class RemoteAvatar:
	audio3d = Audio3DManager.Audio3DManager(base.sfxManagerList[0], camera)
	audio3d.setDistanceFactor(25)
	audio3d.setDropOffFactor(0.025)
	
	notify = directNotify.newCategory("RemoteAvatar")
	
	def __init__(self, mg, cr, avId):
		self.mg = mg
		self.cr = cr
		self.avId = avId
		self.avatar = None
		
	def retrieveAvatar(self):
		self.avatar = self.cr.doId2do.get(self.avId, None)
		if not self.avatar:
			self.notify.warning("Tried to create a " + self.__class__.__name__ + " when the avatar doesn't exist!")
			self.avatar = None
	
	def cleanup(self):
		del self.avatar
		del self.avId
		del self.cr
		del self.mg
