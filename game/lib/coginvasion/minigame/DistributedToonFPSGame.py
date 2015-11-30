# Filename: DistributedToonFPSGame.py
# Created by:  blach (30Mar15)

from panda3d.core import Vec4

from direct.interval.IntervalGlobal import Sequence, Func, LerpScaleInterval, LerpColorScaleInterval, Parallel
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.ClockDelta import globalClockDelta

from DistributedMinigame import DistributedMinigame

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

    def makeSmokeEffect(self, pos):
        smoke = loader.loadModel("phase_4/models/props/test_clouds.bam")
        smoke.setBillboardAxis()
        smoke.reparentTo(render)
        smoke.setPos(pos)
        smoke.setScale(0.05, 0.05, 0.05)
        smoke.setDepthWrite(False)
        track = Sequence(
            Parallel(
                LerpScaleInterval(smoke, 0.5, (0.1, 0.15, 0.15)),
                LerpColorScaleInterval(smoke, 0.5, Vec4(2, 2, 2, 0))),
            Func(smoke.removeNode))
        track.start()

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

    def setupRemoteAvatar(self, avId):
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
