# Filename: DistributedTakeOverSuitAI.py
# Created by:  blach (14Jun16)

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.ClockDelta import globalClockDelta
from direct.interval.IntervalGlobal import Sequence, Wait, Func
from direct.fsm import ClassicFSM, State

from lib.coginvasion.avatar.DistributedAvatarAI import DistributedAvatarAI
from lib.coginvasion.cog.DistributedSuitAI import DistributedSuitAI
from lib.coginvasion.cog import SuitBank
from lib.coginvasion.globals import CIGlobals

class DistributedTakeOverSuitAI(DistributedSuitAI):
    notify = directNotify.newCategory("DistributedTakeOverSuitAI")

    def __init__(self, air, planner, bldg, doorDoId):
        DistributedSuitAI.__init__(self, air)
        self.planner = planner
        self.bldg = bldg
        self.doorDoId = doorDoId
        self.takeOverTrack = None
        self.state = 'off'
        self.stateTimestamp = 0
        self.setAllowHits(False)

    def requestStateAndTimestamp(self):
        avId = self.air.getAvatarIdFromSender()
        self.sendUpdateToAvatarId('stateAndTimestamp', self.getState())

    def setState(self, state):
        self.state = state

    def d_setState(self, state):
        self.stateTimestamp = globalClockDelta.getRealNetworkTime()
        self.sendUpdate('setState', [state, self.stateTimestamp])

    def b_setState(self, state):
        self.d_setState(state)
        self.setState(state)

    def getState(self):
        return [self.state, self.stateTimestamp]

    def getDoorDoId(self):
        return self.doorDoId

    def closeSuit(self):
        DistributedSuitAI.closeSuit(self, False)

    def monitorHealth(self, task):
        if self.isDead():
            # No! I'm dead! I lost my building!
            self.bldg.takenBySuit = False

            self.sendUpdate('interruptTakeOver')
            if self.takeOverTrack:
                self.takeOverTrack.pause()
                self.takeOverTrack = None
        return DistributedSuitAI.monitorHealth(self, task)

    def disable(self):
        if self.takeOverTrack:
            self.takeOverTrack.pause()
            self.takeOverTrack = None
        DistributedSuitAI.disable(self)

    def announceGenerate(self):
        DistributedAvatarAI.announceGenerate(self)
        self.clearTrack()

        # Let's set the combo data task name and start the task.
        self.comboDataTaskName = self.uniqueName('clearComboData')
        taskMgr.add(self.clearComboData, self.comboDataTaskName)
        taskMgr.add(self.monitorHealth, self.uniqueName('monitorHealth'))

    def initiateTakeOver(self):
        self.b_setState('takeOver')
        self.takeOverTrack = Sequence(
            Wait(6.834),
            Func(self.setAllowHits, True),
            Wait(2.8),
            Func(self.bldg.door.requestEnter, True),
            Wait(2.5),
            Func(self.setAllowHits, False),
            Wait(2.5),
            Func(self.planner.takeOverBuilding, self.bldg, self.suitPlan.getDept(), self.level),
            Func(self.planner.deadSuit, self.doId),
            Func(self.disable),
            Func(self.requestDelete)
        )
        self.takeOverTrack.start()
