from lib.coginvasion.globals.CIGlobals import *

def isInInterior(zoneId):
	return int(str(zoneId)[1:]) >= 500 and int(str(zoneId)[1:]) <= 999

def getWhereName(zoneId):
	if int(str(zoneId)[1]) == 0:
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
    hoodId = getHoodId(zoneId)
    offset = currentZoneId - currentZoneId % 2000
    if hoodId == ToontownCentral:
        return zoneId - ToontownCentralId + offset
    elif hoodId == GoofySpeedway:
        return zoneId - GoofySpeedwayId + offset + 1000
    return zoneId

def getHoodId(zoneId, street = 0):
	if street:
		if str(zoneId)[0] == '1' and len(str(zoneId)) == 4:
			return DonaldsDock
		elif str(zoneId)[0] == '1' and len(str(zoneId)) == 5:
			return MinigameArea
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
	else:
		if zoneId == ToontownCentralId:
			return ToontownCentral
		elif zoneId == MinigameAreaId:
			return MinigameArea
		elif zoneId == RecoverAreaId:
			return RecoverArea
		elif zoneId == TheBrrrghId:
			return TheBrrrgh
		elif zoneId == DonaldsDreamlandId:
			return DonaldsDreamland
		elif zoneId == MinniesMelodylandId:
			return MinniesMelodyland
		elif zoneId == DaisyGardensId:
			return DaisyGardens
		elif zoneId == DonaldsDockId:
			return DonaldsDock

def getZoneId(hoodId):
	if hoodId == ToontownCentral:
		return ToontownCentralId
	elif hoodId == MinigameArea:
		return MinigameAreaId
	elif hoodId == RecoverArea:
		return RecoverAreaId
	elif hoodId == TheBrrrgh:
		return TheBrrrghId
	elif hoodId == DonaldsDreamland:
		return DonaldsDreamlandId
	elif hoodId == MinniesMelodyland:
		return MinniesMelodylandId
	elif hoodId == DaisyGardens:
		return DaisyGardensId
	elif hoodId == DonaldsDock:
		return DonaldsDockId
