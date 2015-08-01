# Filename: CogBattleGlobals.py
# Created by:  blach (28Jul15)

from lib.coginvasion.globals.CIGlobals import *
from lib.coginvasion.hood import ZoneUtil

HoodId2HoodIndex = {
    ToontownCentral: 0,
    TheBrrrgh: 1,
    DonaldsDreamland: 2,
    #MinniesMelodyland: 3,
    #DaisyGardens: 4,
    #DonaldsDock: 5
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
    hi2hi[ToontownCentral]: range(1, 3 + 1),
    hi2hi[TheBrrrgh]: range(5, 9 + 1),
    hi2hi[DonaldsDreamland]: range(6, 9 + 1),
    #hi2hi[MinniesMelodyland]: range(2, 6 + 1),
    #hi2hi[DaisyGardens]: range(2, 6 + 1),
    #hi2hi[DonaldsDock]: range(2, 6 + 1)
}

HoodIndex2TotalCogs = {
    hi2hi[ToontownCentral]: 40,
    hi2hi[TheBrrrgh]: 45,
    hi2hi[DonaldsDreamland]: 50,
    #hi2hi[MinniesMelodyland]: 45,
    #hi2hi[DaisyGardens]: 45,
    #hi2hi[DonaldsDock]: 45
}

WaiterHoodIndex = hi2hi[TheBrrrgh]
SkeletonHoodIndex = 10
