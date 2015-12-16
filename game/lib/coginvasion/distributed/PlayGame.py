# Filename: PlayGame.py
# Created by:  blach (28Nov14)
# Updated by:  blach (12Dec15) - CogTropolis is now a complete new world.

from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.distributed.CogInvasionMsgTypes import *
from direct.fsm.ClassicFSM import ClassicFSM
from direct.fsm.State import State
from direct.fsm.StateData import StateData
from direct.directnotify.DirectNotifyGlobal import directNotify
from lib.coginvasion.hood import ZoneUtil
from panda3d.core import *

import OToontown
import CogTropolis

class PlayGame(StateData):
    notify = directNotify.newCategory('PlayGame')

    def __init__(self, parentFSM, doneEvent):
        StateData.__init__(self, "playGameDone")
        self.doneEvent = doneEvent
        self.fsm = ClassicFSM('PlayGame', [State('off', self.enterOff, self.exitOff, [CIGlobals.OToontown, CIGlobals.CogTropolis]),
                State(CIGlobals.OToontown, self.enterOToontown, self.exitOToontown),
                State(CIGlobals.CogTropolis, self.enterCogTropolis, self.exitCogTropolis)],
                'off', 'off')
        self.fsm.enterInitialState()
        self.parentFSM = parentFSM
        self.parentFSM.getStateNamed('playGame').addChild(self.fsm)
        self.worldDoneEvent = 'worldDone'
        self.world = None
        self.hood = None
        self.lastWorld = None
        self.suitManager = None

    def enter(self, hoodId, zoneId, avId, world):
        StateData.enter(self)
        whereName = ZoneUtil.getWhereName(zoneId)
        loaderName = ZoneUtil.getLoaderName(zoneId)
        self.fsm.request(world, [{'zoneId': zoneId,
            'hoodId': hoodId,
            'where': whereName,
            'how': 'teleportIn',
            'avId': avId,
            'shardId': None,
            'loader': loaderName,
            'world': world}])

    def exit(self):
        StateData.exit(self)

    def getPlace(self):
        if self.world:
            return self.world.getPlace()

    def setPlace(self, place):
        self.world.setPlace(place)

    def getCurrentWorldName(self):
        return self.fsm.getCurrentState().getName()

    def enterOff(self):
        pass

    def exitOff(self):
        pass

    def enterOToontown(self, requestStatus):
        self.acceptOnce(self.worldDoneEvent, self.handleWorldDone)
        self.world = OToontown.OToontown(self.fsm, self.worldDoneEvent)
        self.world.load()
        self.world.enter(requestStatus)

    def exitOToontown(self):
        self.lastWorld = CIGlobals.OToontown
        self.ignore(self.worldDoneEvent)
        self.world.exit()
        self.world.unload()
        self.world = None

    def enterCogTropolis(self, requestStatus):
        self.acceptOnce(self.worldDoneEvent, self.handleWorldDone)
        self.world = CogTropolis.CogTropolis(self.fsm, self.worldDoneEvent)
        self.world.load()
        self.world.enter(requestStatus)

    def exitCogTropolis(self):
        self.lastWorld = CIGlobals.CogTropolis
        self.ignore(self.worldDoneEvent)
        self.world.exit()
        self.world.unload()
        self.world = None

    def handleWorldDone(self):
        doneStatus = self.world.getDoneStatus()
        if doneStatus['zoneId'] == None or doneStatus['world'] == None:
            self.doneStatus = doneStatus
            messenger.send(self.doneEvent)
        else:
            self.fsm.request(doneStatus['world'], [doneStatus])
