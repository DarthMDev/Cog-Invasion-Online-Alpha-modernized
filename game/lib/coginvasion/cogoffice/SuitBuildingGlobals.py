# Filename: SuitBuildingGlobals.py
# Created by:  blach (13Dec15)

from ElevatorConstants import *
from lib.coginvasion.globals import CIGlobals

VICTORY_RUN_TIME = ElevatorData[ELEVATOR_NORMAL]['openTime'] + TOON_VICTORY_EXIT_TIME
TO_TOON_BLDG_TIME = 8
VICTORY_SEQUENCE_TIME = VICTORY_RUN_TIME + TO_TOON_BLDG_TIME
CLEAR_OUT_TOON_BLDG_TIME = 4
TO_SUIT_BLDG_TIME = 8

SPAWN_TIME_RANGE = (300, 600)

# Range of guards per section.
GUARDS_PER_SECTION = 0
# Cog level range on the bottom floors.
LEVEL_RANGE = 1
# Cog level range on the top floor.
BOSS_LEVEL_RANGE = 2

buildingInfo = {
    CIGlobals.ToontownCentral:   {GUARDS_PER_SECTION: (0, 2),
                                  LEVEL_RANGE:        (1, 4),
                                  BOSS_LEVEL_RANGE:   (2, 4)},

    CIGlobals.DonaldsDock:       {GUARDS_PER_SECTION: (1, 3),
                                  LEVEL_RANGE:        (2, 6),
                                  BOSS_LEVEL_RANGE:   (3, 6)},

    CIGlobals.DaisyGardens:      {GUARDS_PER_SECTION: (2, 3),
                                  LEVEL_RANGE:        (2, 6),
                                  BOSS_LEVEL_RANGE:   (4, 6)},

    CIGlobals.MinniesMelodyland: {GUARDS_PER_SECTION: (2, 4),
                                  LEVEL_RANGE:        (3, 6),
                                  BOSS_LEVEL_RANGE:   (4, 6)},

    CIGlobals.TheBrrrgh:         {GUARDS_PER_SECTION: (3, 4),
                                  LEVEL_RANGE:        (6, 11),
                                  BOSS_LEVEL_RANGE:   (8, 11)},

    CIGlobals.DonaldsDreamland:  {GUARDS_PER_SECTION: (3, 4),
                                  LEVEL_RANGE:        (8, 11),
                                  BOSS_LEVEL_RANGE:   (8, 12)}
}

# The minimum and maximum number of cog buildings that can be present on each street.
buildingMinMax = {
    CIGlobals.SillyStreet: (0, 3),
    CIGlobals.PunchlinePlace: (0, 3),
    CIGlobals.LoopyLane: (0, 3),
    CIGlobals.BarnacleBoulevard: (1, 5),
    CIGlobals.SeaweedStreet: (1, 5),
    CIGlobals.LighthouseLane: (1, 5),
    CIGlobals.ElmStreet: (2, 6),
    CIGlobals.MapleStreet: (2, 6),
    CIGlobals.OakStreet: (2, 6),
    CIGlobals.AltoAvenue: (3, 7),
    CIGlobals.BaritoneBoulevard: (3, 7),
    CIGlobals.TenorTerrace: (3, 7),
    CIGlobals.WalrusWay: (5, 10),
    CIGlobals.SleetStreet: (5, 10),
    CIGlobals.PolarPlace: (5, 10),
    CIGlobals.LullabyLane: (6, 12),
    CIGlobals.PajamaPlace: (6, 12)
}

# The chance a cog building will be spawned each interval.
buildingChances = {
    CIGlobals.SillyStreet: 2.0,
    CIGlobals.LoopyLane: 2.0,
    CIGlobals.PunchlinePlace: 2.0,
    CIGlobals.BarnacleBoulevard: 75.0,
    CIGlobals.SeaweedStreet: 75.0,
    CIGlobals.LighthouseLane: 75.0,
    CIGlobals.ElmStreet: 90.0,
    CIGlobals.MapleStreet: 90.0,
    CIGlobals.OakStreet: 90.0,
    CIGlobals.AltoAvenue: 95.0,
    CIGlobals.BaritoneBoulevard: 95.0,
    CIGlobals.TenorTerrace: 95.0,
    CIGlobals.WalrusWay: 100.0,
    CIGlobals.SleetStreet: 100.0,
    CIGlobals.PolarPlace: 100.0,
    CIGlobals.LullabyLane: 100.0,
    CIGlobals.PajamaPlace: 100.0,
}
