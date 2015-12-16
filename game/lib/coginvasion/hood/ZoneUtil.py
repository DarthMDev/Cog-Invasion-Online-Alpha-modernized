from lib.coginvasion.globals.CIGlobals import *

def isInInterior(zoneId):
    return int(str(zoneId)[1:]) >= 500 and int(str(zoneId)[1:]) <= 999

def getWhereName(zoneId):
    if str(zoneId)[-3:] == '000':
        return 'playground'
    elif int(str(zoneId)[1:]) < 400:
        return 'street'
    elif isInInterior(zoneId):
        return 'toonInterior'
    else:
        return 'street'

def getBranchZone(zoneId):
    branchZone = zoneId - zoneId % 100
    if zoneId % 1000 >= 500:
        branchZone -= 500
    return branchZone

def getLoaderName(zoneId):
    if str(getBranchZone(zoneId))[-3:] == '000':
        return 'safeZoneLoader'
    elif int(str(getBranchZone(zoneId))[1:]) >= 100 and int(str(getBranchZone(zoneId))[1:]) <= 300:
        return 'townLoader'
    else:
        return None

def isStreetInSameHood(zoneId):
    return str(zoneId)[0] == str(base.localAvatar.zoneId)[0]

def isStreet(zoneId):
    return getWhereName(zoneId) == 'street'

def getCanonicalBranchZone(zoneId):
    return getBranchZone(getCanonicalZoneId(zoneId))

def getCanonicalZoneId(zoneId):
    zoneId = zoneId % 2000
    if zoneId < 1000:
        zoneId = zoneId + ToontownCentralId
    else:
        zoneId = zoneId - 1000 + GoofySpeedwayId
    return zoneId

def getTrueZoneId(zoneId, currentZoneId):
    if zoneId > 20000:
        world = CogTropolis
    else:
        world = OToontown
    hoodId = getHoodId(zoneId, street = 1, world = world)
    offset = currentZoneId - currentZoneId % 2000
    if hoodId == ToontownCentral and game.process != 'client' or game.process == 'client' and hoodId == ToontownCentral and base.cr.playGame.getCurrentWorldName() == OToontown:
        return zoneId - ToontownCentralId + offset
    elif hoodId == GoofySpeedway:
        return zoneId - GoofySpeedwayId + offset + 1000
    return zoneId

def getHoodId(zoneId, street = 0, world = None):
    if world is None:
        world = base.cr.playGame.getCurrentWorldName()
    if street:
        if world == OToontown:
            if str(zoneId)[0] == '1' and len(str(zoneId)) == 4:
                return DonaldsDock
            elif str(zoneId)[:2] == '10' and len(str(zoneId)) == 5:
                return MinigameArea
            elif str(zoneId)[:2] == '12' and len(str(zoneId)) == 5:
                return CogTropolis
            elif str(zoneId)[0] == '2':
                return ToontownCentral
            elif str(zoneId)[0] == '3':
                return TheBrrrgh
            elif str(zoneId)[0] == '4':
                return MinniesMelodyland
            elif str(zoneId)[0] == '5':
                return DaisyGardens
            elif str(zoneId)[0] == '9':
                return DonaldsDreamland
        elif world == CogTropolis:
            if str(zoneId)[1] == '1':
                return DonaldsDock
            elif str(zoneId)[1] == '2':
                return CogTropCentral
            elif str(zoneId)[1] == '3':
                return TheBrrrgh
            elif str(zoneId)[1] == '4':
                return MinniesMelodyland
            elif str(zoneId)[1] == '5':
                return DaisyGardens
            elif str(zoneId)[1] == '9':
                return DonaldsDreamland
    else:
        if base.localAvatar.zoneId < DynamicZonesBegin:
            return World2ZoneId2Hood[world][zoneId]

def getZoneId(hoodId, world = None):
    if world is None:
        # If no world is specified, use the current world we are in.
        world = base.cr.playGame.getCurrentWorldName()
    if hoodId == CogTropCentral and world == OToontown:
        hoodId = ToontownCentral
    return World2Hood2ZoneId[world][hoodId]
