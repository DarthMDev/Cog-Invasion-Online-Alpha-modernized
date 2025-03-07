# Filename: DDTownLoader.py
# Created by:  blach (26Jul15)

from . import TownLoader
from . import DDStreet

from lib.coginvasion.globals import CIGlobals

class DDTownLoader(TownLoader.TownLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        TownLoader.TownLoader.__init__(self, hood, parentFSM, doneEvent)
        self.streetClass = DDStreet.DDStreet
        self.musicFile = 'phase_6/audio/bgm/DD_SZ.ogg'
        self.interiorMusicFile = 'phase_6/audio/bgm/DD_SZ_activity.ogg'
        self.townStorageDNAFile = 'phase_6/dna/storage_DD_town.pdna'

    def load(self, zoneId):
        TownLoader.TownLoader.load(self, zoneId)
        zone4File = str(self.branchZone)
        dnaFile = 'phase_6/dna/donalds_dock_' + zone4File + '.pdna'
        self.createHood(dnaFile)

    def enter(self, requestStatus):
        TownLoader.TownLoader.enter(self, requestStatus)
        self.hood.setWhiteFog()

    def exit(self):
        self.hood.setNoFog()
        TownLoader.TownLoader.exit(self)
