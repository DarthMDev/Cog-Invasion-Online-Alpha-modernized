# Filename: DistributedCogOfficeElevator.py
# Created by:  blach (15Dec15)

from direct.directnotify.DirectNotifyGlobal import directNotify

from DistributedElevator import DistributedElevator

class DistributedCogOfficeElevator(DistributedElevator):
    notify = directNotify.newCategory('DistributedCogOfficeElevator')

    # In this class, self.bldg is the DistributedCogOfficeBattle associated with this elevator.

    def __init__(self, cr):
        DistributedElevator.__init__(self, cr)
        self.index = None

    def setIndex(self, index):
        self.index = index

    def getIndex(self):
        return self.index

    def onDoorCloseFinish(self):
        base.transitions.fadeScreen(1)
        self.bldg.d_readyForNextFloor()

    def getElevatorModel(self):
        return self.bldg.elevatorModels[self.index]
