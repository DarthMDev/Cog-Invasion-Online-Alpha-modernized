# Filename: DistributedCogOfficeBattleAI.py
# Created by:  blach (15Dec15)

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.DistributedObjectAI import DistributedObjectAI
from direct.fsm import ClassicFSM, State

from DistributedCogOfficeElevatorAI import DistributedCogOfficeElevatorAI

class DistributedCogOfficeBattleAI(DistributedObjectAI):
    notify = directNotify.newCategory('DistributedCogOfficeBattleAI')

    def __init__(self, air, avatars, numFloors):
        DistributedObjectAI.__init__(self, air)
        self.avatars = avatars
        self.numFloors = numFloors
        self.currentFloor = 0
        self.readyAvatars = []
        self.entranceElevator = None
        self.exitElevator = None

    def getAvatars(self):
        return self.avatars

    def getCurrentFloor(self):
        return self.currentFloor

    def announceGenerate(self):
        DistributedObjectAI.announceGenerate(self)

    def readyToStart(self):
        avId = self.air.getAvatarIdFromSender()
        self.readyAvatars.append(avId)
        if len(self.readyAvatars) == len(self.avatars):
            # We're ready to go!
            self.currentFloor = 0
            self.sendUpdate('loadFloor', [self.currentFloor])
            self.b_setState('rideElevator')
