########################################
# Filename: DistributedGagBarrelAI.py
# Created by: DecodedLogic (12Mar16)
########################################

from DistributedRestockBarrelAI import DistributedRestockBarrelAI
from lib.coginvasion.gags.GagManager import GagManager
from lib.coginvasion.gags import GagGlobals

class DistributedGagBarrelAI(DistributedRestockBarrelAI):
    
    def __init__(self, gagId, air, loadoutOnly = False):
        DistributedRestockBarrelAI.__init__(self, air)
        self.gagId = gagId
        self.maxRestock = 20
        self.loadoutOnly = loadoutOnly
        self.gagManager = GagManager()
        
    def announceGenerate(self):
        DistributedRestockBarrelAI.announceGenerate(self)
        self.sendUpdate('setLabel', [self.gagId + 2])
        
    def delete(self):
        DistributedRestockBarrelAI.delete(self)
        del self.gagId
        del self.maxRestock
        del self.loadoutOnly
        del self.gagManager
        
    def d_setGrab(self, avId):
        self.sendUpdate('setGrab', [avId])
        avatar = self.air.doId2do.get(avId)
        backpack = avatar.backpack
        track = backpack.getGagByID(self.gagId).getType()
        availableGags = []
        restockGags = {}
        
        if not self.loadoutOnly:
            trackGags = GagGlobals.TrackGagNamesByTrackName.get(GagGlobals.TrackNameById.get(GagGlobals.Type2TrackName.get(track)))
            
            # Get the gagids of gags in this gag track.
            for trackGag in trackGags:
                gagId = GagGlobals.getIDByName(trackGag)
                bpGag = backpack.getGagByID(gagId)
                
                if bpGag:
                    availableGags.append(gagId)
            # The strongest gags should be first.
            availableGags.reverse()
        else:
            trackGags = list()
            loadout = backpack.getLoadout()
            for gagCls in loadout:
                gagId = GagGlobals.getIDByName(self.gagManager.getGagNameByType(gagCls))
                gag = backpack.getGagByID(gagId)
                print gag.getName()
                if gag.getType() == track:
                    trackGags.append(gag.getID())
            availableGags = trackGags
        
        restockLeft = self.maxRestock
        
        for gagId in availableGags:
            if restockLeft <= 0:
                break
            maxAmount = backpack.getMaxSupply(gagId)
            
            if backpack.getSupply(gagId) < maxAmount:
                giveAmount = maxAmount - backpack.getSupply(gagId)
                if restockLeft < giveAmount:
                    giveAmount = restockLeft
                restockGags[gagId] = giveAmount
                restockLeft -= giveAmount
                print 'Restocking %s.' % (backpack.getGagByID(gagId).getName())
                
        for gagId in restockGags.keys():
            avatar.b_setGagAmmo(gagId, restockGags.get(gagId))