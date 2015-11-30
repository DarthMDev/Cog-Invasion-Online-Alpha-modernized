# Filename: FriendsManager.py
# Created by:  blach (04Aug15)

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.DistributedObjectGlobal import DistributedObjectGlobal

from lib.coginvasion.globals import CIGlobals, ChatGlobals
from lib.coginvasion.gui.Whisper import Whisper
from lib.coginvasion.gui.WhisperPopup import WhisperPopup

class FriendsManager(DistributedObjectGlobal):
    notify = directNotify.newCategory("FriendsManager")

    ComingOnlineMessage = "%s is coming online!"
    GoingOfflineMessage = "%s has logged out."
    LeftListMessage = "%s left your friends list."
    TeleportNotify = "%s is coming to visit you."

    def d_sendWhisper(self, target, message):
        self.sendUpdate('sendWhisper', [target, message])

    def whisper(self, sender, message, name):
        base.playSfx(self.cr.whisperNoise)
        whisper = WhisperPopup(name + ': ' + message, CIGlobals.getToonFont(), ChatGlobals.WTNormal)
        whisper.setClickable(name, sender, isPlayer = 1)
        whisper.manage(base.marginManager)

    def getAvatarName(self, avId):
        av = self.cr.doId2do.get(avId)
        if av:
            return av.getName()

    def d_requestFriendsList(self):
        self.sendUpdate('requestFriendsList', [])

    def friendsList(self, idArray, nameArray, flags):
        messenger.send('gotFriendsList', [idArray, nameArray, flags])

    def teleportNotify(self, name):
        Whisper().createSystemMessage(self.TeleportNotify % name)

    def friendLeftYourList(self, avatarId):
        Whisper().createSystemMessage(self.LeftListMessage % self.getAvatarName(avatarId))
        base.localAvatar.panel.maybeUpdateFriendButton()
        self.d_requestFriendsList()

    def toonOnline(self, avatarId, name):
        if avatarId in base.localAvatar.friends:
            Whisper().createSystemMessage(self.ComingOnlineMessage % name)
            self.d_requestFriendsList()

    def toonOffline(self, avatarId, name):
        if avatarId in base.localAvatar.friends:
            Whisper().createSystemMessage(self.GoingOfflineMessage % name)
            self.d_requestFriendsList()

    def avatarInfo(self, name, dna, maxHP, hp, zoneId, shardId, isOnline):
        messenger.send('avatarInfoResponse', [name, dna, maxHP, hp, zoneId, shardId, isOnline])

    def friendRequest(self, sender, name, dna):
        messenger.send('newFriendRequest', [sender, name, dna])

    def avatarLocation(self, avatarId, shardId, zoneId):
        messenger.send('gotAvatarTeleportResponse', [avatarId, shardId, zoneId])

    def d_myAvatarLocation(self, avatarId, shardId, zoneId):
        self.sendUpdate('myAvatarLocation', [avatarId, shardId, zoneId])

    def avatarWantsYourLocation(self, avatarId):
        self.d_myAvatarLocation(avatarId, base.localAvatar.parentId, base.localAvatar.zoneId)

    def d_requestAvatarInfo(self, avatarId):
        self.sendUpdate('requestAvatarInfo', [avatarId])

    def d_iWantToTeleportToAvatar(self, avatarId):
        self.sendUpdate('iWantToTeleportToAvatar', [avatarId])

    def d_iRemovedFriend(self, avatarId):
        self.sendUpdate('iRemovedFriend', [avatarId])

    def d_iAcceptedFriendRequest(self, avatarId):
        self.sendUpdate('iAcceptedFriendRequest', [avatarId])

    def d_iRejectedFriendRequest(self, avatarId):
        self.sendUpdate('iRejectedFriendRequest', [avatarId])

    def d_iCancelledFriendRequest(self, avatarId):
        self.sendUpdate('iCancelledFriendRequest', [avatarId])

    def d_requestAvatarStatus(self, avatarId):
        self.sendUpdate('requestAvatarStatus', [avatarId])

    def d_myAvatarStatus(self, avatarId):
        busy = base.localAvatar.getBusy()
        if base.localAvatar.getMyBattle():
            busy = 1
        self.sendUpdate('myAvatarStatus', [avatarId, busy])

    def d_askAvatarToBeFriends(self, avatarId):
        self.sendUpdate('askAvatarToBeFriends', [avatarId])

    def avatarStatus(self, avatarId, status):
        messenger.send('gotAvatarStatus', [avatarId, status])

    def someoneWantsYourStatus(self, avatarId):
        self.d_myAvatarStatus(avatarId)

    def acceptedFriendRequest(self):
        messenger.send('friendRequestAccepted')

    def rejectedFriendRequest(self):
        messenger.send('friendRequestRejected')

    def cancelFriendRequest(self, requester):
        messenger.send('friendRequestCancelled', [requester])
