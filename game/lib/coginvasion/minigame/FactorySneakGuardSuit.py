# Filename: FactorySneakGuardSuit.py
# Created by:  blach (21Aug15)

from panda3d.core import PerspectiveLens, Spotlight

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.fsm.FSM import FSM
from direct.interval.IntervalGlobal import LerpHprInterval

from lib.coginvasion.npc.NPCWalker import NPCLookInterval
from lib.coginvasion.cog.Suit import Suit
from lib.coginvasion.globals import CIGlobals
import CogGuardGlobals as CGG

import random

class FactorySneakGuardSuit(Suit, FSM):
    notify = directNotify.newCategory("FactorySneakGuardSuit")

    SUIT = "mrhollywood"
    VIEW_DISTANCE_TASK_NAME = "ViewDistanceTask"
    MAX_VIEW_DISTANCE = 100.0
    GUARD_DIED_DELAY = 6.0
    MAX_HP = 200

    IN_VIEW = "somethingInSight"
    HEARD = "heard"
    TRY_TO_CONFIRM_TIME = 5.0

    def __init__(self, world, guardKey):
        Suit.__init__(self)
        FSM.__init__(self, 'FactorySneakGuardSuit')
        self.gameWorld = world
        self.guardKey = guardKey
        self.viewDistanceTaskName = self.VIEW_DISTANCE_TASK_NAME + "-" + str(id(self))
        self.diedTaskName = "GuardDied-" + str(id(self))
        self.health = 0
        self.maxHealth = self.MAX_HP
        self.eyeLight = None
        self.eyeLens = None
        self.eyeNode = None
        self.moveTrack = None

    def enterGuard(self):
        self.loop('neutral')
        pos, hpr = CGG.FactoryGuardPoints[self.guardKey]
        self.setHpr(hpr - (180, 0, 0))
        self.setPos(pos)

        base.taskMgr.add(self.__guard, self.taskName("guard"))

    def __guard(self, task):
        # Can we see the target?
        if self.eyeNode.node().isInView(base.localAvatar.getPos(self.eyeNode)):
            # Yes, we can! Prowler spotted!
            self.request('SeekTarget', self.IN_VIEW)
            return task.done
        return task.cont

    def exitGuard(self):
        base.taskMgr.remove(self.taskName("guard"))

    def enterTurnToGuardSpot(self):
        self.loop('walk')
        _, hpr = CGG.FactoryGuardPoints[self.guardKey]
        self.moveTrack = LerpHprInterval(self, duration = 1.0, hpr = hpr, startHpr = self.getHpr())
        self.moveTrack.setDoneEvent(self.uniqueName('TurnedToGuardSpot'))
        self.acceptOnce(self.moveTrack.getDoneEvent(), self.request, ['Guard'])
        self.moveTrack.start()

    def exitTurnToGuardSpot(self):
        if self.moveTrack:
            self.ignore(self.moveTrack.getDoneEvent())
            self.moveTrack.finish()
            self.moveTrack = None

    def enterSeekTarget(self, event):
        dialogue = random.choice(CGG.GuardDialog[event])
        self.setChat(dialogue)

        self.loop('walk')
        self.moveTrack = NPCLookInterval(self, base.localAvatar)
        self.moveTrack.setDoneEvent(self.uniqueName("SeekLocalAvatar"))
        self.acceptOnce(self.moveTrack.getDoneEvent(), self.request, ['TryToConfirmTarget'])
        self.moveTrack.start()

    def exitSeekTarget(self):
        if self.moveTrack:
            self.ignore(self.moveTrack.getDoneEvent())
            self.moveTrack.finish()
            self.moveTrack = None

    def enterTryToConfirmTarget(self):
        self.loop('neutral')
        base.taskMgr.add(self.__tryToConfirmTarget, self.uniqueName('TryToConfirmTarget'))

    def __tryToConfirmTarget(self, task):
        if task.time >= self.TRY_TO_CONFIRM_TIME:
            # Hmm, I guess it was nothing.
            chat = random.choice(CGG.GuardDialog['disregard'])
            self.setChat(chat)
            self.request('TurnToGuardSpot')
            return task.done
        # Let me see the target again, so I know it's actually something.
        if self.eyeNode.node().isInView(base.localAvatar.getPos(self.eyeNode)):
            # There he is!
            chat = random.choice(CGG.GuardDialog['spot'])
            self.setChat(chat)
            # TODO: Chase the toon.
            return task.done
        return task.cont

    def exitTryToConfirmTarget(self):
        base.taskMgr.remove(self.uniqueName('TryToConfirmTarget'))

    def uniqueName(self, name):
        return self.taskName(name)

    def taskName(self, name):
        return name + "-" + str(id(self))

    def setHealth(self, hp):
        self.health = hp

    def getHealth(self):
        return self.health

    def shot(self):
        dialogue = random.choice(CGG.GuardDialog['shot'])
        self.setChat(dialogue)

    def dead(self):
        self.animFSM.request('die')
        base.taskMgr.doMethodLater(self.GUARD_DIED_DELAY, self.__diedDone, self.diedTaskName)

    def __diedDone(self, task):
        self.gameWorld.deleteGuard(self)
        return task.done

    def generate(self):
        data = CIGlobals.SuitBodyData[self.SUIT]
        type = data[0]
        team = data[1]
        self.generateSuit(type, self.SUIT, team, self.MAX_HP, 0, False)
        base.taskMgr.add(self.__viewDistance, self.viewDistanceTaskName)
        self.setPythonTag('guard', self)
        self.eyeLight = Spotlight('eyes')
        self.eyeLens = PerspectiveLens()
        self.eyeLens.setMinFov(90.0 / (4./3.))
        self.eyeLight.setLens(self.eyeLens)
        self.eyeNode = self.headModel.attachNewNode(self.eyeLight)
        self.eyeNode.setZ(-5)
        self.eyeNode.setY(-4.5)
        self.request('Guard')

    def __viewDistance(self, task):
        # All the guards in the warehouse eat up a lot of frames.  This task will
        # hide the guard geometry if it's too far away.

        if self.getDistance(base.localAvatar) > self.MAX_VIEW_DISTANCE:
            if not self.isHidden():
                self.hide()
        else:
            if self.isHidden():
                self.show()

        task.delayTime = 1.0
        return task.again

    def disable(self):
        base.taskMgr.remove(self.diedTaskName)
        base.taskMgr.remove(self.viewDistanceTaskName)
        if self.eyeNode:
            self.eyeNode.removeNode()
            self.eyeNode = None
            self.eyeLens = None
            self.eyeLight = None
        self.viewDistanceTaskName = None
        self.guardKey = None
        self.gameWorld = None
        Suit.disable(self)
