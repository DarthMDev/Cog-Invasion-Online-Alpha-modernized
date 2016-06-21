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
from lib.coginvasion.gags.GagType import GagType
from lib.coginvasion.battle.DistributedGagBarrelAI import DistributedGagBarrelAI
from DistributedCogOfficeElevatorAI import DistributedCogOfficeElevatorAI
from DistributedCogOfficeSuitAI import DistributedCogOfficeSuitAI
from CogOfficeConstants import *
from ElevatorConstants import *
import SuitBuildingGlobals

import random

RIDE_ELEVATOR_TIME = 6.5
FACE_OFF_TIME = 7.5
VICTORY_TIME = 5.0

class DistributedCogOfficeBattleAI(DistributedObjectAI):
    notify = directNotify.newCategory('DistributedCogOfficeBattleAI')
    UNIQUE_FLOORS = []

    def __init__(self, air, numFloors, dept, hood, bldg, exteriorZoneId):
        DistributedObjectAI.__init__(self, air)
        self.fsm = ClassicFSM.ClassicFSM('DistributedCogOfficeBattleAI', [State.State('off', self.enterOff, self.exitOff),
         State.State('floorIntermission', self.enterFloorIntermission, self.exitFloorIntermission),
         State.State('bldgComplete', self.enterBldgComplete, self.exitBldgComplete),
         State.State('battle', self.enterBattle, self.exitBattle),
         State.State('rideElevator', self.enterRideElevator, self.exitRideElevator),
         State.State('faceOff', self.enterFaceOff, self.exitFaceOff),
         State.State('victory', self.enterVictory, self.exitVictory)], 'off', 'off')
        self.fsm.enterInitialState()
        self.hood = hood
        self.avIds = []
        self.bldg = bldg
        self.bldgDoId = self.bldg.doId
        self.exteriorZoneId = exteriorZoneId
        self.toonId2suitsTargeting = {}
        self.guardSuits = []
        self.chairSuits = []
        self.roomsVisited = []
        self.numFloors = numFloors
        self.currentFloor = 0
        self.currentRoom = ""
        self.readyAvatars = []
        self.elevators = []
        self.drops = []
        self.barrels = []
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

    # Sent by the client when they enter a certain floor section
    def enterSection(self, sectionIndex):
        # Get the guard suits associated with this section
        for guard in self.getGuardsBySection(sectionIndex):
            # Make sure this guard isn't already activated
            if not guard.isActivated():
               # Activate this guard!
                guard.activate()

    def iAmDead(self):
        avId = self.air.getAvatarIdFromSender()
        self.handleToonLeft(avId, 1)

    def handleToonLeft(self, avId, died = 0):
        if self.avIds is None:
            return

        if avId in self.avIds:
            self.avIds.remove(avId)
        self.b_setAvatars(self.avIds)

        if avId in self.toonId2suitsTargeting.keys():
            del self.toonId2suitsTargeting[avId]

        if len(self.avIds) > 0:
            allSuits = self.guardSuits + self.chairSuits
            for suit in allSuits:
                if suit.isActivated():
                    if not suit.brain is None and not suit.brain.currentBehavior is None and suit.brain.currentBehavior.targetId == avId:
                        # Uh oh, this cog was targeting this toon.
                        # We have to make them pick a new target.
                        suit.brain.currentBehavior.pickTarget()

        if died:
            toon = self.air.doId2do.get(avId)
            if toon:
                self.ignore(toon.getDeleteEvent())

        if len(self.avIds) == 0:
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
        while len(self.avIds) < 4:
            self.avIds.append(None)
        self.bldg.fsm.request('waitForVictors', [self.avIds])
        return task.done

    def exitVictory(self):
        base.taskMgr.remove(self.uniqueName('victoryTask'))

    def enterFaceOff(self):
        base.taskMgr.doMethodLater(FACE_OFF_TIME, self.faceOffTask, self.uniqueName('faceOffTask'))

    def faceOffTask(self, task):
        self.b_setState('battle')

        # Activate all of the guards in section 0 (the first section).
        for guard in self.getGuardsBySection(0):
            guard.activate()

        return task.done

    def exitFaceOff(self):
        base.taskMgr.remove(self.uniqueName('faceOffTask'))

    def enterRideElevator(self):
        base.taskMgr.doMethodLater(RIDE_ELEVATOR_TIME, self.rideElevatorTask, self.uniqueName('rideElevatorTask'))

    def rideElevatorTask(self, task):
        guards = list(self.getGuardsBySection(0))
        guards.sort(key = lambda guard: guard.getLevel(), reverse = True)
        guard = guards[0]

        suitId = guard.doId
        taunts = CIGlobals.SuitFaceoffTaunts[guard.suitPlan.getName()]
        tauntIndex = taunts.index(random.choice(taunts))

        self.sendUpdate('doFaceoff', [suitId, tauntIndex, globalClockDelta.getRealNetworkTime()])

        self.setState('faceOff')

        return task.done

    def exitRideElevator(self):
        base.taskMgr.remove(self.uniqueName('rideElevatorTask'))

    def enterBattle(self):
        self.elevators[0].b_setState('closing')
        self.elevators[1].b_setState('closed')

    def exitBattle(self):
        pass

    def enterBldgComplete(self):
        self.enterFloorIntermission()

    def exitBldgComplete(self):
        pass

    def enterFloorIntermission(self):
        self.sendUpdate('openRestockDoors')
        self.elevators[1].b_setState('opening')
        self.elevators[0].b_setState('closed')
        self.readyAvatars = []

    def readyForNextFloor(self):
        avId = self.air.getAvatarIdFromSender()
        if not avId in self.readyAvatars:
            self.readyAvatars.append(avId)
        if len(self.readyAvatars) == len(self.avIds):
            floors = numFloors2roomsVisited[self.numFloors]
            newFloor = floors[self.currentFloor + 1]
            if newFloor == RANDOM_FLOOR:
                # Let's choose a random middle floor to go to!
                print "Choosing random floor"
                choices = []
                for floor in middleFloors:
                    if not floor in self.roomsVisited:
                        print "Added floor to choices: " + floor
                        choices.append(floor)
                    else:
                        print "Room {0} already visited.".format(floor)
                if len(choices) == 0:
                    print "No choices, choosing randomly from middleFloors."
                    # We haven't finished making all of the floors yet, go to one we have already been to.
                    newFloor = random.choice(middleFloors)
                else:
                    newFloor = random.choice(choices)
            print 'Chose floor: ' + newFloor
            self.startFloor(self.currentFloor + 1, newFloor)

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
        self.avIds = avatars
        self.toonId2suitsTargeting = {avId: [] for avId in self.avIds}
        for avId in self.avIds:
            toon = self.air.doId2do.get(avId)
            if toon:
                self.ignore(toon.getDeleteEvent())
                self.acceptOnce(toon.getDeleteEvent(), self.handleToonLeft, [avId])

    def b_setAvatars(self, avatars):
        self.sendUpdate('setAvatars', [avatars])
        self.setAvatars(avatars)

    def getAvatars(self):
        return self.avIds

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
        #self.resetBattlePoints()

    def resetBattlePoints(self):
        self.availableBattlePoints = self.getPoints('battle')

    def getPoints(self, name):
        if self.currentRoom in self.UNIQUE_FLOORS:
            dataList = POINTS[self.deptClass][self.currentRoom][name]
        else:
            dataList = POINTS[self.currentRoom][name]
        return dataList

    def cleanupBarrels(self):
        for barrel in self.barrels:
            barrel.requestDelete()
        self.barrels = []

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
        self.toonId2suitsTargeting = {}
        self.spotTaken2suitId = {}
        self.cleanupDrops()
        self.cleanupChairSuits()
        self.cleanupGuardSuits()
        self.cleanupBarrels()
        self.avIds = []
        self.readyAvatars = []
        for elevator in self.elevators:
            elevator.b_setState('closed')
        self.b_setState('off')

    def delete(self):
        self.fsm.requestFinalState()
        self.fsm = None
        for avId in self.avIds:
            toon = self.air.doId2do.get(avId)
            if toon:
                self.ignore(toon.getDeleteEvent())
        self.currentFloor = None
        self.toonId2suitsTargeting = None
        self.spotTaken2suitId = None
        self.cleanupDrops()
        self.drops = None
        self.cleanupBarrels()
        self.cleanupChairSuits()
        self.chairSuits = None
        self.cleanupGuardSuits()
        self.guardSuits = None
        self.avIds = None
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
        self.availableBattlePoints = None
        DistributedObjectAI.delete(self)

    def suitHPAtZero(self, doId):
        foundIt = False
        section = 0
        for suit in self.guardSuits:
            if suit.doId == doId:
                section = suit.floorSection
                foundIt = True
                break
        if foundIt and len(self.getGuardsBySection(section, excludeIfZeroHP = 1)) <= 2:
            for suit in self.getChairsBySection(section):
                if suit.getHealth() > 0:
                    suit.allStandSuitsDead()

    def deadSuit(self, doId):
        foundIt = False
        section = 0
        for suit in self.guardSuits:
            if suit.doId == doId:
                section = suit.floorSection
                self.guardSuits.remove(suit)
                foundIt = True
                break
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

    def makeSuit(self, initPointData, isChair, boss = False):
        bldgInfo = SuitBuildingGlobals.buildingInfo[self.hood]
        if self.currentFloor < self.numFloors - 1:
            levelRange = bldgInfo[SuitBuildingGlobals.LEVEL_RANGE]
        else:
            levelRange = bldgInfo[SuitBuildingGlobals.BOSS_LEVEL_RANGE]
        battlePoint = None
        level, availableSuits = SuitBank.chooseLevelAndGetAvailableSuits(levelRange, self.deptClass, boss)
        if isChair:
            for suit in availableSuits:
                if suit.getSuitType() == SuitType.B:
                    availableSuits.remove(suit)

        plan = random.choice(availableSuits)
        suit = DistributedCogOfficeSuitAI(self.air, self, initPointData, isChair, self.hood)
        suit.setManager(self)
        suit.generateWithRequired(self.zoneId)
        suit.d_setHood(suit.hood)
        suit.b_setLevel(level)
        variant = Variant.NORMAL
        hood = self.hood
        if self.hood == CIGlobals.ToontownCentral:
            hood = CIGlobals.BattleTTC
        if CogBattleGlobals.hi2hi[hood] == CogBattleGlobals.WaiterHoodIndex:
            variant = Variant.WAITER
        suit.b_setSuit(plan, variant)
        suit.b_setPlace(self.zoneId)
        suit.b_setName(plan.getName())
        return suit

    def getGuardsBySection(self, sectionIndex, excludeIfZeroHP = 0):
        guards = []
        for guard in self.guardSuits:
            if guard.floorSection == sectionIndex:
                if not excludeIfZeroHP or (excludeIfZeroHP and not guard.isDead()):
                    guards.append(guard)
        return guards

    def getChairsBySection(self, sectionIndex):
        chairs = []
        for chair in self.chairSuits:
            if chair.floorSection == sectionIndex:
                chairs.append(chair)
        return chairs

    def startFloor(self, floorNum, room):
        # Clean up barrels and drops from the last floor.
        self.cleanupBarrels()
        self.cleanupDrops()

        self.currentFloor = floorNum
        self.currentRoom = room
        if room not in self.roomsVisited:
            self.roomsVisited.append(room)
        wantBoss = False
        if self.currentFloor == self.numFloors - 1:
            wantBoss = True
        # Make the Cogs for this floor.

        sectionRange = SuitBuildingGlobals.buildingInfo[self.hood][SuitBuildingGlobals.GUARDS_PER_SECTION]

        guardSection2NumInSection = {}
        guardPoints = self.getPoints('guard')
        maxInThisSection = 0
        for point in guardPoints:
            isBoss = False
            if wantBoss:
                isBoss = True
                wantBoss = False
            section = point[0]
            if not guardSection2NumInSection.has_key(section):
                guardSection2NumInSection[section] = 0
                if section == 0:
                    # Always make section 0 have 4 guards.
                    maxInThisSection = 4
                else:
                    maxInThisSection = random.randint(sectionRange[0], sectionRange[1])
            if guardSection2NumInSection[section] < maxInThisSection:
                suit = self.makeSuit([guardPoints.index(point), point], 0, isBoss)
                self.guardSuits.append(suit)
                guardSection2NumInSection[section] += 1

        chairPoints = self.getPoints('chairs')
        chairSection2NumInSection = {}
        maxInThisSection = 0
        for point in chairPoints:
            section = point[0]
            if not chairSection2NumInSection.has_key(section):
                chairSection2NumInSection[section] = 0
                if guardSection2NumInSection[section] == 0:
                    # Don't make any chairs in this section if their are no guards in the same section!!!
                    maxInThisSection = 0
                else:
                    maxInThisSection = random.randint(sectionRange[0], sectionRange[1])
            if chairSection2NumInSection[section] < maxInThisSection:
                suit = self.makeSuit([chairPoints.index(point), point], 1)
                self.chairSuits.append(suit)
                chairSection2NumInSection[section] += 1

        # Let's make the barrels.
        barrelPoints = self.getPoints('barrels')
        if barrelPoints:
            barrelPoints = list(barrelPoints)
            # This is the data for each gag track.
            # The list inside of the dictionary value is a list of gagIds that
            # can be chosen to represent the gag track.
            # The second value is the percentage chance that it'll be chosen.
            trackGags = {
                GagType.SOUND : [[18, 20], 20],
                GagType.SQUIRT : [[31, 4], 38],
                GagType.DROP : [[8, 30], 25]
            }
            maxBarrels = 3

            for _ in xrange(maxBarrels):
                locationData = random.choice(barrelPoints)
                barrelPoints.remove(locationData)

                position = locationData[0]
                hpr = locationData[1]

                gagIcon = random.choice([0, 2])
                track = GagType.THROW

                for track, data in trackGags.iteritems():
                    if random.randrange(0, 100) <= data[1]:
                        gagIcon = random.choice(data[0])
                        track = track
                        break
                del trackGags[track]

                barrel = DistributedGagBarrelAI(gagIcon, self.air, loadoutOnly = True)
                barrel.generateWithRequired(self.zoneId)
                barrel.b_setPosHpr(position[0], position[1], position[2], hpr[0], hpr[1], hpr[2])
                self.barrels.append(barrel)

        # We need to wait for a response from all players telling us that they finished loading the floor.
        # Once they all finish loading the floor, we ride the elevator.
        self.readyAvatars = []
        self.sendUpdate('loadFloor', [self.currentFloor, self.currentRoom])
        self.elevators[0].sendUpdate('putToonsInElevator')

    # Sent by the player telling us that they have finished loading/setting up the floor.
    def loadedFloor(self):
        avId = self.air.getAvatarIdFromSender()
        if not avId in self.readyAvatars:
            self.readyAvatars.append(avId)
        if len(self.readyAvatars) == len(self.avIds):
            # Let's ride!
            self.b_setState('rideElevator')

    def readyToStart(self):
        avId = self.air.getAvatarIdFromSender()
        self.readyAvatars.append(avId)
        if len(self.readyAvatars) == len(self.avIds):
            # We're ready to go!
            self.startFloor(0, numFloors2roomsVisited[self.numFloors][0])
