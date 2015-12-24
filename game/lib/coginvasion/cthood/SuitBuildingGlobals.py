# Filename: SuitBuildingGlobals.py
# Created by:  blach (13Dec15)

from ElevatorConstants import *
from lib.coginvasion.globals import CIGlobals

VICTORY_RUN_TIME = ElevatorData[ELEVATOR_NORMAL]['openTime'] + TOON_VICTORY_EXIT_TIME
TO_TOON_BLDG_TIME = 8
VICTORY_SEQUENCE_TIME = VICTORY_RUN_TIME + TO_TOON_BLDG_TIME
CLEAR_OUT_TOON_BLDG_TIME = 4
TO_SUIT_BLDG_TIME = 8

SWITCH_BACK_TO_SUIT_TIME = (1000, 2500)

buildingMinMax = {
    CIGlobals.WallStreet: (1, 4),
    CIGlobals.ProprietaryPlace: (1, 4),
    CIGlobals.LimitedLiabilityLane: (1, 4),
    CIGlobals.BarnacleBoulevard: (2, 6),
    CIGlobals.SeaweedStreet: (2, 6),
    CIGlobals.LighthouseLane: (2, 6),
    CIGlobals.ElmStreet: (3, 7),
    CIGlobals.MapleStreet: (3, 7),
    CIGlobals.OakStreet: (3, 7),
    CIGlobals.AltoAvenue: (4, 8),
    CIGlobals.BaritoneBoulevard: (4, 8),
    CIGlobals.TenorTerrace: (4, 8),
    CIGlobals.WalrusWay: (6, 11),
    CIGlobals.SleetStreet: (6, 11),
    CIGlobals.PolarPlace: (6, 11),
    CIGlobals.LullabyLane: (7, 13),
    CIGlobals.PajamaPlace: (7, 13)
}
