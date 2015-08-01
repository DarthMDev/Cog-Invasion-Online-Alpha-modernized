"""

  Filename: HoodAI.py
  Created by: blach (20Dec14)

"""

from lib.coginvasion.distributed.HoodMgr import HoodMgr
from direct.directnotify.DirectNotifyGlobal import directNotify
from lib.coginvasion.hood import TreasureGlobals
from lib.coginvasion.hood.SZTreasurePlannerAI import SZTreasurePlannerAI
import ZoneUtil
from lib.coginvasion.dna.DNAParser import *
import DistributedDoorAI
import DistributedToonInteriorAI
import DistributedCinemaInteriorAI
import DistributedToonHQInteriorAI
import CinemaGlobals

class HoodAI:
    notify = directNotify.newCategory("HoodAI")
    notify.setInfo(True)

    def __init__(self, air, zoneId, hood):
        self.air = air
        self.zoneId = zoneId
        self.hood = hood
        self.hoodMgr = HoodMgr()
        self.air.hoods[zoneId] = self
        self.treasurePlanner = None
        self.interiors = []
        self.exteriorDoors = []

    def startup(self):
        self.createTreasurePlanner()

        self.notify.info("Creating objects in hood %s.." % self.hood)
        interiorZoneAllocator = UniqueIdAllocator(self.zoneId + 400, self.zoneId + 999)
        for dnaFile in self.dnaFiles:
            zoneId = 0
            if 'sz' in dnaFile:
                zoneId = self.zoneId
            else:
                for segment in dnaFile.split('_'):
                    if segment.endswith('dna'):
                        segment = segment[:4]
                        if segment.isdigit():
                            zoneId = int(segment)
                            break
            dnaStore = DNAStorage()
            dnaData = loadDNAFileAI(dnaStore, dnaFile)
            self.air.dnaStoreMap[zoneId] = dnaStore
            self.air.dnaDataMap[zoneId] = dnaData
            for block in dnaStore.blockZones.keys():
                exteriorZone = dnaStore.blockZones[block]
                interiorZone = (ZoneUtil.getBranchZone(zoneId) - (ZoneUtil.getBranchZone(zoneId) % 100)) + 500 + block
                if dnaStore.blockBuildingTypes.get(block, None) == None:
                    interior = DistributedToonInteriorAI.DistributedToonInteriorAI(self.air, block, exteriorZone)
                    interior.generateWithRequired(interiorZone)
                    door = DistributedDoorAI.DistributedDoorAI(self.air, block, interiorZone, 1)
                    door.generateWithRequired(exteriorZone)
                    self.exteriorDoors.append(door)
                    self.interiors.append(interior)
                elif dnaStore.blockBuildingTypes.get(block) == 'cinema':
                    cinemaIndex = CinemaGlobals.Zone2Block2CinemaIndex[zoneId][block]
                    interior = DistributedCinemaInteriorAI.DistributedCinemaInteriorAI(
                        self.air, block, exteriorZone, cinemaIndex)
                    interior.generateWithRequired(interiorZone)
                    door = DistributedDoorAI.DistributedDoorAI(self.air, block, interiorZone, 1)
                    door.generateWithRequired(exteriorZone)
                    self.exteriorDoors.append(door)
                    self.interiors.append(interior)
                elif dnaStore.blockBuildingTypes.get(block) == 'hq':
                    interior = DistributedToonHQInteriorAI.DistributedToonHQInteriorAI(
                        self.air, block, exteriorZone)
                    interior.generateWithRequired(interiorZone)
                    door0 = DistributedDoorAI.DistributedDoorAI(self.air, block, interiorZone, 3)
                    door0.generateWithRequired(exteriorZone)
                    door1 = DistributedDoorAI.DistributedDoorAI(self.air, block, interiorZone, 3, 1)
                    door1.generateWithRequired(exteriorZone)
                    self.exteriorDoors.append(door0)
                    self.exteriorDoors.append(door1)
                    self.interiors.append(interior)
        del self.dnaFiles

    def createTreasurePlanner(self):
        spawnInfo = TreasureGlobals.treasureSpawns.get(self.zoneId)
        if not spawnInfo: return
        treasureType, healAmount, spawnPoints, spawnRate, maxTreasures = spawnInfo
        self.treasurePlanner = SZTreasurePlannerAI(self.air,
            self.zoneId, treasureType, healAmount, spawnPoints,
            spawnRate, maxTreasures)
        self.treasurePlanner.start()

    def shutdown(self):
        for obj in self.air.doId2do.values():
            obj.requestDelete()
        if self.treasurePlanner:
            self.treasurePlanner.stop()
            self.treasurePlanner.deleteAllTreasuresNow()
            self.treasurePlanner = None
        del self.zoneId
        del self.hood
        del self.hoodMgr
        del self.air.hoods[self]
        del self.air
