# Filename: CogBattleGlobals.py
# Created by:  blach (28Jul15)

from lib.coginvasion.globals.CIGlobals import *
from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.hood import ZoneUtil

MAX_TURRETS = 3

HoodId2HoodIndex = {
    BattleTTC: 0,
    TheBrrrgh: 1,
    DonaldsDreamland: 2,
    MinniesMelodyland: 3,
    DaisyGardens: 4,
    DonaldsDock: 5
}
HoodIndex2HoodName = {v: k for k, v in HoodId2HoodIndex.items()}
HoodIndex2HoodId = None
if HoodIndex2HoodId == None:
    HoodIndex2HoodId = {}
    for hoodName in HoodId2HoodIndex.keys():
        index = HoodId2HoodIndex[hoodName]
        zone = ZoneUtil.getZoneId(hoodName)
        HoodIndex2HoodId[index] = zone

hi2hi = HoodId2HoodIndex

HoodIndex2LevelRange = {
    hi2hi[BattleTTC]: list(range(1, 3 + 1)),
    hi2hi[TheBrrrgh]: list(range(5, 9 + 1)),
    hi2hi[DonaldsDreamland]: list(range(6, 9 + 1)),
    hi2hi[MinniesMelodyland]: range(2, 6 + 1),
    hi2hi[DaisyGardens]: range(2, 6 + 1),
    hi2hi[DonaldsDock]: range(2, 6 + 1)
}

HoodId2WantBattles = {
    BattleTTC: True,
    TheBrrrgh: True,
    DonaldsDreamland: False,
    MinniesMelodyland: False,
    DaisyGardens: False,
    DonaldsDock: False
}

HoodIndex2TotalCogs = {
    hi2hi[BattleTTC]: 45,
    hi2hi[TheBrrrgh]: 45,
    hi2hi[DonaldsDreamland]: 50,
    hi2hi[MinniesMelodyland]: 45,
    hi2hi[DaisyGardens]: 45,
    hi2hi[DonaldsDock]: 45
}

WaiterHoodIndex = hi2hi[TheBrrrgh]
SkeletonHoodIndex = 10
