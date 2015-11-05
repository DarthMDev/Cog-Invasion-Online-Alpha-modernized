"""

  Filename: DistributedGunGameAI.py
  Created by: blach (26Oct14)

"""

from panda3d.core import *
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.interval.IntervalGlobal import *

from lib.coginvasion.minigame.DistributedToonFPSGameAI import DistributedToonFPSGameAI
import GunGameLevelLoaderAI
from GunGameGlobals import *

class DistributedGunGameAI(DistributedToonFPSGameAI):
    notify = directNotify.newCategory("DistributedGunGameAI")

    def __init__(self, air):
        try:
            self.DistributedGunGameAI_initialized
            return
        except:
            self.DistributedGunGameAI_initialized = 1
        DistributedToonFPSGameAI.__init__(self, air)
        self.loader = GunGameLevelLoaderAI.GunGameLevelLoaderAI(self)
        self.setZeroCommand(self.timeUp)
        self.setInitialTime(305) # 5 minutes + the time it takes to countdown
        self.winnerPrize = 70
        self.loserPrize = 15
        self.gameMode = 0
        self.votes = {}
        return

    def setGameMode(self, mode):
        self.gameMode = mode

    def d_setGameMode(self, mode):
        self.sendUpdate('setGameMode', [mode])

    def b_setGameMode(self, mode):
        self.d_setGameMode(mode)
        self.setGameMode(mode)

    def getGameMode(self):
        return self.gameMode

    def timeUp(self):
        self.sendUpdate('timeUp', [])
        Sequence(Wait(10.0), Func(self.d_gameOver)).start()

    def d_gameOver(self):
        winnerAvIds = []
        for avId in self.finalScoreAvIds:
            score = self.finalScores[self.finalScoreAvIds.index(avId)]
            if score == max(self.finalScores):
                winnerAvIds.append(avId)
        DistributedToonFPSGameAI.d_gameOver(self, 1, winnerAvIds)

    def allAvatarsReady(self):
        for avatar in self.avatars:
            self.sendUpdate('attachGunToAvatar', [avatar.doId])
        DistributedToonFPSGameAI.allAvatarsReady(self)
        self.startTiming()
        #self.sendUpdate('startGameModeVote', [])

    def myGameModeVote(self, mode):
        self.votes[mode] += 1
        totalVotes = 0
        for numVotes in self.votes.values():
            totalVotes += numVotes
        if totalVotes >= len(self.avatars):
            v = list(self.votes.values())
            k = list(self.votes.keys())
            gameMode = k[v.index(max(v))]
            self.b_setGameMode(gameMode)
            self.setupGameMode()

    def setupGameMode(self):
        if self.gameMode == GameModes.CASUAL:
            DistributedToonFPSGameAI.allAvatarsReady(self)
            self.startTiming()
        elif self.gameMode == GameModes.CTF:
            self.sendUpdate('makeCTF_Flags', [])

    def deadAvatar(self, avId, timestamp):
        sender = self.air.getAvatarIdFromSender()

    def dead(self, killerId):
        self.sendUpdateToAvatarId(killerId, 'incrementKills', [])

    def d_setLevelName(self, level):
        self.sendUpdate('setLevelName', [level])

    def getLevelName(self):
        return self.loader.getLevel()

    def generate(self):
        self.loader.makeLevel()
        self.setInitialTime(self.loader.getGameTimeOfCurrentLevel())
        DistributedToonFPSGameAI.generate(self)

    def delete(self):
        try:
			self.DistributedGunGameAI_deleted
			return
		except:
			self.DistributedGunGameAI_deleted = 1
        self.stopTiming()
        self.loader.cleanup()
        DistributedToonFPSGameAI.delete(self)
