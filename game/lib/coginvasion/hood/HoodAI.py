"""

  Filename: HoodAI.py
  Created by: blach (20Dec14)

"""

from lib.coginvasion.distributed.HoodMgr import HoodMgr
from direct.directnotify.DirectNotifyGlobal import directNotify
from lib.coginvasion.hood import TreasureGlobals
from lib.coginvasion.hood.SZTreasurePlannerAI import SZTreasurePlannerAI
from . import ZoneUtil
from lib.coginvasion.dna.DNALoader import *
from . import DistributedDoorAI
from . import DistributedToonInteriorAI
from . import DistributedCinemaInteriorAI
from . import DistributedToonHQInteriorAI
from . import DistributedTailorInteriorAI
from . import DistributedGagShopInteriorAI
from . import DistributedBuildingAI
from . import CinemaGlobals
from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.cogoffice.BuildingSuitPlannerAI import BuildingSuitPlannerAI

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
        self.buildings = {}
        self.buildingPlanners = {}

    def startup(self):
        self.createTreasurePlanner()

        self.notify.info("Creating objects in hood %s.." % self.hood)
        interiorZoneAllocator = UniqueIdAllocator(self.zoneId + 400, self.zoneId + 999)
        for dnaFile in self.dnaFiles:
            zoneId = 0
            isSZ = False
            if 'sz' in dnaFile:
                isSZ = True
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
            self.buildings[zoneId] = []
            blockZoneByNumber = {}
            for i in range(dnaStore.get_num_block_numbers()):
                blockNumber = dnaStore.get_block_number_at(i)
                blockZoneByNumber[blockNumber] = dnaStore.get_zone_from_block_number(blockNumber)
            for block, exteriorZone in list(blockZoneByNumber.items()):
                buildingType = dnaStore.get_block_building_type(block)
                interiorZone = (ZoneUtil.getBranchZone(zoneId) - (ZoneUtil.getBranchZone(zoneId) % 100)) + 500 + block
                if isSZ or (not isSZ and buildingType in ['hq']):
                    if not buildingType:
                        interior = DistributedToonInteriorAI.DistributedToonInteriorAI(self.air, block, exteriorZone)
                        interior.generateWithRequired(interiorZone)
                        door = DistributedDoorAI.DistributedDoorAI(self.air, block, interiorZone, 1)
                        door.generateWithRequired(exteriorZone)
                        self.exteriorDoors.append(door)
                        self.interiors.append(interior)
                    elif buildingType == 'cinema':
                        cinemaIndex = CinemaGlobals.Zone2Block2CinemaIndex[zoneId][block]
                        interior = DistributedCinemaInteriorAI.DistributedCinemaInteriorAI(
                            self.air, block, exteriorZone, cinemaIndex)
                        interior.generateWithRequired(interiorZone)
                        door = DistributedDoorAI.DistributedDoorAI(self.air, block, interiorZone, 1)
                        door.generateWithRequired(exteriorZone)
                        self.exteriorDoors.append(door)
                        self.interiors.append(interior)
                    elif buildingType == 'hq':
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
                    elif buildingType == 'clotheshop':
                        interior = DistributedTailorInteriorAI.DistributedTailorInteriorAI(self.air, block, exteriorZone)
                        interior.generateWithRequired(interiorZone)
                        door = DistributedDoorAI.DistributedDoorAI(self.air, block, interiorZone, 1)
                        door.generateWithRequired(exteriorZone)
                        self.exteriorDoors.append(door)
                        self.interiors.append(interior)
                    elif buildingType == 'gagshop':
                        interior = DistributedGagShopInteriorAI.DistributedGagShopInteriorAI(self.air, block, exteriorZone)
                        interior.generateWithRequired(interiorZone)
                        door = DistributedDoorAI.DistributedDoorAI(self.air, block, interiorZone, 4)
                        door.generateWithRequired(exteriorZone)
                        self.exteriorDoors.append(door)
                        self.interiors.append(interior)
                else:
                    if not buildingType in ["animbldg", "hq"]:
                        building = DistributedBuildingAI.DistributedBuildingAI(self.air, block, exteriorZone, zoneId, self.hood)
                        building.generateWithRequired(exteriorZone)
                        building.setState('toon')
                        self.buildings[zoneId].append(building)
            if not isSZ:
                self.buildingPlanners[zoneId] = BuildingSuitPlannerAI(zoneId, CIGlobals.BranchZone2StreetName[zoneId], self)

        del self.dnaFiles

    def createTreasurePlanner(self):
        spawnInfo = TreasureGlobals.treasureSpawns.get(self.zoneId)
        if not spawnInfo:
            return
        treasureType, healAmount, spawnPoints, spawnRate, maxTreasures = spawnInfo
        self.treasurePlanner = SZTreasurePlannerAI(self.air,
            self.zoneId, treasureType, healAmount, spawnPoints,
            spawnRate, maxTreasures)
        self.treasurePlanner.start()

    def shutdown(self):
        for obj in list(self.air.doId2do.values()):
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
