"""

  Filename: SuitPathBehavior.py
  Created by: DecodedLogic (03Sep15)

"""

from panda3d.core import Point3, Point2

from lib.coginvasion.cog.SuitBehaviorBase import SuitBehaviorBase
from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.npc.NPCWalker import NPCWalkInterval
from direct.interval.IntervalGlobal import Sequence, Func

from SuitPathDataAI import *

import random

class SuitPathBehavior(SuitBehaviorBase):

    def __init__(self, suit, exitOnWalkFinish = True):
        SuitBehaviorBase.__init__(self, suit)
        self.walkTrack = None
        self.exitOnWalkFinish = exitOnWalkFinish
        self.isEntered = 0
        self.pathFinder = getPathFinder(self.suit.hood)
        
    def exit(self):
        self.clearWalkTrack()
        SuitBehaviorBase.exit(self)

    def unload(self):
        self.clearWalkTrack()
        del self.exitOnWalkFinish
        del self.walkTrack
        SuitBehaviorBase.unload(self)

    def createPath(self, node = None, durationFactor = 0.2, fromCurPos = False):
        x1, y1 = node.getX(render), node.getY(render)
        z = node.getZ(render)
        x2, y2 = self.suit.getX(render), self.suit.getY(render)
        path = self.pathFinder.planPath((x2, y2), (x1, y1))
        if path is None:
            return
        if len(path) > 1:
            path.remove(path[0])
        self.startPath(path, z, durationFactor)
            
    def startPath(self, path, z, durationFactor):
        pathName = self.suit.uniqueName('suitPath')
        correctedPath = []
        for i in xrange(len(path)):
            waypoint = path[i]
            correctedPath.append([waypoint[0], waypoint[1], z])
        self.suit.d_setWalkPath(correctedPath)
        self.path = correctedPath
        print self.path
        self._doWalk()
        
    def _doWalk(self):
        self.walkTrack = Sequence()
        for i in xrange(len(self.path)):
            waypoint = self.path[i]
            if i > 0:
                lastWP = self.path[i - 1]
            else:
                lastWP = [self.suit.getX(render), self.suit.getY(render), self.suit.getZ(render)]
            ival = NPCWalkInterval(self.suit, Point3(*waypoint),
                startPos = lambda self = self: self.suit.getPos(render),
                fluid = 1, name = self.suit.uniqueName('doWalkIval' + str(i)),
                duration = (Point2(waypoint[0], waypoint[1]) - Point2(lastWP[0], lastWP[1])).length() * 0.2)
            self.walkTrack.append(ival)
        self.startFollow()

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
