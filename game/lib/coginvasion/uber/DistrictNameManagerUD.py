# Filename: DistrictNameManagerUD.py
# Created by:  blach (23Jul15)

from direct.distributed.DistributedObjectGlobalUD import DistributedObjectGlobalUD
from direct.directnotify.DirectNotifyGlobal import directNotify

class DistrictNameManagerUD(DistributedObjectGlobalUD):
    notify = directNotify.newCategory("DistrictNameManagerUD")

    def __init__(self, air):
        DistributedObjectGlobalUD.__init__(self, air)
        self.availableNames = []

    def toonJoined(self, avatarId):

        def toonResponse(dclass, fields):
            if dclass != self.air.dclassesByName['DistributedToonUD']:
                return

            name = fields['setName'][0]
            fl = fields['setFriendsList'][0]
            self.air.friendsManager.d_toonOnline(avatarId, name, fl)

        self.air.dbInterface.queryObject(
            self.air.dbId,
            avatarId,
            toonResponse
        )

    def toonLeft(self, avatarId):

        def toonResponse(dclass, fields):
            if dclass != self.air.dclassesByName['DistributedToonUD']:
                return

            name = fields['setName'][0]
            fl = fields['setFriendsList'][0]
            self.air.friendsManager.d_toonOffline(avatarId, name, fl)

        self.air.dbInterface.queryObject(
            self.air.dbId,
            avatarId,
            toonResponse
        )

    def requestDistrictName(self):
        sender = self.air.getMsgSender()
        # Give them the first name in the array, if it exists.
        if len(self.availableNames) > 0:
            name = self.availableNames[0]
            self.sendUpdateToChannel(sender, 'claimDistrictName', [name])
            self.availableNames.remove(name)
        else:
            self.sendUpdateToChannel(sender, 'noAvailableNames', [])

    def announceGenerate(self):
        DistributedObjectGlobalUD.announceGenerate(self)
        namesFile = open("astron/DistrictNames.txt")
        lines = namesFile.readlines()
        for index in range(len(lines) - 1):
            lines[index] = lines[index][:-1]
        self.availableNames = lines
        namesFile.close()

    def delete(self):
        self.availableNames = None
        DistributedObjectGlobalUD.delete(self)
