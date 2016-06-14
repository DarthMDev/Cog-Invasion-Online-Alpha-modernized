# Filename: BuildingSuitPlannerAI.py
# Created by:  blach (13Jun16)

from direct.directnotify.DirectNotifyGlobal import directNotify

from lib.coginvasion.cog import Dept
import SuitBuildingGlobals

import random

# One building suit planner per street.
class BuildingSuitPlannerAI:
    notify = directNotify.newCategory("BuildingSuitPlannerAI")

    def __init__(self, branchZone, streetName, hoodClass):
        self.branchZone = branchZone
        self.streetName = streetName
        self.hoodClass = hoodClass
        self.minBuildings = SuitBuildingGlobals.buildingMinMax[streetName][0]
        self.maxBuildings = SuitBuildingGlobals.buildingMinMax[streetName][1]
        self.numCogBuildings = 0
        self.__setupInitialBuildings()

    def __setupInitialBuildings(self):

        for _ in xrange(self.minBuildings):

            if self.numCogBuildings >= self.minBuildings:
                break

            bldg = random.choice(self.hoodClass.buildings[self.branchZone])
            if bldg.fsm.getCurrentState().getName() == 'toon':
                bldg.suitTakeOver(random.choice([Dept.SALES, Dept.CASH, Dept.LAW, Dept.BOSS]), 0, 0)
                self.numCogBuildings += 1
