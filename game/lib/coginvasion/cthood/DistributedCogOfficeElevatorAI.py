# Filename: DistributedCogOfficeElevatorAI.py
# Created by:  blach (15Dec15)

from direct.directnotify.DirectNotifyGlobal import directNotify

from DistributedElevatorAI import DistributedElevatorAI
from ElevatorConstants import *

class DistributedCogOfficeElevatorAI(DistributedElevatorAI):
    notify = directNotify.newCategory('DistributedCogOfficeElevatorAI')

    # In this class, self.bldg is the DistributedCogOfficeBattleAI associated with this elevator.

    def __init__(self, air, battle, index):
        DistributedElevatorAI.__init__(self, air, battle, 0, ELEVATOR_NORMAL)
        self.index = index

    def getIndex(self):
        return self.index

    def delete(self):
        del self.index
        DistributedElevatorAI.delete(self)
