# Filename: DistributedCogOfficeSuitAI.py
# Created by:  blach (17Dec15)

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.fsm import ClassicFSM, State
from direct.distributed.ClockDelta import globalClockDelta

from lib.coginvasion.cog.DistributedSuitAI import DistributedSuitAI
from lib.coginvasion.globals import CIGlobals
from CogOfficeSuitBrainAI import CogOfficeSuitBrainAI
from CogOfficeConstants import POINTS

CHAIR_2_BATTLE_TIME = 9.0

class DistributedCogOfficeSuitAI(DistributedSuitAI):
    notify = directNotify.newCategory('DistributedSuitAI')
    
    def __init__(self, air, battle, guardPoint, flyToPoint, isChair, hood):
        DistributedSuitAI.__init__(self, air)
        self.hood = hood
        self.battle = battle
        self.battleDoId = self.battle.doId
        self.guardPoint = guardPoint
        self.battleStartPoint = flyToPoint
        self.isChair = isChair
        self.fsm = ClassicFSM.ClassicFSM('DistributedCogOfficeSuitAI', [State.State('off', self.enterOff, self.exitOff),
         State.State('guard', self.enterGuard, self.exitGuard, ['think']),
         State.State('think', self.enterThink, self.exitThink, ['off']),
         State.State('chair', self.enterChair, self.exitChair, ['chair2battle']),
         State.State('chair2battle', self.enterChair2Battle, self.exitChair2Battle, ['think'])], 'off', 'off')
        self.fsm.enterInitialState()
        self.stateExtraArgs = []
        
    def canGetHit(self):
        return (not self.isChair) or (self.isChair and self.fsm.getCurrentState().getName() == 'think')
        
    def getBattleDoId(self):
        return self.battleDoId
        
    def getPoints(self, name):
        if self.battle.currentFloor in self.battle.UNIQUE_FLOORS:
            points = POINTS[self.battle.deptClass][self.battle.currentFloor][name]
        else:
            points = POINTS[self.battle.currentFloor][name]
        return points
        
    def enterOff(self):
        pass
        
    def exitOff(self):
        pass
        
    def enterGuard(self):
        points = self.getPoints('guard')
        self.setPos(points[self.guardPoint][0], points[self.guardPoint][1], points[self.guardPoint][2])
        self.b_setAnimState('neutral')
        
    def toonsArrivedFromElevator(self):
        self.b_setState('think')
        
    def exitGuard(self):
        pass
        
    def enterThink(self):
        self.brain.startThinking()
        
    def exitThink(self):
        if self.brain is not None:
            self.brain.stopThinking()
        
    def enterChair(self):
        points = self.getPoints('chairs')
        self.setPos(points[self.guardPoint][0], points[self.guardPoint][1], points[self.guardPoint][2])
        self.b_setAnimState('sit')
        
    def allStandSuitsDead(self):
        self.b_setState('chair2battle', [self.battleStartPoint])
        
    def exitChair(self):
        pass
        
    def enterChair2Battle(self):
        taskMgr.remove(self.uniqueName('monitorHealth'))
        taskMgr.doMethodLater(CHAIR_2_BATTLE_TIME, self.chair2BattleTask, self.uniqueName('chair2BattleTask'))
        points = self.getPoints('battle')
        point = points[self.battleStartPoint]
        self.setPosHpr(*point)
        
    def chair2BattleTask(self, task):
        self.b_setState('think')
        return task.done
        
    def exitChair2Battle(self):
        taskMgr.add(self.monitorHealth, self.uniqueName('monitorHealth'))
        
    def setState(self, state, extraArgs = []):
        self.fsm.request(state)
        self.stateExtraArgs = extraArgs
        
    def b_setState(self, state, extraArgs = []):
        self.d_setState(state, extraArgs)
        self.setState(state, extraArgs)
        
    def d_setState(self, state, extraArgs):
        timestamp = globalClockDelta.getRealNetworkTime()
        self.sendUpdate('setState', [state, extraArgs, timestamp])
        
    def getState(self):
        return [self.fsm.getCurrentState().getName(), self.stateExtraArgs, globalClockDelta.getRealNetworkTime()]
        
    def spawn(self):
        self.brain = CogOfficeSuitBrainAI(self)
        if not self.isChair:
            self.b_setState('guard', [self.guardPoint])
        else:
            self.b_setState('chair', [self.guardPoint])
        self.b_setParent(CIGlobals.SPRender)
        taskMgr.add(self.monitorHealth, self.uniqueName('monitorHealth'))
            
    def delete(self):
        del self.guardPoint
        del self.isChair
        self.fsm.requestFinalState()
        del self.fsm
        del self.battle
        del self.stateExtraArgs
        DistributedSuitAI.delete(self)
