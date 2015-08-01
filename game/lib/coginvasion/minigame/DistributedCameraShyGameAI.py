"""

  Filename: DistributedCameraShyGameAI.py
  Created by: blach (27Apr15)

"""

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.interval.IntervalGlobal import Sequence, Wait, Func

import random

from DistributedMinigameAI import DistributedMinigameAI

class DistributedCameraShyGameAI(DistributedMinigameAI):
    notify = directNotify.newCategory("DistributedCameraShyGameAI")
    numPicsToTakeOfEachAvatar = 3

    def __init__(self, air):
        try:
            self.DistributedCameraShyGameAI_initialized
            return
        except:
            self.DistributedCameraShyGameAI_initialized = 1
        DistributedMinigameAI.__init__(self, air)
        self.setZeroCommand(self.d_gameOver)
        self.setInitialTime(150)
        self.winnerPrize = 30
        self.loserPrize = 15
        self.availableSpawnPoints = [0, 1, 2, 3, 4]

        self.pictureData = {}

    def tookPictureOfToon(self, idOfToon):
        avId = self.air.getAvatarIdFromSender()
        self.pictureData[avId][idOfToon] += 1

        # Check if this avatar has taken 3 pictures of all other toons.
        completedToons = 0
        for numPicsTaken in self.pictureData[avId].values():
            if numPicsTaken >= self.numPicsToTakeOfEachAvatar:
                completedToons += 1
        if completedToons == len(self.avatars) - 1:
            self.d_announceGameOver(avId)
        self.sendUpdateToAvatarId(idOfToon, 'tookPictureOfMe', [avId])
        if self.pictureData[avId][idOfToon] <= self.numPicsToTakeOfEachAvatar:
            self.sendUpdate('updateOtherPlayerHead', [avId, idOfToon, self.pictureData[avId][idOfToon]])

    def d_announceGameOver(self, winner):
        self.sendUpdate('announceGameOver', [])
        Sequence(
            Wait(3.0),
            Func(self.sendUpdate, 'showWinner', [winner]),
            Wait(7.5),
            Func(DistributedMinigameAI.d_gameOver, self, 1, [winner])
        ).start()

    def ready(self):
        avId = self.air.getAvatarIdFromSender()
        self.pictureData[avId] = {}
        for avatar in self.avatars:
            if avatar.doId != avId:
                self.pictureData[avId][avatar.doId] = 0
        index = random.choice(self.availableSpawnPoints)
        self.sendUpdateToAvatarId(avId, 'setSpawnPoint', [index])
        self.availableSpawnPoints.remove(index)
        DistributedMinigameAI.ready(self)

    def allAvatarsReady(self):
        for avatar in self.avatars:
            self.sendUpdate('createRemoteAvatar', [avatar.doId])
        DistributedMinigameAI.allAvatarsReady(self)
        self.sendHeadPanels()
        self.sendUpdate('generateOtherPlayerGui', [])
        self.startTiming()

    def d_gameOver(self):
        DistributedMinigameAI.d_gameOver(self, 1, [0])

    def disable(self):
        del self.availableSpawnPoints
        del self.pictureData
        self.stopTiming()
        DistributedMinigameAI.disable(self)
