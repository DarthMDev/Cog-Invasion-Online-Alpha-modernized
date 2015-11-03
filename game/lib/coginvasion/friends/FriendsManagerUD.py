# Filename: FriendsManagerUD.py
# Created by:  blach (04Aug15)

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.DistributedObjectGlobalUD import DistributedObjectGlobalUD

class FriendsManagerUD(DistributedObjectGlobalUD):
    notify = directNotify.newCategory("FriendsManagerUD")

    def __init__(self, air):
        DistributedObjectGlobalUD.__init__(self, air)
        self.toonsOnline = []

    def requestFriendsList(self):
        sender = self.air.getAvatarIdFromSender()

        realFriendsList = [[], [], []]
        avatarFriendsList = []

        def friendResponse(dclass, fields):
            global avatarFriendsList
            if dclass != self.air.dclassesByName['DistributedToonUD']:
                self.notify.warning("Queried a non toon object?!")
                return

            name = fields['setName'][0]
            try:
                avatarId = avatarFriendsList[friendResponse.friend]
            except:
                self.sendUpdateToAvatarId(sender, 'friendsList', realFriendsList)
                return
            realFriendsList[0].append(avatarId)
            realFriendsList[1].append(name)
            isOnline = int(avatarId in self.toonsOnline)
            realFriendsList[2].append(isOnline)
            if friendResponse.friend == len(avatarFriendsList) - 1:
                # Done, send it out
                self.sendUpdateToAvatarId(sender, 'friendsList', realFriendsList)
                return
            friendResponse.friend += 1
            self.air.dbInterface.queryObject(
                self.air.dbId,
                avatarFriendsList[friendResponse.friend],
                friendResponse
            )

        friendResponse.friend = 0

        def avatarResponse(dclass, fields):
            global avatarFriendsList
            if dclass != self.air.dclassesByName['DistributedToonUD']:
                self.notify.warning("Queried a non toon object?!")
                return

            avatarFriendsList = fields['setFriendsList'][0]

            if len(avatarFriendsList) == 0:
                self.sendUpdateToAvatarId(sender, 'friendsList', [[], [], []])
                return

            self.air.dbInterface.queryObject(
                self.air.dbId,
                avatarFriendsList[friendResponse.friend],
                friendResponse
            )

        self.air.dbInterface.queryObject(
            self.air.dbId,
            sender,
            avatarResponse
        )

    def d_toonOnline(self, avatarId, friendsList, name):
        self.toonsOnline.append(avatarId)

        for friendId in friendsList:
            if friendId in self.toonsOnline:
                self.sendUpdateToAvatarId(friendId, 'toonOnline', [avatarId, name])

    def d_toonOffline(self, avatarId, friendsList, name):
        self.toonsOnline.remove(avatarId)

        for friendId in friendsList:
            if friendId in self.toonsOnline:
                self.sendUpdateToAvatarId(friendId, 'toonOffline', [avatarId, name])

    def requestAvatarInfo(self, avId):
        sender = self.air.getAvatarIdFromSender()

        def avatarResponse(dclass, fields):
            if dclass != self.air.dclassesByName["DistributedToonUD"]:
                self.notify.warning("requestAvatarInfo: avatarResponse: It's not a toon.")
                return

            name = fields['setName'][0]
            dna = fields['setDNAStrand'][0]
            maxHP = fields['setMaxHealth'][0]
            hp = fields['setHealth'][0]

            self.sendUpdateToAvatarId(sender, 'avatarInfo', [name, dna, maxHP, hp])

        self.air.dbInterface.queryObject(
            self.air.dbId,
            avId,
            avatarResponse
        )

    def askAvatarToBeFriends(self, avId):
        sender = self.air.getAvatarIdFromSender()

        def avatarResponse(dclass, fields):
            if dclass != self.air.dclassesByName["DistributedToonUD"]:
                self.notify.warning("requestAvatarInfo: avatarResponse: It's not a toon.")
                return

            name = fields['setName'][0]
            dna = fields['setDNAStrand'][0]

            self.sendUpdateToAvatarId(avId, 'friendRequest', [sender, name, dna])

        self.air.dbInterface.queryObject(
            self.air.dbId,
            sender,
            avatarResponse
        )

    def iRemovedFriend(self, friendId):
        sender = self.air.getAvatarIdFromSender()

        def removerAvatarResponse(dclass, fields):
            if dclass != self.air.dclassesByName["DistributedToonUD"]:
                self.notify.warning("iRemovedFriend: removerAvatarResponse: It's not a toon.")
                return

            newList = list(fields['setFriendsList'][0])
            newList.remove(friendId)
            dg = dclass.aiFormatUpdate('setFriendsList', sender, sender, self.air.ourChannel, [newList])
            self.air.send(dg)
            self.air.dbInterface.updateObject(self.air.dbId, sender, dclass, {'setFriendsList': [newList]})

        def removeeAvatarResponse(dclass, fields):
            if dclass != self.air.dclassesByName["DistributedToonUD"]:
                self.notify.warning("iRemovedFriend: removeeAvatarResponse: It's not a toon.")
                return

            newList = list(fields['setFriendsList'][0])
            newList.remove(sender)
            dg = dclass.aiFormatUpdate('setFriendsList', friendId, friendId, self.air.ourChannel, [newList])
            self.air.send(dg)
            self.air.dbInterface.updateObject(self.air.dbId, friendId, dclass, {'setFriendsList': [newList]})

        self.air.dbInterface.queryObject(
            self.air.dbId,
            sender,
            removerAvatarResponse
        )
        self.air.dbInterface.queryObject(
            self.air.dbId,
            friendId,
            removeeAvatarResponse
        )

        self.sendUpdateToAvatarId(friendId, 'friendLeftYourList', [sender])

    def iAcceptedFriendRequest(self, avatarId):
        sender = self.air.getAvatarIdFromSender()

        def accepterAvatarResponse(dclass, fields):
            if dclass != self.air.dclassesByName["DistributedToonUD"]:
                self.notify.warning("iAcceptedFriendRequest: accepterAvatarResponse: It's not a toon.")
                return

            newList = list(fields['setFriendsList'][0])
            newList.append(avatarId)
            dg = dclass.aiFormatUpdate('setFriendsList', sender, sender, self.air.ourChannel, [newList])
            self.air.send(dg)
            self.air.dbInterface.updateObject(self.air.dbId, sender, dclass, {'setFriendsList': [newList]})

        def requesterAvatarResponse(dclass, fields):
            if dclass != self.air.dclassesByName["DistributedToonUD"]:
                self.notify.warning("iAcceptedFriendRequest: requesterAvatarResponse: It's not a toon.")
                return

            newList = list(fields['setFriendsList'][0])
            newList.append(sender)
            dg = dclass.aiFormatUpdate('setFriendsList', avatarId, avatarId, self.air.ourChannel, [newList])
            self.air.send(dg)
            self.air.dbInterface.updateObject(self.air.dbId, avatarId, dclass, {'setFriendsList': [newList]})

        self.air.dbInterface.queryObject(
            self.air.dbId,
            sender,
            accepterAvatarResponse
        )
        self.air.dbInterface.queryObject(
            self.air.dbId,
            avatarId,
            requesterAvatarResponse
        )

        self.sendUpdateToAvatarId(avatarId, 'acceptedFriendRequest', [])

    def iRejectedFriendRequest(self, avatarId):
        self.sendUpdateToAvatarId(avatarId, 'rejectedFriendRequest', [])

    def iCancelledFriendRequest(self, avatarId):
        sender = self.air.getAvatarIdFromSender()
        self.sendUpdateToAvatarId(avatarId, 'cancelFriendRequest', [sender])

    def requestAvatarStatus(self, avatarId):
        sender = self.air.getAvatarIdFromSender()
        self.sendUpdateToAvatarId(avatarId, 'someoneWantsYourStatus', [sender])

    def myAvatarStatus(self, avatarId, status):
        sender = self.air.getAvatarIdFromSender()
        self.sendUpdateToAvatarId(avatarId, 'avatarStatus', [sender, status])

    def iWantToTeleportToAvatar(self, avatarId):
        sender = self.air.getAvatarIdFromSender()
        self.sendUpdateToAvatarId(avatarId, 'avatarWantsYourLocation', [sender])

    def myAvatarLocation(self, avatarId, shardId, zoneId):
        sender = self.air.getAvatarIdFromSender()

        def teleportingAvatarResponse(dclass, fields):
            if dclass != self.air.dclassesByName['DistributedToonUD']:
                return

            name = fields['setName'][0]
            self.sendUpdateToAvatarId(sender, 'teleportNotify', [name])

        self.air.dbInterface.queryObject(
            self.air.dbId,
            avatarId,
            teleportingAvatarResponse
        )
        self.sendUpdateToAvatarId(avatarId, 'avatarLocation', [sender, shardId, zoneId])
