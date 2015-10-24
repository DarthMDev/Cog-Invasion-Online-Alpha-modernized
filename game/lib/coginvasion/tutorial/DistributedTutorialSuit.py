# Filename: DistributedTutorialSuit.py
# Created by:  blach (21Oct15)

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.interval.IntervalGlobal import LerpPosInterval, Sequence, Wait

from lib.coginvasion.cog.DistributedSuit import DistributedSuit
from lib.coginvasion.npc.NPCWalker import NPCWalkInterval
import TutorialGlobals

import random

class DistributedTutorialSuit(DistributedSuit):
    notify = directNotify.newCategory('DistributedTutorialSuit')

    def enterFlyingDown(self, startIndex, endIndex, ts = 0.0):
        startPos = TutorialGlobals.SUIT_POINTS[startIndex] + (0, 0, 50)
        endPos = TutorialGlobals.SUIT_POINTS[endIndex]
        duration = 3
        self.moveIval = LerpPosInterval(self, duration = duration, pos = endPos, startPos = startPos, fluid = 1)
        self.moveIval.start(ts)
        self.animFSM.request('flyDown', [ts])
        yaw = random.uniform(0.0, 360.0)
        self.setH(yaw)

    def enterWalking(self, startIndex, endIndex, ts = 0.0):
        durationFactor = 0.2
        if startIndex > -1:
            startPos = TutorialGlobals.SUIT_POINTS[startIndex]
        else:
            startPos = self.getPos(render)
        endPos = TutorialGlobals.SUIT_POINTS[endIndex]
        self.stopMoving()
        self.moveIval = NPCWalkInterval(self, endPos, durationFactor, startPos, fluid = 1)
        self.moveIval.start(ts)
        self.animFSM.request('walk')
