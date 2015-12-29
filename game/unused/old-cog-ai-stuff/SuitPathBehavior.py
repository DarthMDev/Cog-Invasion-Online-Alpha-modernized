"""

  Filename: SuitPathBehavior.py
  Created by: DecodedLogic (03Sep15)

"""

from lib.coginvasion.cog.SuitBehaviorBase import SuitBehaviorBase
from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.npc.NPCWalker import NPCWalkInterval

import random

class SuitPathBehavior(SuitBehaviorBase):

    def __init__(self, suit, exitOnWalkFinish = True):
        SuitBehaviorBase.__init__(self, suit)
        self.walkTrack = None
        self.exitOnWalkFinish = exitOnWalkFinish
        self.isEntered = 0

    def unload(self):
        SuitBehaviorBase.unload(self)
        self.clearWalkTrack()
        del self.exitOnWalkFinish
        del self.walkTrack

    def createPath(self, pathKey = None, durationFactor = 0.2, fromCurPos = False):
        currentPathQueue = self.suit.getCurrentPathQueue()
        currentPath = self.suit.getCurrentPath()
        if pathKey == None and not len(currentPathQueue):
            pathKeyList = CIGlobals.SuitPathData[self.suit.getHood()][self.suit.getCurrentPath()]
            pathKey = random.choice(pathKeyList)
        elif len(currentPathQueue):
            pathKey = currentPathQueue[0]
            currentPathQueue.remove(pathKey)
        endIndex = CIGlobals.SuitSpawnPoints[self.suit.getHood()].keys().index(pathKey)
        path = CIGlobals.SuitSpawnPoints[self.suit.getHood()][pathKey]
        self.clearWalkTrack()
        if not currentPath or fromCurPos:
            startIndex = -1
        else:
            oldPath = currentPath
            startIndex = CIGlobals.SuitSpawnPoints[self.suit.getHood()].keys().index(oldPath)
        self.suit.currentPath = pathKey
        self.startPath(path, durationFactor, startIndex, endIndex)
            
    def startPath(self, path, durationFactor, startIndex, endIndex):
        startPos = self.suit.getPos(render)
        pathName = self.suit.uniqueName('suitPath')
        self.walkTrack = NPCWalkInterval(self.suit, path, startPos = startPos,
            name = pathName, durationFactor = durationFactor, fluid = 1
        )
        self.walkTrack.setDoneEvent(self.walkTrack.getName())
        self.startFollow()
        self.suit.b_setSuitState(1, startIndex, endIndex)

    def clearWalkTrack(self):
        if self.walkTrack:
            self.ignore(self.walkTrack.getDoneEvent())
            self.walkTrack.clearToInitial()
            self.walkTrack = None
            if hasattr(self, 'suit'):
                self.suit.d_stopMoveInterval()

    def startFollow(self):
        self.suit.b_setAnimState('walk')
        if self.walkTrack:
            self.acceptOnce(self.walkTrack.getName(), self._walkDone)
            self.walkTrack.start()

    def _walkDone(self):
        self.clearWalkTrack()
        if not self.suit.isDead():
            self.suit.b_setAnimState('neutral')
            if self.exitOnWalkFinish == True:
                self.exit()

    def getWalkTrack(self):
        return self.walkTrack

    def isWalking(self):
        if self.walkTrack:
            return self.walkTrack.isPlaying()
        return False
