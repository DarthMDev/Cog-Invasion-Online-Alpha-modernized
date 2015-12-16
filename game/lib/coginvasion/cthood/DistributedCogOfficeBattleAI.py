# Filename: DistributedCogOfficeBattleAI.py
# Created by:  blach (15Dec15)

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.DistributedObjectAI import DistributedObjectAI
from direct.fsm import ClassicFSM, State

from DistributedCogOfficeElevatorAI import DistributedCogOfficeElevatorAI

class DistributedCogOfficeBattleAI(DistributedObjectAI):
    notify = directNotify.newCategory('DistributedCogOfficeBattleAI')

    def __init__(self, air, raiders, numFloors):
        DistributedObjectAI.__init__(self, air)
        self.raiders = raiders
        self.numFloors = numFloors
        self.readyAvatars = []
        self.entranceElevator = None
        self.exitElevator = None

    def announceGenerate(self):
        DistributedObjectAI.announceGenerate(self)
