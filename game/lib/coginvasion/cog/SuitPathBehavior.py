"""

  Filename: SuitPathBehavior.py
  Created by: DecodedLogic (03Sep15)

"""

from panda3d.core import Point3

from lib.coginvasion.cog.SuitBehaviorBase import SuitBehaviorBase
from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.npc.NPCWalker import NPCWalkInterval
from direct.interval.IntervalGlobal import Sequence

from SuitPathDataAI import *

import random

class SuitPathBehavior(SuitBehaviorBase):

    def __init__(self, suit, exitOnWalkFinish = True):
        SuitBehaviorBase.__init__(self, suit)
        self.walkTrack = None
        self.exitOnWalkFinish = exitOnWalkFinish
        self.isEntered = 0
        self.pathFinder = getPathFinder(self.suit.hood)

    def unload(self):
        SuitBehaviorBase.unload(self)
        self.clearWalkTrack()
        del self.exitOnWalkFinish
        del self.walkTrack

    def createPath(self, node = None, durationFactor = 0.2, fromCurPos = False):
        x1, y1 = node.getX(render), node.getY(render)
        x2, y2 = self.suit.getX(render), self.suit.getY(render)
        path = self.pathFinder.planPath((x2, y2), (x1, y1))
        if path is None:
            return
        self.startPath(path, durationFactor)
            
    def startPath(self, path, durationFactor):
        pathName = self.suit.uniqueName('suitPath')
        self.path = path
        self.suit.d_setWalkPath(path)
        self._doWalk()
        
    def _doWalk(self):
        waypoint = self.path[0]
        print 'walking to: {0}'.format(waypoint)
        self.walkTrack = NPCWalkInterval(self.suit, Point3(waypoint[0], waypoint[1], 0), startPos = self.suit.getPos(render),
            durationFactor = 0.2, fluid = 1, name = self.suit.uniqueName('walkIval'))
        self.walkTrack.setDoneEvent(self.walkTrack.getName())
        self.acceptOnce(self.walkTrack.getDoneEvent(), self._handleWalkDone)
        self.path.remove(waypoint)
        self.startFollow()
        
    def _handleWalkDone(self):
        if len(self.path) == 0:
            return
        self._doWalk()

    def clearWalkTrack(self):
        if self.walkTrack:
            self.ignore(self.walkTrack.getDoneEvent())
            self.walkTrack.clearToInitial()
            self.walkTrack = None
            if hasattr(self, 'suit'):
                self.suit.d_stopMoveInterval()

    def startFollow(self):
        if self.walkTrack:
            #self.acceptOnce(self.walkTrack.getName(), self._walkDone)
            self.walkTrack.start()

    def _walkDone(self):
        self.clearWalkTrack()
        if not self.suit.isDead():
            if self.exitOnWalkFinish == True:
                self.exit()

    def getWalkTrack(self):
        return self.walkTrack

    def isWalking(self):
        if self.walkTrack:
            return self.walkTrack.isPlaying()
        return False
