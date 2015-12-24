# Filename: DistributedCogOfficeBattleAI.py
# Created by:  blach (15Dec15)

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.DistributedObjectAI import DistributedObjectAI
from direct.distributed.ClockDelta import globalClockDelta
from direct.fsm import ClassicFSM, State

from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.cog import SuitBank, Variant
from lib.coginvasion.cog.SuitType import SuitType
from lib.coginvasion.suit import CogBattleGlobals
from lib.coginvasion.hood import ZoneUtil
from DistributedCogOfficeElevatorAI import DistributedCogOfficeElevatorAI
from DistributedCogOfficeSuitAI import DistributedCogOfficeSuitAI
from CogOfficeConstants import *
from ElevatorConstants import *
import SuitBuildingGlobals

import random

RIDE_ELEVATOR_TIME = 6.5
FACE_OFF_TIME = 3.0
VICTORY_TIME = 5.0

class DistributedCogOfficeBattleAI(DistributedObjectAI):
    notify = directNotify.newCategory('DistributedCogOfficeBattleAI')
    UNIQUE_FLOORS = [1, 2, 3]

    def __init__(self, air, numFloors, dept, hood, bldg, exteriorZoneId):
        DistributedObjectAI.__init__(self, air)
        self.fsm = ClassicFSM.ClassicFSM('DistributedCogOfficeBattleAI', [State.State('off', self.enterOff, self.exitOff),
         State.State('floorIntermission', self.enterFloorIntermission, self.exitFloorIntermission),
         State.State('battle', self.enterBattle, self.exitBattle),
         State.State('rideElevator', self.enterRideElevator, self.exitRideElevator),
         State.State('faceOff', self.enterFaceOff, self.exitFaceOff),
         State.State('victory', self.enterVictory, self.exitVictory)], 'off', 'off')
        self.fsm.enterInitialState()
        self.hood = hood
        self.avatars = []
        self.bldg = bldg
        self.bldgDoId = self.bldg.doId
        self.exteriorZoneId = exteriorZoneId
        self.avId2suitsAttacking = {}
        self.spotTaken2suitId = {}
        self.guardSuits = []
        self.chairSuits = []
        self.numFloors = numFloors
        self.currentFloor = 0
        self.readyAvatars = []
        self.elevators = []
        self.drops = []
        self.entranceElevator = None
        self.exitElevator = None
        self.dept = dept
        if dept == 'c':
            self.deptClass = Dept.BOSS
        elif dept == 'l':
            self.deptClass = Dept.LAW
        elif dept == 's':
            self.deptClass = Dept.SALES
        elif dept == 'm':
            self.deptClass = Dept.CASH
            
    def getExteriorZoneId(self):
        return self.exteriorZoneId
    
    def getBldgDoId(self):
        return self.bldgDoId
            
    def iAmDead(self):
        avId = self.air.getAvatarIdFromSender()
        self.handleToonLeft(avId, 1)
        
    def handleToonLeft(self, avId, died = 0):
        if avId in self.avatars:
            self.avatars.remove(avId)
        self.b_setAvatars(self.avatars)
        if avId in self.avId2suitsAttacking.keys():
            del self.avId2suitsAttacking[avId]
        if died:
            toon = self.air.doId2do.get(avId)
            if toon:
                self.ignore(toon.getDeleteEvent())
        if len(self.avatars) == 0:
            self.resetEverything()
            self.bldg.elevator.b_setState('opening')
            
    def getDrops(self):
        return self.drops

    def getDept(self):
        return self.dept
        
    def getNumFloors(self):
        return self.numFloors

    def enterOff(self):
        pass

    def exitOff(self):
        pass
        
    def enterVictory(self):
        base.taskMgr.doMethodLater(VICTORY_TIME, self.victoryTask, self.uniqueName('victoryTask'))
        
    def victoryTask(self, task):
        while len(self.avatars) < 4:
            self.avatars.append(None)
        self.bldg.fsm.request('waitForVictors', [self.avatars])
        return task.done
        
    def exitVictory(self):
        base.taskMgr.remove(self.uniqueName('victoryTask'))
        
    def enterFaceOff(self):
        base.taskMgr.doMethodLater(FACE_OFF_TIME, self.faceOffTask, self.uniqueName('faceOffTask'))
        
    def faceOffTask(self, task):
        self.b_setState('battle')
        for suit in self.guardSuits:
            suit.toonsArrivedFromElevator()
        return task.done
        
    def exitFaceOff(self):
        base.taskMgr.remove(self.uniqueName('faceOffTask'))

    def enterRideElevator(self):
        base.taskMgr.doMethodLater(RIDE_ELEVATOR_TIME, self.rideElevatorTask, self.uniqueName('rideElevatorTask'))

    def rideElevatorTask(self, task):
        self.b_setState('faceOff')
        return task.done

    def exitRideElevator(self):
        base.taskMgr.remove(self.uniqueName('rideElevatorTask'))

    def enterBattle(self):
        self.elevators[0].b_setState('closing')
        self.elevators[1].b_setState('closed')

    def exitBattle(self):
        pass

    def enterFloorIntermission(self):
        self.elevators[1].b_setState('opening')
        self.elevators[0].b_setState('closed')
        self.readyAvatars = []
        
    def readyForNextFloor(self):
        avId = self.air.getAvatarIdFromSender()
        if not avId in self.readyAvatars:
            self.readyAvatars.append(avId)
        if len(self.readyAvatars) == len(self.avatars):
            self.startFloor(EXECUTIVE_FLOOR)

    def exitFloorIntermission(self):
        pass

    def setState(self, state):
        self.fsm.request(state)

    def d_setState(self, state):
        timestamp = globalClockDelta.getRealNetworkTime()
        self.sendUpdate('setState', [state, timestamp])

    def b_setState(self, state):
        self.d_setState(state)
        self.setState(state)

    def setAvatars(self, avatars):
        self.avatars = avatars
        self.avId2suitsAttacking = {avId: [] for avId in self.avatars}
        for avId in self.avatars:
            toon = self.air.doId2do.get(avId)
            if toon:
                self.ignore(toon.getDeleteEvent())
                self.acceptOnce(toon.getDeleteEvent(), self.handleToonLeft, [avId])

    def b_setAvatars(self, avatars):
        self.sendUpdate('setAvatars', [avatars])
        self.setAvatars(avatars)

    def getAvatars(self):
        return self.avatars

    def getCurrentFloor(self):
        return self.currentFloor

    def announceGenerate(self):
        DistributedObjectAI.announceGenerate(self)
        elevator0 = DistributedCogOfficeElevatorAI(self.air, self, 0)
        elevator0.generateWithRequired(self.zoneId)
        elevator0.b_setState('closed')
        self.elevators.append(elevator0)
        elevator1 = DistributedCogOfficeElevatorAI(self.air, self, 1, ELEVATOR_INT)
        elevator1.generateWithRequired(self.zoneId)
        elevator1.b_setState('closed')
        self.elevators.append(elevator1)
        
    def getPoints(self, name):
        if self.currentFloor in self.UNIQUE_FLOORS:
            dataList = POINTS[self.deptClass][self.currentFloor][name]
        else:
            dataList = POINTS[self.currentFloor][name]
        return dataList
        
    def cleanupDrops(self):
        for drop in self.drops:
            drop.requestDelete()
        self.drops = []
        
    def cleanupChairSuits(self):
        for suit in self.chairSuits:
            suit.disable()
            suit.requestDelete()
        self.chairSuits = []
        
    def cleanupGuardSuits(self):
        for suit in self.guardSuits:
            suit.disable()
            suit.requestDelete()
        self.guardSuits = []
        
    def cleanupElevators(self):
        for elevator in self.elevators:
            elevator.requestDelete()
        self.elevators = []
        
    def resetEverything(self):
        self.currentFloor = 0
        self.avId2suitsAttacking = {}
        self.spotTaken2suitId = {}
        self.cleanupDrops()
        self.cleanupChairSuits()
        self.cleanupGuardSuits()
        self.avatars = []
        self.readyAvatars = []
        for elevator in self.elevators:
            elevator.b_setState('closed')
        self.b_setState('off')
        
    def delete(self):
        self.fsm.requestFinalState()
        self.fsm = None
        self.currentFloor = None
        self.avId2suitsAttacking = None
        self.spotTaken2suitId = None
        self.cleanupDrops()
        self.drops = None
        self.cleanupChairSuits()
        self.chairSuits = None
        self.cleanupGuardSuits()
        self.guardSuits = None
        self.avatars = None
        self.readyAvatars = None
        self.cleanupElevators()
        self.elevators = None
        self.entanceElevator = None
        self.exitElevator = None
        self.hood = None
        self.numFloors = None
        self.dept = None
        self.deptClass = None
        self.bldg = None
        self.bldgDoId = None
        self.exteriorZoneId = None
        DistributedObjectAI.delete(self)
        
    def deadSuit(self, doId):
        foundIt = False
        for suit in self.guardSuits:
            if suit.doId == doId:
                self.guardSuits.remove(suit)
                foundIt = True
                break
        if foundIt and len(self.guardSuits) == 0:
            for suit in self.chairSuits:
                if suit.getHealth() > 0:
                    suit.allStandSuitsDead()
        if not foundIt:
            for suit in self.chairSuits:
                if suit.doId == doId:
                    self.chairSuits.remove(suit)
        
        if len(self.guardSuits) + len(self.chairSuits) == 0:
            if self.currentFloor < self.numFloors - 1:
                self.b_setState('floorIntermission')
            else:
                self.b_setState('victory')
                    
    def getHoodIndex(self):
        return CogBattleGlobals.hi2hi[self.hood]
        
    def makeSuit(self, guardPoint, isChair, boss = False):
        levelRange = SuitBuildingGlobals.buildingMinMax[CIGlobals.BranchZone2StreetName[ZoneUtil.getBranchZone(self.zoneId)]]
        availableSuits = []
        minLevel = levelRange[0]
        maxLevel = levelRange[1]
        if not boss:
            maxLevel -= 1
        else:
            minLevel = maxLevel
        level = random.randint(minLevel, maxLevel)
        for suit in SuitBank.getSuits():
            if level >= suit.getLevelRange()[0] and level <= suit.getLevelRange()[1] and suit.getDept() == self.deptClass:
                availableSuits.append(suit)
        if isChair:
            for suit in availableSuits:
                if suit.getSuitType() == SuitType.B:
                    availableSuits.remove(suit)
        plan = random.choice(availableSuits)
        suit = DistributedCogOfficeSuitAI(self.air, self, guardPoint, isChair, self.hood)
        suit.setManager(self)
        suit.generateWithRequired(self.zoneId)
        suit.d_setHood(suit.hood)
        suit.b_setLevel(level)
        variant = Variant.NORMAL
        if CogBattleGlobals.hi2hi[self.hood] == CogBattleGlobals.WaiterHoodIndex:
            variant = Variant.WAITER
        suit.b_setSuit(plan, variant)
        suit.b_setPlace(self.zoneId)
        suit.b_setName(plan.getName())
        return suit

    def startFloor(self, floorNum):
        for drop in self.drops:
            drop.requestDelete()
        self.drops = []
        self.currentFloor = floorNum
        wantBoss = False
        if self.currentFloor == self.numFloors - 1:
            wantBoss = True
        # Make the Cogs for this floor.
        chairPoints = self.getPoints('chairs')
        for point in chairPoints:
            suit = self.makeSuit(chairPoints.index(point), 1)
            self.chairSuits.append(suit)
        guardPoints = self.getPoints('guard')
        for point in guardPoints:
            isBoss = False
            if wantBoss:
                isBoss = True
                wantBoss = False
            suit = self.makeSuit(guardPoints.index(point), 0, isBoss)
            self.guardSuits.append(suit)
        self.sendUpdate('loadFloor', [self.currentFloor])
        self.elevators[0].sendUpdate('putToonsInElevator')
        self.b_setState('rideElevator')

    def readyToStart(self):
        avId = self.air.getAvatarIdFromSender()
        self.readyAvatars.append(avId)
        if len(self.readyAvatars) == len(self.avatars):
            # We're ready to go!
            self.startFloor(RECEPTION_FLOOR)
