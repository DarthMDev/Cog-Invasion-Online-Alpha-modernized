# Filename: DLHood.py
# Created by:  blach (24Jul15)

from direct.directnotify.DirectNotifyGlobal import directNotify

from ToonHood import ToonHood
from DLSafeZoneLoader import DLSafeZoneLoader
from DLTownLoader import DLTownLoader
from lib.coginvasion.globals import CIGlobals

class DLHood(ToonHood):
    notify = directNotify.newCategory("DLHood")

    def __init__(self, parentFSM, doneEvent, dnaStore, hoodId):
        ToonHood.__init__(self, parentFSM, doneEvent, dnaStore, hoodId)
        self.id = CIGlobals.DonaldsDreamland
        self.safeZoneLoader = DLSafeZoneLoader
        self.townLoader = DLTownLoader
        self.storageDNAFile = "phase_8/dna/storage_DL.pdna"
        self.skyFilename = "phase_8/models/props/DL_sky.bam"
        self.spookySkyFile = "phase_8/models/props/DL_sky.bam"
        self.titleColor = (0.443, 0.21, 1.0, 1.0)
        self.loaderDoneEvent = 'DLHood-loaderDone'

    def load(self):
        ToonHood.load(self)
        self.parentFSM.getStateNamed('DLHood').addChild(self.fsm)

    def unload(self):
        self.parentFSM.getStateNamed('DLHood').removeChild(self.fsm)
        ToonHood.unload(self)
