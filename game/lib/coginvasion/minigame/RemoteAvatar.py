"""

  Filename: RemoteAvatar.py
  Created by: blach (28Apr15)

"""

from direct.directnotify.DirectNotifyGlobal import directNotify

class RemoteAvatar:

    notify = directNotify.newCategory("RemoteAvatar")

    def __init__(self, mg, cr, avId):
        self.mg = mg
        self.cr = cr
        self.avId = avId
        self.avatar = None

    def retrieveAvatar(self):
        self.avatar = self.cr.doId2do.get(self.avId, None)
        self.avatar.setPythonTag('player', self.avId)
        if not self.avatar:
            self.notify.warning("Tried to create a " + self.__class__.__name__ + " when the avatar doesn't exist!")
            self.avatar = None

    def cleanup(self):
        del self.avatar
        del self.avId
        del self.cr
        del self.mg
