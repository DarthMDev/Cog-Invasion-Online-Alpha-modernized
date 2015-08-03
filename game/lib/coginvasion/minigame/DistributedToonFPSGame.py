"""

  Filename: DistributedToonFPSGame.py
  Created by: blach (30Mar15)

"""

from DistributedMinigame import DistributedMinigame
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.ClockDelta import globalClockDelta

class DistributedToonFPSGame(DistributedMinigame):
    notify = directNotify.newCategory("DistributedToonFPSGame")

    def __init__(self, cr):
        try:
            self.DistributedToonFPSGame_initialized
            return
        except:
            self.DistributedToonFPSGame_initialized = 1
        DistributedMinigame.__init__(self, cr)
        self.remoteAvatars = []
        self.myRemoteAvatar = None

    def avatarHitByBullet(self, avId, damage):
        pass

    def d_gunShot(self):
        timestamp = globalClockDelta.getFrameNetworkTime()
        self.sendUpdate('gunShot', [base.localAvatar.doId, timestamp])

    def standingAvatar(self, avId):
        av = self.getRemoteAvatar(avId)
        if av:
            av.stand()

    def runningAvatar(self, avId):
        av = self.getRemoteAvatar(avId)
        if av:
            av.run()

    def jumpingAvatar(self, avId):
        av = self.getRemoteAvatar(avId)
        if av:
            av.jump()

    def getMyRemoteAvatar(self):
        return self.myRemoteAvatar

    def damage(self, amount, avId):
        self.toonFps.damageTaken(amount, avId)

    def attachGunToAvatar(self, avId):
        # Should be overridden by inheritors.
        pass

    def gunShot(self, avId, timestamp):
        ts = globalClockDelta.localElapsedTime(timestamp)
        av = self.getRemoteAvatar(avId)
        if av:
            av.fsm.request('shoot', [ts])

    def deadAvatar(self, avId, timestamp):
        ts = globalClockDelta.localElapsedTime(timestamp)
        av = self.getRemoteAvatar(avId)
        if av:
            av.fsm.request('die', [ts])

    def respawnAvatar(self, avId):
        av = self.getRemoteAvatar(avId)
        if av:
            av.exitDead()
            av.fsm.requestFinalState()

    def getRemoteAvatar(self, avId):
        for avatar in self.remoteAvatars:
            if avatar.avId == avId:
                return avatar
        return None

    def disable(self):
        self.myRemoteAvatar.cleanup()
        self.myRemoteAvatar = None
        for av in self.remoteAvatars:
            av.cleanup()
            del av
        self.remoteAvatars = None
        DistributedMinigame.disable(self)
