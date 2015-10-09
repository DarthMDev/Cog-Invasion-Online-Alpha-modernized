# Filename: DistributedDeliveryGameAI.py
# Created by:  blach (04Oct15)

from direct.directnotify.DirectNotifyGlobal import directNotify

from lib.coginvasion.cog import SuitBank, Variant
from lib.coginvasion.minigame.DistributedMinigameAI import DistributedMinigameAI
from lib.coginvasion.globals import CIGlobals
from DistributedDeliveryTruckAI import DistributedDeliveryTruckAI
from DistributedDeliveryGameSuitAI import DistributedDeliveryGameSuitAI

import random

class DistributedDeliveryGameAI(DistributedMinigameAI):
    notify = directNotify.newCategory('DistributedDeliveryGameAI')

    NumBarrelsInEachTruck = 18
    SuitSpawnRateByNumPlayers = {1 : 0.55, 2 : 0.45, 3 : 0.35, 4 : 0.25}
    SuitBaseSpawnTime = 20.0

    def __init__(self, air):
        DistributedMinigameAI.__init__(self, air)
        self.trucks = []
        self.suits = []

    def announceGenerate(self):
        DistributedMinigameAI.announceGenerate(self)
        truck0 = DistributedDeliveryTruckAI(self.air, self, 0)
        truck0.setNumBarrels(self.NumBarrelsInEachTruck)
        truck0.generateWithRequired(self.zoneId)
        self.trucks.append(truck0)

    def allAvatarsReady(self):
        DistributedMinigameAI.allAvatarsReady(self)
        self.startSuitSpawner()

    def d_gameOver(self, winner = 0, winnerDoId = []):
        DistributedMinigameAI.d_gameOver(self, winner, winnerDoId)
        self.stopSuitSpawner()

    def getSuitSpawnTime(self):
        minTime = self.SuitBaseSpawnTime * self.SuitSpawnRateByNumPlayers[self.numPlayers]
        return random.randint(minTime, minTime + 3)

    def startSuitSpawner(self):
        time = self.getSuitSpawnTime()
        base.taskMgr.doMethodLater(time, self.__spawnSuit, self.uniqueName('suitSpawner'))

    def __spawnSuit(self, task):
        plan = random.choice(SuitBank.getSuits())
        level = 0
        variant = Variant.NORMAL
        suit = DistributedDeliveryGameSuitAI(self.air, self)
        suit.generateWithRequired(self.zoneId)
        suit.b_setLevel(level)
        suit.b_setSuit(plan, variant)
        suit.b_setPlace(self.zoneId)
        suit.b_setName(plan.getName())
        suit.b_setParent(CIGlobals.SPHidden)
        self.suits.append(suit)
        task.delayTime = self.getSuitSpawnTime()
        return task.again

    def stopSuitSpawner(self):
        base.taskMgr.remove(self.uniqueName('suitSpawner'))

    def delete(self):
        self.stopSuitSpawner()
        for truck in self.trucks:
            self.truck.requestDelete()
        self.trucks = None
        for suit in self.suits:
            self.suit.requestDelete()
        self.suits = None
